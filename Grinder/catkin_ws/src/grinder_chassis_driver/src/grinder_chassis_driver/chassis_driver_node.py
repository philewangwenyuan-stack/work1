#!/usr/bin/env python3

import os
import threading
import time
import math

import rospy
from actionlib_msgs.msg import GoalID
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from slamware_ros_sdk.msg import PoseQuality, RelocalizationStatus, SystemStatus
from std_msgs.msg import Bool, Int16, UInt16
from std_srvs.srv import SetBool, SetBoolResponse, Trigger, TriggerResponse

from grinder_chassis_driver.msg import (
    ChassisStatus,
    LocalizationWatchdogStatus,
    WheelSpeedCommand,
    WheelSpeedState,
)
from grinder_chassis_driver.srv import (
    ClearFault,
    ClearFaultResponse,
    EnableChassis,
    EnableChassisResponse,
)
from grinder_chassis_driver.modbus_transport import ModbusTransport, ModbusTransportError
from grinder_chassis_driver.register_map import (
    DISC_ENABLE_OFF,
    DISC_ENABLE_ON,
    DISC_LIFT_DOWN,
    DISC_LIFT_UP,
    INT16_MAX,
    INT16_MIN,
    LIGHT_OFF,
    LIGHT_ON,
    READ_BLOCK_COUNT,
    READ_BLOCK_START,
    REGISTER_DISC_ENABLE,
    REGISTER_DISC_LIFT,
    REGISTER_DISC_SPEED,
    REGISTER_LEFT_WHEEL_SPEED,
    REGISTER_LIGHT,
    REGISTER_RIGHT_WHEEL_SPEED,
    REGISTER_WORK_MODE,
    WORK_MODE_MANUAL,
    ChassisCommand,
    RegisterSnapshot,
    clamp,
)


LOCALIZATION_BLOCKING_SYSTEM_STATUSES = frozenset(
    (
        "DeviceInitFailed",
        "DeviceTrackingLost",
    )
)
LOCALIZATION_RECOVERED_SYSTEM_STATUSES = frozenset(
    (
        "DeviceInited",
        "DeviceRunning",
        "DeviceLoopClosure",
        "DeviceOptimizationCompleted",
    )
)
LOCALIZATION_BLOCKING_RELOCALIZATION_STATUSES = frozenset(
    (
        "RelocalizationRunning",
        "RelocalizationFailed",
    )
)
LOCALIZATION_RECOVERED_RELOCALIZATION_STATUSES = frozenset(
    (
        "RelocalizationNone",
        "RelocalizationSucceed",
        "RelocalizationCanceled",
    )
)


def _get_bool_param(name, default):
    value = rospy.get_param(name, default)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


class ChassisDriverNode:
    def __init__(self):
        self._lock = threading.Lock()
        self.command = ChassisCommand()
        self.snapshot = RegisterSnapshot()
        self.enabled = True
        self.connected = False
        self.last_error = ""
        self.consecutive_failures = 0
        self.last_command_time = rospy.Time.now()
        self.last_sent_left_wheel_speed = 0
        self.last_sent_right_wheel_speed = 0
        self.last_sent_disc_speed = 0
        self.echo_failure_count = 0
        self._last_written_block = None
        self._last_written_registers = {}
        self._last_safe_stop_on_error_time = 0.0

        self.port = rospy.get_param("~port", "/dev/ttyS0")
        self.baudrate = rospy.get_param("~baudrate", 115200)
        self.slave_id = rospy.get_param("~slave_id", 1)
        self.timeout = rospy.get_param("~timeout", 0.1)
        self.poll_rate_hz = rospy.get_param("~poll_rate_hz", 20.0)
        self.command_timeout = rospy.get_param("~command_timeout", 0.5)
        self.write_verify = rospy.get_param("~write_verify", False)
        self.max_retries = rospy.get_param("~max_retries", 3)
        self.stop_on_timeout = rospy.get_param("~stop_on_timeout", True)
        self.startup_zero_output = rospy.get_param("~startup_zero_output", True)
        self.left_speed_min = rospy.get_param("~left_speed_min", INT16_MIN)
        self.left_speed_max = rospy.get_param("~left_speed_max", INT16_MAX)
        self.right_speed_min = rospy.get_param("~right_speed_min", INT16_MIN)
        self.right_speed_max = rospy.get_param("~right_speed_max", INT16_MAX)
        self.disc_speed_min = rospy.get_param("~disc_speed_min", INT16_MIN)
        self.disc_speed_max = rospy.get_param("~disc_speed_max", INT16_MAX)
        self.disc_speed_max_step = int(rospy.get_param("~disc_speed_max_step", 200))
        self.enable_disc_speed_ramp_limit = bool(rospy.get_param("~enable_disc_speed_ramp_limit", True))
        self.max_cmd_step_rpm = int(rospy.get_param("~max_cmd_step_rpm", 50))
        self.enable_cmd_ramp_limit = bool(rospy.get_param("~enable_cmd_ramp_limit", True))
        self.max_echo_deviation = int(rospy.get_param("~max_echo_deviation", 200))
        self.max_echo_failures = int(rospy.get_param("~max_echo_failures", 2))
        self.safe_stop_on_error_interval = float(rospy.get_param("~safe_stop_on_error_interval", 1.0))
        self.enable_safe_stop_on_comm_error = bool(rospy.get_param("~enable_safe_stop_on_comm_error", True))
        self.rs485_raw_log_enabled = bool(rospy.get_param("~rs485_raw_log_enabled", False))
        self.rs485_raw_log_file = rospy.get_param("~rs485_raw_log_file", "temp/chassis_rs485_raw.log")
        if self.rs485_raw_log_enabled:
            base = str(self.rs485_raw_log_file or "temp/chassis_rs485_raw.log")
            root, ext = os.path.splitext(base)
            if not ext:
                ext = ".log"
            ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.rs485_raw_log_file = "{}_{}{}".format(root, ts, ext)
            rospy.loginfo("RS485 raw log file: %s", self.rs485_raw_log_file)
        self.cmd_vel_enabled = bool(rospy.get_param("~cmd_vel_enabled", True))
        self.cmd_vel_topic = rospy.get_param("~cmd_vel_topic", "/cmd_vel")
        self.task_enable = bool(rospy.get_param("~task_enable_default", False))
        self.cmd_vel_wheel_track_m = float(rospy.get_param("~cmd_vel_wheel_track_m", 0.5))
        self.cmd_vel_wheel_radius_m = float(rospy.get_param("~cmd_vel_wheel_radius_m", 0.1))
        self.cmd_vel_gear_ratio = float(rospy.get_param("~cmd_vel_gear_ratio", 60.0))
        self.cmd_vel_scale = float(rospy.get_param("~cmd_vel_scale", 1.0))
        self.cmd_vel_max_linear = float(rospy.get_param("~cmd_vel_max_linear", 0.6))
        self.cmd_vel_max_angular = float(rospy.get_param("~cmd_vel_max_angular", 1.5))
        self.cmd_vel_max_input_v = float(rospy.get_param("~cmd_vel_max_input_v", 0.083))
        self.cmd_vel_max_input_w = float(rospy.get_param("~cmd_vel_max_input_w", 0.15))
        self.cmd_vel_max_abs_wheel_rpm = float(rospy.get_param("~cmd_vel_max_abs_wheel_rpm", 1500.0))
        self.cmd_vel_deadband_linear = float(rospy.get_param("~cmd_vel_deadband_linear", 0.0))
        self.cmd_vel_deadband_angular = float(rospy.get_param("~cmd_vel_deadband_angular", 0.0))
        self.cmd_source_hold_sec = float(rospy.get_param("~cmd_source_hold_sec", 0.2))
        #=================================================================================================================
        self.cmd_vel_filter_enabled = bool(rospy.get_param("~cmd_vel_filter_enabled", True))
        self.cmd_vel_filter_linear_accel = float(rospy.get_param("~cmd_vel_filter_linear_accel", 0.20))
        self.cmd_vel_filter_angular_accel = float(rospy.get_param("~cmd_vel_filter_angular_accel", 0.20))
        self.cmd_vel_filter_angular_deadband = float(rospy.get_param("~cmd_vel_filter_angular_deadband", 0.02))
        self.cmd_vel_filter_sign_confirm_count = int(rospy.get_param("~cmd_vel_filter_sign_confirm_count", 2))

        self._last_filtered_linear = 0.0
        self._last_filtered_angular = 0.0
        self._last_cmd_filter_time = time.monotonic()
        self._pending_angular_sign = 0
        self._pending_angular_sign_count = 0
        #=================================================================================================================
        # Manual wheel-speed input anti-jitter around zero crossing.
        self.manual_wheel_deadband_rpm = int(rospy.get_param("~manual_wheel_deadband_rpm", 0))
        self.manual_wheel_hyst_enter_rpm = int(rospy.get_param("~manual_wheel_hyst_enter_rpm", 0))
        self.manual_wheel_hyst_exit_rpm = int(rospy.get_param("~manual_wheel_hyst_exit_rpm", 0))
        if self.manual_wheel_hyst_enter_rpm < self.manual_wheel_hyst_exit_rpm:
            self.manual_wheel_hyst_enter_rpm = self.manual_wheel_hyst_exit_rpm
        self._manual_last_left_input = 0
        self._manual_last_right_input = 0
        self.manual_override_enabled = _get_bool_param("~manual_override_enabled", True)
        self.manual_override_topic = rospy.get_param("~manual_override_topic", "/chassis/manual_override")
        self.manual_override_service = rospy.get_param("~manual_override_service", "/chassis/set_manual_override")
        self.manual_override_cancel_navigation = _get_bool_param("~manual_override_cancel_navigation", False)
        self.manual_override_bypass_localization_watchdog = _get_bool_param(
            "~manual_override_bypass_localization_watchdog",
            True,
        )
        self._manual_override_active = False
        # Direction correction:
        # default to +1/+1 (no inversion), and leave fine-tuning to YAML params.
        self.drive_left_sign = -1 if int(rospy.get_param("~drive_left_sign", 1)) < 0 else 1
        self.drive_right_sign = -1 if int(rospy.get_param("~drive_right_sign", 1)) < 0 else 1
        self.drive_swap_lr = bool(rospy.get_param("~drive_swap_lr", False))
        self.cmd_vel_drive_left_sign = -1 if int(rospy.get_param("~cmd_vel_drive_left_sign", 1)) < 0 else 1
        self.cmd_vel_drive_right_sign = -1 if int(rospy.get_param("~cmd_vel_drive_right_sign", 1)) < 0 else 1
        self.cmd_vel_drive_swap_lr = bool(rospy.get_param("~cmd_vel_drive_swap_lr", False))
        self._last_cmd_vel_recv_monotonic = 0.0
        self.localization_watchdog_enabled = _get_bool_param("~localization_watchdog_enabled", True)
        self.localization_system_status_topic = rospy.get_param(
            "~localization_system_status_topic",
            "/slamware_ros_sdk_server_node/system_status",
        )
        self.localization_relocalization_status_topic = rospy.get_param(
            "~localization_relocalization_status_topic",
            "/slamware_ros_sdk_server_node/relocalization_status",
        )
        self.localization_pose_quality_topic = rospy.get_param(
            "~localization_pose_quality_topic",
            "/slamware_ros_sdk_server_node/pose_quality",
        )
        self.localization_pose_quality_timeout_sec = float(
            rospy.get_param("~localization_pose_quality_timeout_sec", 1.0)
        )
        self.localization_pose_quality_block_unknown = _get_bool_param(
            "~localization_pose_quality_block_unknown",
            True,
        )
        self.localization_pose_quality_warn_glide = _get_bool_param(
            "~localization_pose_quality_warn_glide",
            True,
        )
        self.localization_watchdog_use_system_status = _get_bool_param(
            "~localization_watchdog_use_system_status",
            False,
        )
        self.localization_watchdog_use_relocalization_status = _get_bool_param(
            "~localization_watchdog_use_relocalization_status",
            False,
        )
        self.localization_status_timeout_sec = float(rospy.get_param("~localization_status_timeout_sec", 1.0))
        self.localization_watchdog_cancel_topic = rospy.get_param(
            "~localization_watchdog_cancel_topic",
            "/move_base/cancel",
        )
        self.localization_watchdog_cancel_period_sec = float(
            rospy.get_param("~localization_watchdog_cancel_period_sec", 1.0)
        )
        self.localization_watchdog_auto_release = _get_bool_param("~localization_watchdog_auto_release", True)
        self.localization_watchdog_release_service = rospy.get_param(
            "~localization_watchdog_release_service",
            "/chassis/localization_watchdog_release",
        )
        self.localization_watchdog_restore_motion_on_release = _get_bool_param(
            "~localization_watchdog_restore_motion_on_release",
            False,
        )
        self.localization_watchdog_restore_disc_on_release = _get_bool_param(
            "~localization_watchdog_restore_disc_on_release",
            False,
        )
        self.localization_watchdog_stop_disc_on_lock = _get_bool_param(
            "~localization_watchdog_stop_disc_on_lock",
            False,
        )
        self.localization_watchdog_disc_speed_scale = float(
            rospy.get_param("~localization_watchdog_disc_speed_scale", 0.5)
        )
        self.localization_watchdog_disc_speed_scale = max(
            0.0,
            min(1.0, self.localization_watchdog_disc_speed_scale),
        )
        self.localization_watchdog_status_topic = rospy.get_param(
            "~localization_watchdog_status_topic",
            "/chassis/localization_watchdog_status",
        )
        self.localization_recovery_glide_enabled = _get_bool_param(
            "~localization_recovery_glide_enabled",
            True,
        )
        self.localization_watchdog_stop_disc_when_not_gliding = _get_bool_param(
            "~localization_watchdog_stop_disc_when_not_gliding",
            True,
        )
        self.localization_recovery_glide_speed_mps = float(
            rospy.get_param("~localization_recovery_glide_speed_mps", 0.05)
        )
        self.localization_recovery_max_distance_m = float(
            rospy.get_param("~localization_recovery_max_distance_m", 0.30)
        )
        self.localization_recovery_max_duration_sec = float(
            rospy.get_param("~localization_recovery_max_duration_sec", 10.0)
        )
        self.localization_recovery_scan_topic = rospy.get_param(
            "~localization_recovery_scan_topic",
            "/slamware_ros_sdk_server_node/scan",
        )
        self.localization_recovery_scan_timeout_sec = float(
            rospy.get_param("~localization_recovery_scan_timeout_sec", 0.5)
        )
        self.localization_recovery_front_sector_deg = float(
            rospy.get_param("~localization_recovery_front_sector_deg", 45.0)
        )
        self.localization_recovery_obstacle_stop_m = float(
            rospy.get_param("~localization_recovery_obstacle_stop_m", 0.40)
        )
        now_mono = time.monotonic()
        self._localization_system_status = ""
        self._localization_relocalization_status = ""
        self._localization_pose_quality_state = ""
        self._localization_pose_quality_reason = ""
        self._localization_pose_quality_time = now_mono - max(0.0, self.localization_pose_quality_timeout_sec) - 0.001
        self._localization_system_status_time = now_mono - max(0.0, self.localization_status_timeout_sec) - 0.001
        self._localization_watchdog_locked = False
        self._localization_watchdog_reason = ""
        self._localization_watchdog_waiting_manual_release = False
        self._localization_watchdog_saved_command = None
        self._last_localization_watchdog_stop_time = 0.0
        self._last_localization_watchdog_cancel_time = 0.0
        self._recovery_glide_active = False
        self._recovery_glide_start_time = 0.0
        self._recovery_glide_distance_m = 0.0
        self._recovery_glide_last_update_time = 0.0
        self._recovery_glide_stop_reason = ""
        self._front_obstacle_distance_m = float("inf")
        self._last_scan_time = 0.0

        self.transport = ModbusTransport(
            port=self.port,
            slave_id=self.slave_id,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_verify=self.write_verify,
            raw_log_enabled=self.rs485_raw_log_enabled,
            raw_log_file=self.rs485_raw_log_file,
        )

        self.wheel_speed_pub = rospy.Publisher("/chassis/wheel_speed_state", WheelSpeedState, queue_size=10)
        self.status_pub = rospy.Publisher("/chassis/status", ChassisStatus, queue_size=10)
        self.diagnostics_pub = rospy.Publisher("/diagnostics", DiagnosticArray, queue_size=10)
        self.localization_watchdog_status_pub = rospy.Publisher(
            self.localization_watchdog_status_topic,
            LocalizationWatchdogStatus,
            queue_size=10,
        )
        self.localization_cancel_pub = None
        if self.localization_watchdog_enabled or (
            self.manual_override_enabled and self.manual_override_cancel_navigation
        ):
            self.localization_cancel_pub = rospy.Publisher(
                self.localization_watchdog_cancel_topic,
                GoalID,
                queue_size=1,
            )

        rospy.Subscriber("/chassis/wheel_speed_cmd", WheelSpeedCommand, self._handle_wheel_speed_cmd, queue_size=10)
        if self.cmd_vel_enabled:
            rospy.Subscriber(self.cmd_vel_topic, Twist, self._handle_cmd_vel, queue_size=10)
            rospy.Subscriber("/chassis/task_enable", Bool, self._handle_task_enable_cmd, queue_size=10)
        rospy.Subscriber("/chassis/disc_speed_cmd", Int16, self._handle_disc_speed_cmd, queue_size=10)
        rospy.Subscriber("/chassis/disc_enable_cmd", Bool, self._handle_disc_enable_cmd, queue_size=10)
        rospy.Subscriber("/chassis/work_mode_cmd", UInt16, self._handle_work_mode_cmd, queue_size=10)
        rospy.Subscriber("/chassis/disc_lift_cmd", UInt16, self._handle_disc_lift_cmd, queue_size=10)
        rospy.Subscriber("/chassis/light_cmd", Bool, self._handle_light_cmd, queue_size=10)
        if self.manual_override_enabled:
            rospy.Subscriber(self.manual_override_topic, Bool, self._handle_manual_override_cmd, queue_size=10)
        if self.localization_watchdog_enabled:
            rospy.Subscriber(
                self.localization_system_status_topic,
                SystemStatus,
                self._handle_localization_system_status,
                queue_size=10,
            )
            rospy.Subscriber(
                self.localization_relocalization_status_topic,
                RelocalizationStatus,
                self._handle_localization_relocalization_status,
                queue_size=10,
            )
            rospy.Subscriber(
                self.localization_pose_quality_topic,
                PoseQuality,
                self._handle_pose_quality,
                queue_size=10,
            )
            rospy.Subscriber(
                self.localization_recovery_scan_topic,
                LaserScan,
                self._handle_recovery_scan,
                queue_size=10,
            )

        rospy.Service("/chassis/enable", EnableChassis, self._handle_enable_service)
        rospy.Service("/chassis/clear_fault", ClearFault, self._handle_clear_fault_service)
        if self.localization_watchdog_enabled:
            rospy.Service(
                self.localization_watchdog_release_service,
                Trigger,
                self._handle_localization_watchdog_release,
            )
        if self.manual_override_enabled:
            rospy.Service(self.manual_override_service, SetBool, self._handle_manual_override_service)

        if self.startup_zero_output:
            self._apply_startup_safe_state()

        self.timer = rospy.Timer(rospy.Duration.from_sec(1.0 / max(self.poll_rate_hz, 1.0)), self._poll_once)
        rospy.on_shutdown(self._on_shutdown)

    def _apply_startup_safe_state(self):
        with self._lock:
            self.command.left_wheel_speed = 0
            self.command.right_wheel_speed = 0
            self.command.disc_speed = 0
            self.command.disc_enable = DISC_ENABLE_OFF
            self.command.light = LIGHT_OFF
        try:
            self._write_all_outputs()
        except ModbusTransportError as exc:
            rospy.logwarn("Failed to send startup safe state: %s", exc)

    def _handle_localization_system_status(self, msg):
        status = str(msg.status)
        with self._lock:
            self._localization_system_status = status
            self._localization_system_status_time = time.monotonic()
        self._refresh_localization_watchdog("system_status={}".format(status))

    def _handle_localization_relocalization_status(self, msg):
        status = str(msg.status)
        with self._lock:
            self._localization_relocalization_status = status
        self._refresh_localization_watchdog("relocalization_status={}".format(status))

    def _handle_pose_quality(self, msg):
        state = str(getattr(msg, "state_label", "") or "").strip().upper()
        if not state:
            state = {
                getattr(PoseQuality, "STATE_OK", 1): "OK",
                getattr(PoseQuality, "STATE_WARN", 2): "WARN",
                getattr(PoseQuality, "STATE_FAULT", 3): "FAULT",
                getattr(PoseQuality, "STATE_UNKNOWN", 0): "UNKNOWN",
            }.get(int(getattr(msg, "state", 0)), "UNKNOWN")
        reason = str(getattr(msg, "reason", "") or "")
        with self._lock:
            self._localization_pose_quality_state = state
            self._localization_pose_quality_reason = reason
            self._localization_pose_quality_time = time.monotonic()
        self._refresh_localization_watchdog("pose_quality={}:{}".format(state, reason))

    def _handle_recovery_scan(self, msg):
        min_front = self._front_scan_min_distance(msg)
        with self._lock:
            self._front_obstacle_distance_m = min_front
            self._last_scan_time = time.monotonic()

    def _front_scan_min_distance(self, msg):
        half_sector = math.radians(max(1.0, float(self.localization_recovery_front_sector_deg)) * 0.5)
        best = float("inf")
        angle = float(msg.angle_min)
        increment = float(msg.angle_increment)
        if not math.isfinite(increment) or abs(increment) <= 1e-9:
            return best
        for value in msg.ranges:
            if -half_sector <= angle <= half_sector:
                distance = float(value)
                if math.isfinite(distance):
                    min_range = float(msg.range_min or 0.0)
                    max_range = float(msg.range_max or 0.0)
                    if distance >= min_range and (max_range <= 0.0 or distance <= max_range):
                        best = min(best, distance)
            angle += increment
        return best

    def _get_localization_watchdog_state(self, now):
        reasons = []
        with self._lock:
            system_status = self._localization_system_status
            relocalization_status = self._localization_relocalization_status
            pose_quality_state = self._localization_pose_quality_state
            pose_quality_reason = self._localization_pose_quality_reason
            pose_quality_age = now - self._localization_pose_quality_time
            system_status_age = now - self._localization_system_status_time

        if self.localization_watchdog_use_system_status:
            if system_status in LOCALIZATION_BLOCKING_SYSTEM_STATUSES:
                reasons.append("system_status={}".format(system_status))
            elif system_status in LOCALIZATION_RECOVERED_SYSTEM_STATUSES:
                pass

            timeout_sec = float(self.localization_status_timeout_sec)
            if timeout_sec > 0.0 and system_status_age > timeout_sec:
                if system_status:
                    reasons.append("system_status timeout %.2fs (%s)" % (system_status_age, system_status))
                else:
                    reasons.append("system_status timeout %.2fs" % system_status_age)

        if self.localization_watchdog_use_relocalization_status:
            if relocalization_status in LOCALIZATION_BLOCKING_RELOCALIZATION_STATUSES:
                reasons.append("relocalization_status={}".format(relocalization_status))
            elif relocalization_status in LOCALIZATION_RECOVERED_RELOCALIZATION_STATUSES:
                pass

        timeout_sec = float(self.localization_pose_quality_timeout_sec)
        if timeout_sec > 0.0 and pose_quality_age > timeout_sec:
            if pose_quality_state:
                reasons.append("pose_quality timeout %.2fs (%s)" % (pose_quality_age, pose_quality_state))
            else:
                reasons.append("pose_quality timeout %.2fs" % pose_quality_age)

        if pose_quality_state == "FAULT":
            reasons.append("pose_quality=FAULT:{}".format(pose_quality_reason))
        elif pose_quality_state == "WARN" and self.localization_pose_quality_warn_glide:
            reasons.append("pose_quality=WARN:{}".format(pose_quality_reason))
        elif pose_quality_state == "UNKNOWN" and self.localization_pose_quality_block_unknown:
            reasons.append("pose_quality=UNKNOWN:{}".format(pose_quality_reason))

        return bool(reasons), "; ".join(reasons)

    def _refresh_localization_watchdog(self, source=""):
        if not self.localization_watchdog_enabled:
            return False

        now = time.monotonic()
        unsafe, reason = self._get_localization_watchdog_state(now)
        release_now = False
        with self._lock:
            was_locked = self._localization_watchdog_locked
            was_waiting_manual = self._localization_watchdog_waiting_manual_release
            if unsafe:
                self._localization_watchdog_locked = True
                self._localization_watchdog_waiting_manual_release = False
                self._localization_watchdog_reason = reason
            elif was_locked and not self.localization_watchdog_auto_release:
                self._localization_watchdog_locked = True
                self._localization_watchdog_waiting_manual_release = True
                self._localization_watchdog_reason = "localization recovered; waiting for manual release"
            else:
                self._localization_watchdog_locked = False
                self._localization_watchdog_waiting_manual_release = False
                self._localization_watchdog_reason = ""
                release_now = was_locked

            locked = self._localization_watchdog_locked
            locked_reason = self._localization_watchdog_reason
            waiting_manual = self._localization_watchdog_waiting_manual_release
            newly_locked = locked and not was_locked
            newly_waiting_manual = waiting_manual and not was_waiting_manual

        manual_bypass = self._manual_override_bypasses_localization_watchdog()

        if locked:
            if newly_locked:
                self._save_localization_watchdog_restore_command()
                self._start_recovery_glide(now)
                rospy.logwarn("Localization watchdog locked: %s", locked_reason)
            elif newly_waiting_manual:
                rospy.logwarn("Localization recovered, but watchdog remains locked until manual release.")
            self._issue_localization_watchdog_stop(
                force=newly_locked,
                stop_motion=not manual_bypass,
                stop_disc=(not manual_bypass) and self.localization_watchdog_stop_disc_on_lock,
                reduce_disc=not manual_bypass,
            )
        elif release_now:
            self._reset_recovery_glide()
            self._restore_localization_watchdog_outputs()
            if source:
                rospy.loginfo("Localization watchdog released by %s", source)
            else:
                rospy.loginfo("Localization watchdog released")
        return locked

    def _localization_watchdog_blocks_commands(self, allow_manual_bypass=False):
        if not self.localization_watchdog_enabled:
            return False
        locked = self._refresh_localization_watchdog("command")
        if locked and allow_manual_bypass and self._manual_override_bypasses_localization_watchdog():
            return False
        return locked

    def _start_recovery_glide(self, now):
        with self._lock:
            self._recovery_glide_active = bool(self.localization_recovery_glide_enabled)
            self._recovery_glide_start_time = now
            self._recovery_glide_distance_m = 0.0
            self._recovery_glide_last_update_time = now
            self._recovery_glide_stop_reason = ""

    def _reset_recovery_glide(self):
        with self._lock:
            self._recovery_glide_active = False
            self._recovery_glide_start_time = 0.0
            self._recovery_glide_distance_m = 0.0
            self._recovery_glide_last_update_time = 0.0
            self._recovery_glide_stop_reason = ""

    def _linear_velocity_to_cmd_vel_wheels(self, linear_mps):
        if self.cmd_vel_wheel_radius_m <= 0.0 or self.cmd_vel_gear_ratio == 0.0:
            return 0, 0
        rpm_factor = 60.0 / (2.0 * math.pi * self.cmd_vel_wheel_radius_m)
        rpm = float(linear_mps) * rpm_factor * self.cmd_vel_gear_ratio * self.cmd_vel_scale
        max_abs_rpm = abs(float(self.cmd_vel_max_abs_wheel_rpm))
        if max_abs_rpm > 0.0:
            rpm = max(-max_abs_rpm, min(max_abs_rpm, rpm))
        left_cmd = int(round(rpm))
        right_cmd = int(round(rpm))
        return self._apply_drive_direction_cmd_vel(left_cmd, right_cmd)

    def _straight_glide_wheel_cmd(self):
        left_cmd, right_cmd = self._linear_velocity_to_cmd_vel_wheels(
            max(0.0, float(self.localization_recovery_glide_speed_mps))
        )
        magnitude = min(abs(int(left_cmd)), abs(int(right_cmd)))
        if magnitude <= 0:
            return 0, 0
        left_sign = -1 if int(left_cmd) < 0 else 1
        right_sign = -1 if int(right_cmd) < 0 else 1
        return left_sign * magnitude, right_sign * magnitude

    def _feedback_wheels_to_linear_mps(self, left_speed, right_speed):
        left = int(left_speed)
        right = int(right_speed)
        if self.cmd_vel_drive_swap_lr:
            left, right = right, left
        left = left * self.cmd_vel_drive_left_sign
        right = right * self.cmd_vel_drive_right_sign
        denom = self.cmd_vel_gear_ratio * self.cmd_vel_scale
        if self.cmd_vel_wheel_radius_m <= 0.0 or abs(denom) <= 1e-9:
            return 0.0
        wheel_rpm = (float(left) + float(right)) * 0.5 / denom
        return wheel_rpm * (2.0 * math.pi * self.cmd_vel_wheel_radius_m) / 60.0

    def _update_recovery_glide_distance(self, now):
        with self._lock:
            if not self._recovery_glide_active:
                self._recovery_glide_last_update_time = now
                return
            last = self._recovery_glide_last_update_time or now
            dt = max(0.0, min(0.5, now - last))
            self._recovery_glide_last_update_time = now
            snapshot = RegisterSnapshot(**self.snapshot.__dict__)
            connected = self.connected
        if dt <= 0.0:
            return
        if connected:
            speed = abs(self._feedback_wheels_to_linear_mps(
                snapshot.left_wheel_speed,
                snapshot.right_wheel_speed,
            ))
        else:
            speed = abs(float(self.localization_recovery_glide_speed_mps))
        with self._lock:
            self._recovery_glide_distance_m += speed * dt

    def _recovery_scan_is_clear(self, now):
        with self._lock:
            scan_age = now - self._last_scan_time if self._last_scan_time > 0.0 else float("inf")
            front_distance = self._front_obstacle_distance_m
        if scan_age > max(0.05, float(self.localization_recovery_scan_timeout_sec)):
            return False, "scan_timeout"
        if front_distance <= max(0.0, float(self.localization_recovery_obstacle_stop_m)):
            return False, "front_obstacle=%.3fm" % front_distance
        return True, ""

    def _can_recovery_glide(self, now):
        if not self.localization_recovery_glide_enabled:
            return False, "disabled"
        if not self.task_enable:
            return False, "task_disabled"
        if not self.enabled:
            return False, "chassis_disabled"
        with self._lock:
            waiting_manual_release = self._localization_watchdog_waiting_manual_release
            if not self._recovery_glide_active:
                return False, self._recovery_glide_stop_reason or "inactive"
        if waiting_manual_release:
            return False, "waiting_manual_release"
        self._update_recovery_glide_distance(now)
        with self._lock:
            distance = self._recovery_glide_distance_m
            start_time = self._recovery_glide_start_time
        max_distance = max(0.0, float(self.localization_recovery_max_distance_m))
        max_duration = max(0.0, float(self.localization_recovery_max_duration_sec))
        if max_distance <= 0.0 or distance >= max_distance:
            return False, "max_distance"
        if max_duration <= 0.0 or (start_time > 0.0 and (now - start_time) >= max_duration):
            return False, "max_duration"
        return self._recovery_scan_is_clear(now)

    def _issue_localization_watchdog_stop(self, force=False, stop_motion=True, stop_disc=True, reduce_disc=True):
        now = time.monotonic()
        period = max(0.1, float(self.localization_watchdog_cancel_period_sec))
        glide_allowed = False
        glide_stop_reason = ""
        if stop_motion:
            glide_allowed, glide_stop_reason = self._can_recovery_glide(now)
        left_glide, right_glide = self._straight_glide_wheel_cmd()
        with self._lock:
            if stop_motion:
                if glide_allowed:
                    self.command.left_wheel_speed = left_glide
                    self.command.right_wheel_speed = right_glide
                    self._recovery_glide_active = True
                    self._recovery_glide_stop_reason = ""
                else:
                    self.command.left_wheel_speed = 0
                    self.command.right_wheel_speed = 0
                    self._recovery_glide_active = False
                    self._recovery_glide_stop_reason = glide_stop_reason
            should_stop_disc = stop_disc or (
                reduce_disc
                and self.localization_watchdog_stop_disc_when_not_gliding
                and stop_motion
                and not glide_allowed
            )
            if should_stop_disc:
                self.command.disc_speed = 0
                self.command.disc_enable = DISC_ENABLE_OFF
            elif reduce_disc:
                saved_command = self._localization_watchdog_saved_command
                base_disc_speed = saved_command.disc_speed if saved_command is not None else self.command.disc_speed
                scaled_disc_speed = int(round(float(base_disc_speed) * self.localization_watchdog_disc_speed_scale))
                self.command.disc_speed = clamp(scaled_disc_speed, self.disc_speed_min, self.disc_speed_max)
                if saved_command is not None:
                    self.command.disc_enable = saved_command.disc_enable
            self.last_command_time = rospy.Time.now()
            write_due = force or (now - self._last_localization_watchdog_stop_time) >= period
            cancel_due = force or (now - self._last_localization_watchdog_cancel_time) >= period
            if write_due:
                self._last_localization_watchdog_stop_time = now
            if cancel_due:
                self._last_localization_watchdog_cancel_time = now

        self._reset_cmd_vel_filter()
        if write_due:
            try:
                self._write_all_outputs(force=True)
            except ModbusTransportError as exc:
                self._handle_transport_error(exc)
        if cancel_due:
            self._publish_localization_cancel()

    def _save_localization_watchdog_restore_command(self):
        with self._lock:
            self._localization_watchdog_saved_command = ChassisCommand(**self.command.__dict__)

    def _restore_localization_watchdog_outputs(self):
        with self._lock:
            saved_command = self._localization_watchdog_saved_command
            self._localization_watchdog_saved_command = None
            self._recovery_glide_active = False
            if saved_command is None:
                return

            if self.localization_watchdog_restore_motion_on_release:
                self.command.left_wheel_speed = saved_command.left_wheel_speed
                self.command.right_wheel_speed = saved_command.right_wheel_speed
            else:
                self.command.left_wheel_speed = 0
                self.command.right_wheel_speed = 0

            if self.localization_watchdog_restore_disc_on_release:
                self.command.disc_speed = saved_command.disc_speed
                self.command.disc_enable = saved_command.disc_enable

            self.last_command_time = rospy.Time.now()
            should_write = self.enabled and (
                self.localization_watchdog_restore_motion_on_release
                or self.localization_watchdog_restore_disc_on_release
            )

        if not should_write:
            rospy.loginfo("Localization watchdog released; outputs remain at watchdog-held values by restore config.")
            return

        try:
            self._write_all_outputs(force=True)
            rospy.loginfo(
                "Localization watchdog restored outputs: motion=%s disc=%s",
                str(self.localization_watchdog_restore_motion_on_release),
                str(self.localization_watchdog_restore_disc_on_release),
            )
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)

    def _handle_localization_watchdog_release(self, _request):
        if not self.localization_watchdog_enabled:
            return TriggerResponse(success=True, message="Localization watchdog is disabled.")

        unsafe, reason = self._get_localization_watchdog_state(time.monotonic())
        if unsafe:
            with self._lock:
                self._localization_watchdog_locked = True
                self._localization_watchdog_waiting_manual_release = False
                self._localization_watchdog_reason = reason
            self._issue_localization_watchdog_stop(force=True)
            return TriggerResponse(success=False, message="Localization is still unsafe: {}".format(reason))

        with self._lock:
            was_locked = self._localization_watchdog_locked
            self._localization_watchdog_locked = False
            self._localization_watchdog_waiting_manual_release = False
            self._localization_watchdog_reason = ""

        if was_locked:
            self._restore_localization_watchdog_outputs()
            return TriggerResponse(success=True, message="Localization watchdog released.")
        return TriggerResponse(success=True, message="Localization watchdog was already released.")

    def _publish_localization_cancel(self):
        if self.localization_cancel_pub is None:
            return
        self.localization_cancel_pub.publish(GoalID())

    def _handle_manual_override_cmd(self, msg):
        self._set_manual_override(bool(msg.data), "topic")

    def _handle_manual_override_service(self, request):
        enabled = bool(request.data)
        if not self.manual_override_enabled:
            return SetBoolResponse(success=False, message="Manual override is disabled.")
        self._set_manual_override(enabled, "service")
        return SetBoolResponse(success=True, message="Manual override set to {}".format(str(enabled)))

    def _manual_override_bypasses_localization_watchdog(self):
        return (
            self.manual_override_enabled
            and self._manual_override_active
            and self.manual_override_bypass_localization_watchdog
        )

    def _set_manual_override(self, enabled, source):
        if not self.manual_override_enabled:
            return
        enabled = bool(enabled)
        with self._lock:
            was_active = self._manual_override_active
            self._manual_override_active = enabled
            if enabled:
                self._last_cmd_vel_recv_monotonic = 0.0

        if enabled == was_active:
            return

        self._reset_cmd_vel_filter()
        if enabled:
            rospy.logwarn("Manual override enabled by %s; ignoring cmd_vel and allowing wheel_speed_cmd.", source)
            if self.manual_override_cancel_navigation:
                self._publish_localization_cancel()
            with self._lock:
                self.command.left_wheel_speed = 0
                self.command.right_wheel_speed = 0
                self.last_command_time = rospy.Time.now()
            if self.enabled:
                self._write_motion_registers()
        else:
            rospy.loginfo("Manual override disabled by %s; cmd_vel arbitration restored.", source)
            if self.localization_watchdog_enabled:
                self._refresh_localization_watchdog("manual_override_off")

    def _manual_override_blocks_cmd_vel(self):
        return self.manual_override_enabled and self._manual_override_active

    def _log_localization_watchdog_reject(self, source):
        with self._lock:
            reason = self._localization_watchdog_reason or "locked"
        rospy.logwarn_throttle(2.0, "Ignore %s while localization watchdog is locked: %s", source, reason)

    def _handle_wheel_speed_cmd(self, msg):
        manual_override = self._manual_override_blocks_cmd_vel()
        if self._localization_watchdog_blocks_commands(allow_manual_bypass=True):
            self._log_localization_watchdog_reject("/chassis/wheel_speed_cmd")
            return
        if self.cmd_vel_enabled and not manual_override:
            now_mono = time.monotonic()
            recent_cmd_vel = (now_mono - self._last_cmd_vel_recv_monotonic) <= max(0.0, self.cmd_source_hold_sec)
            if recent_cmd_vel:
                rospy.logwarn_throttle(
                    2.0,
                    "Ignore /chassis/wheel_speed_cmd because cmd_vel source is active (hold=%.3fs).",
                    self.cmd_source_hold_sec,
                )
                return
        req_left = clamp(msg.left_wheel_speed, self.left_speed_min, self.left_speed_max)
        req_right = clamp(msg.right_wheel_speed, self.right_speed_min, self.right_speed_max)
        req_left = self._filter_manual_wheel_input(req_left, self._manual_last_left_input)
        req_right = self._filter_manual_wheel_input(req_right, self._manual_last_right_input)
        self._manual_last_left_input = int(req_left)
        self._manual_last_right_input = int(req_right)
        mapped_left, mapped_right = self._apply_drive_direction(req_left, req_right)
        with self._lock:
            self.command.left_wheel_speed = mapped_left
            self.command.right_wheel_speed = mapped_right
            self.last_command_time = rospy.Time.now()
        if self.enabled:
            self._write_motion_registers()
    #=================================================================================================================
    def _cmd_vel_sign(self, value, deadband):
        if value > deadband:
            return 1
        if value < -deadband:
            return -1
        return 0

    def _rate_limit_value(self, target, last_value, max_rate, dt):
        max_step = max(0.0, float(max_rate)) * max(0.0, float(dt))
        delta = float(target) - float(last_value)
        if delta > max_step:
            return float(last_value) + max_step
        if delta < -max_step:
            return float(last_value) - max_step
        return float(target)

    def _reset_cmd_vel_filter(self):
        self._last_filtered_linear = 0.0
        self._last_filtered_angular = 0.0
        self._last_cmd_filter_time = time.monotonic()
        self._pending_angular_sign = 0
        self._pending_angular_sign_count = 0




    def _apply_cmd_vel_filter(self, linear, angular):
        if not self.cmd_vel_filter_enabled:
            self._last_filtered_linear = float(linear)
            self._last_filtered_angular = float(angular)
            self._last_cmd_filter_time = time.monotonic()
            return float(linear), float(angular)

        now = time.monotonic()
        dt = now - self._last_cmd_filter_time
        if dt <= 0.0:
            dt = 0.02
        dt = max(0.02, min(0.20, dt))

        angular_deadband = max(0.0, float(self.cmd_vel_filter_angular_deadband))
        if abs(angular) < angular_deadband:
            angular = 0.0

        requested_sign = self._cmd_vel_sign(angular, angular_deadband)
        last_sign = self._cmd_vel_sign(self._last_filtered_angular, angular_deadband)
        confirm_count = max(1, int(self.cmd_vel_filter_sign_confirm_count))

        if confirm_count > 1 and requested_sign != 0 and last_sign != 0 and requested_sign != last_sign:
            if requested_sign == self._pending_angular_sign:
                self._pending_angular_sign_count += 1
            else:
                self._pending_angular_sign = requested_sign
                self._pending_angular_sign_count = 1

            if self._pending_angular_sign_count < confirm_count:
                angular = 0.0
            else:
                self._pending_angular_sign = 0
                self._pending_angular_sign_count = 0
        else:
            self._pending_angular_sign = 0
            self._pending_angular_sign_count = 0

        linear = self._rate_limit_value(
            linear,
            self._last_filtered_linear,
            self.cmd_vel_filter_linear_accel,
            dt,
        )
        angular = self._rate_limit_value(
            angular,
            self._last_filtered_angular,
            self.cmd_vel_filter_angular_accel,
            dt,
        )

        if abs(angular) < angular_deadband:
            angular = 0.0

        self._last_filtered_linear = float(linear)
        self._last_filtered_angular = float(angular)
        self._last_cmd_filter_time = now

        return float(linear), float(angular)

    #=================================================================================================================

    def _handle_cmd_vel(self, msg):
        if self._manual_override_blocks_cmd_vel():
            self._reset_cmd_vel_filter()
            rospy.logwarn_throttle(2.0, "Ignore %s while manual override is active.", self.cmd_vel_topic)
            return
        if self._localization_watchdog_blocks_commands():
            self._log_localization_watchdog_reject(self.cmd_vel_topic)
            return
        # if not self.task_enable:
        #     return
        if not self.task_enable:
            self._reset_cmd_vel_filter()
            return
        self._last_cmd_vel_recv_monotonic = time.monotonic()
        if self.cmd_vel_wheel_radius_m <= 0.0 or self.cmd_vel_wheel_track_m <= 0.0:
            rospy.logwarn_throttle(
                2.0,
                "cmd_vel conversion disabled due to invalid geometry: wheel_radius=%.4f wheel_track=%.4f",
                self.cmd_vel_wheel_radius_m,
                self.cmd_vel_wheel_track_m,
            )
            return
        linear_limit = self.cmd_vel_max_linear
        angular_limit = self.cmd_vel_max_angular
        if self.cmd_vel_max_input_v > 0.0:
            linear_limit = min(linear_limit, self.cmd_vel_max_input_v)
        if self.cmd_vel_max_input_w > 0.0:
            angular_limit = min(angular_limit, self.cmd_vel_max_input_w)
        # linear = max(-linear_limit, min(linear_limit, float(msg.linear.x)))
        # angular = max(-angular_limit, min(angular_limit, float(msg.angular.z)))
        # if abs(linear) < max(0.0, self.cmd_vel_deadband_linear):
        #     linear = 0.0
        # if abs(angular) < max(0.0, self.cmd_vel_deadband_angular):
        #     angular = 0.0
        # left_mps = linear - angular * (self.cmd_vel_wheel_track_m * 0.5)

        #=============================================================================================================
        linear = max(-linear_limit, min(linear_limit, float(msg.linear.x)))
        angular = max(-angular_limit, min(angular_limit, float(msg.angular.z)))

        if abs(linear) < max(0.0, self.cmd_vel_deadband_linear):
            linear = 0.0
        if abs(angular) < max(0.0, self.cmd_vel_deadband_angular):
            angular = 0.0

        linear, angular = self._apply_cmd_vel_filter(linear, angular)

        left_mps = linear - angular * (self.cmd_vel_wheel_track_m * 0.5)
        #=================================================================================================================
        right_mps = linear + angular * (self.cmd_vel_wheel_track_m * 0.5)
        rpm_factor = 60.0 / (2.0 * math.pi * self.cmd_vel_wheel_radius_m)
        left_rpm = left_mps * rpm_factor * self.cmd_vel_gear_ratio * self.cmd_vel_scale
        right_rpm = right_mps * rpm_factor * self.cmd_vel_gear_ratio * self.cmd_vel_scale
        max_abs_rpm = abs(float(self.cmd_vel_max_abs_wheel_rpm))
        if max_abs_rpm > 0.0:
            left_rpm = max(-max_abs_rpm, min(max_abs_rpm, left_rpm))
            right_rpm = max(-max_abs_rpm, min(max_abs_rpm, right_rpm))
        left_cmd = int(round(left_rpm))
        right_cmd = int(round(right_rpm))
        mapped_left, mapped_right = self._apply_drive_direction_cmd_vel(left_cmd, right_cmd)
        with self._lock:
            self.command.left_wheel_speed = mapped_left
            self.command.right_wheel_speed = mapped_right
            self.last_command_time = rospy.Time.now()
        if self.enabled:
            self._write_motion_registers()

    def _handle_task_enable_cmd(self, msg):
        self.task_enable = bool(msg.data)
        rospy.loginfo("chassis task_enable updated: %s", str(self.task_enable))

    def _apply_drive_direction(self, left_speed, right_speed):
        left = int(left_speed)
        right = int(right_speed)
        if self.drive_swap_lr:
            left, right = right, left
        left = int(left * self.drive_left_sign)
        right = int(right * self.drive_right_sign)
        return (
            clamp(left, self.left_speed_min, self.left_speed_max),
            clamp(right, self.right_speed_min, self.right_speed_max),
        )

    def _filter_manual_wheel_input(self, value, prev_value):
        v = int(value)
        prev = int(prev_value)
        deadband = max(0, int(self.manual_wheel_deadband_rpm))
        enter_th = max(deadband, int(self.manual_wheel_hyst_enter_rpm))
        exit_th = max(deadband, int(self.manual_wheel_hyst_exit_rpm))
        # Hard deadband near zero.
        if abs(v) <= deadband:
            return 0
        # Hysteresis around zero crossing:
        # - from stop to move: require |v| >= enter_th
        # - from move to stop: require |v| <= exit_th
        if prev == 0:
            if abs(v) < enter_th:
                return 0
            return v
        if abs(v) <= exit_th:
            return 0
        return v

    def _apply_drive_direction_cmd_vel(self, left_speed, right_speed):
        left = int(left_speed)
        right = int(right_speed)
        if self.cmd_vel_drive_swap_lr:
            left, right = right, left
        left = int(left * self.cmd_vel_drive_left_sign)
        right = int(right * self.cmd_vel_drive_right_sign)
        return (
            clamp(left, self.left_speed_min, self.left_speed_max),
            clamp(right, self.right_speed_min, self.right_speed_max),
        )

    def _handle_disc_speed_cmd(self, msg):
        if self._localization_watchdog_blocks_commands(allow_manual_bypass=True):
            self._log_localization_watchdog_reject("/chassis/disc_speed_cmd")
            return
        with self._lock:
            self.command.disc_speed = clamp(msg.data, self.disc_speed_min, self.disc_speed_max)
        if self.enabled:
            self._write_disc_speed_step(force=True)

    def _handle_disc_enable_cmd(self, msg):
        if self._localization_watchdog_blocks_commands(allow_manual_bypass=True):
            self._log_localization_watchdog_reject("/chassis/disc_enable_cmd")
            return
        with self._lock:
            self.command.disc_enable = DISC_ENABLE_ON if msg.data else DISC_ENABLE_OFF
        if self.enabled:
            self._write_single_output(REGISTER_DISC_ENABLE, self.command.disc_enable, signed=False)

    def _handle_work_mode_cmd(self, msg):
        with self._lock:
            self.command.work_mode = msg.data
        if self.enabled:
            self._write_single_output(REGISTER_WORK_MODE, self.command.work_mode, signed=False)

    def _handle_disc_lift_cmd(self, msg):
        with self._lock:
            self.command.disc_lift = msg.data
        if self.enabled:
            self._write_single_output(REGISTER_DISC_LIFT, self.command.disc_lift, signed=False)

    def _handle_light_cmd(self, msg):
        with self._lock:
            self.command.light = LIGHT_ON if msg.data else LIGHT_OFF
        if self.enabled:
            self._write_single_output(REGISTER_LIGHT, self.command.light, signed=False)

    def _handle_enable_service(self, request):
        self.enabled = request.enable
        if not self.enabled:
            self._issue_safe_stop()
            return EnableChassisResponse(success=True, message="Chassis output disabled and motion stopped.")
        self.last_command_time = rospy.Time.now()
        try:
            self._write_all_outputs()
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)
            return EnableChassisResponse(success=False, message="Failed to re-enable outputs: {}".format(exc))
        return EnableChassisResponse(success=True, message="Chassis output enabled.")

    def _handle_clear_fault_service(self, _request):
        return ClearFaultResponse(
            success=False,
            message="Fault clear register is not defined yet. Provide the vendor register table to implement it.",
        )

    def _write_motion_registers(self):
        with self._lock:
            desired_left = self.command.left_wheel_speed if self.enabled else 0
            desired_right = self.command.right_wheel_speed if self.enabled else 0
            left_speed = self._apply_ramp_limit(desired_left, self.last_sent_left_wheel_speed)
            right_speed = self._apply_ramp_limit(desired_right, self.last_sent_right_wheel_speed)
            if (
                int(left_speed) == int(self.last_sent_left_wheel_speed)
                and int(right_speed) == int(self.last_sent_right_wheel_speed)
            ):
                return
        try:
            # Keep left/right wheel command atomic in one Modbus frame
            # to avoid transient "single wheel moves first" behavior.
            self.transport.write_register_block(
                REGISTER_LEFT_WHEEL_SPEED,
                [left_speed, right_speed],
            )
            with self._lock:
                self.last_sent_left_wheel_speed = left_speed
                self.last_sent_right_wheel_speed = right_speed
                self._last_written_registers[REGISTER_LEFT_WHEEL_SPEED] = int(left_speed)
                self._last_written_registers[REGISTER_RIGHT_WHEEL_SPEED] = int(right_speed)
            self._mark_connected()
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)

    def _write_single_output(self, register_address, value, signed):
        with self._lock:
            if register_address in self._last_written_registers and int(self._last_written_registers[register_address]) == int(value):
                return
        try:
            if signed:
                self.transport.write_int16(register_address, value)
            else:
                self.transport.write_uint16(register_address, value)
            with self._lock:
                self._last_written_registers[register_address] = int(value)
                if register_address == REGISTER_DISC_SPEED:
                    self.last_sent_disc_speed = int(value)
            self._mark_connected()
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)

    def _apply_disc_ramp_limit(self, target, last_value):
        if not self.enable_disc_speed_ramp_limit:
            return int(target)
        step = max(0, int(self.disc_speed_max_step))
        if step <= 0:
            return int(target)
        delta = int(target) - int(last_value)
        if delta > step:
            return int(last_value) + step
        if delta < -step:
            return int(last_value) - step
        return int(target)

    def _write_disc_speed_step(self, force=False):
        with self._lock:
            target = 0 if not self.enabled else clamp(self.command.disc_speed, self.disc_speed_min, self.disc_speed_max)
            disc_speed = self._apply_disc_ramp_limit(target, self.last_sent_disc_speed)
            if not force and int(disc_speed) == int(self.last_sent_disc_speed):
                return
        try:
            self.transport.write_int16(REGISTER_DISC_SPEED, disc_speed)
            with self._lock:
                self.last_sent_disc_speed = int(disc_speed)
                self._last_written_registers[REGISTER_DISC_SPEED] = int(disc_speed)
            self._mark_connected()
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)

    def _write_all_outputs(self, force=False):
        with self._lock:
            block = self.command.as_register_block()
            if not self.enabled:
                block[0] = 0
                block[1] = 0
                block[2] = 0
                block[3] = DISC_ENABLE_OFF
            target_disc_speed = 0 if not self.enabled else clamp(self.command.disc_speed, self.disc_speed_min, self.disc_speed_max)
            disc_speed = self._apply_disc_ramp_limit(target_disc_speed, self.last_sent_disc_speed)
            block[2] = disc_speed & 0xFFFF
            block_tuple = tuple(int(x) for x in block)
            if not force and self._last_written_block == block_tuple:
                return
        self.transport.write_register_block(READ_BLOCK_START, block)
        with self._lock:
            self._last_written_block = block_tuple
            self.last_sent_left_wheel_speed = int(block[0])
            self.last_sent_right_wheel_speed = int(block[1])
            self.last_sent_disc_speed = int(disc_speed)
            for index, value in enumerate(block):
                self._last_written_registers[READ_BLOCK_START + index] = int(value)
            self._last_written_registers[REGISTER_DISC_SPEED] = int(disc_speed)
        self._mark_connected()

    def _issue_safe_stop(self):
        with self._lock:
            self.command.left_wheel_speed = 0
            self.command.right_wheel_speed = 0
            self.command.disc_speed = 0
            self.command.disc_enable = DISC_ENABLE_OFF
        try:
            self._write_all_outputs()
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)

    def _poll_once(self, _event):
        self._refresh_localization_watchdog("timer")
        self._enforce_command_timeout()
        self._write_disc_speed_step()
        try:
            registers = self.transport.read_register_block(
                READ_BLOCK_START,
                READ_BLOCK_COUNT,
                signed_indices=(0, 1, 2),
            )
            with self._lock:
                self.snapshot = RegisterSnapshot.from_registers(registers)
                snapshot = RegisterSnapshot(**self.snapshot.__dict__)
            self._mark_connected()
            self._check_echo_deviation(snapshot)
        except ModbusTransportError as exc:
            self._handle_transport_error(exc)

        self._publish_state()
        self._publish_localization_watchdog_status()
        self._publish_diagnostics()

    def _enforce_command_timeout(self):
        if not self.stop_on_timeout or not self.enabled:
            return
        if (rospy.Time.now() - self.last_command_time).to_sec() <= self.command_timeout:
            return
        with self._lock:
            already_stopped = self.command.left_wheel_speed == 0 and self.command.right_wheel_speed == 0
            self.command.left_wheel_speed = 0
            self.command.right_wheel_speed = 0
        if not already_stopped:
            rospy.logwarn_throttle(2.0, "Wheel speed command timeout reached. Stopping chassis motion.")
            self._write_motion_registers()

    def _publish_state(self):
        now = rospy.Time.now()
        with self._lock:
            command = ChassisCommand(**self.command.__dict__)
            snapshot = RegisterSnapshot(**self.snapshot.__dict__)
            connected = self.connected
            enabled = self.enabled
            last_error = self.last_error
            consecutive_failures = self.consecutive_failures

        wheel_msg = WheelSpeedState()
        wheel_msg.header.stamp = now
        wheel_msg.target_left_wheel_speed = command.left_wheel_speed
        wheel_msg.target_right_wheel_speed = command.right_wheel_speed
        wheel_msg.feedback_left_wheel_speed = snapshot.left_wheel_speed
        wheel_msg.feedback_right_wheel_speed = snapshot.right_wheel_speed
        wheel_msg.feedback_valid = connected
        self.wheel_speed_pub.publish(wheel_msg)

        status_msg = ChassisStatus()
        status_msg.header.stamp = now
        status_msg.connected = connected
        status_msg.enabled = enabled
        status_msg.work_mode = snapshot.work_mode
        status_msg.disc_speed_target = command.disc_speed
        status_msg.disc_speed_feedback = snapshot.disc_speed
        status_msg.disc_enabled = snapshot.disc_enable == DISC_ENABLE_ON
        status_msg.disc_lift_state = snapshot.disc_lift
        status_msg.light_enabled = snapshot.light == LIGHT_ON
        status_msg.consecutive_failures = consecutive_failures
        status_msg.last_error = last_error
        self.status_pub.publish(status_msg)

    def _publish_localization_watchdog_status(self):
        now = rospy.Time.now()
        mono = time.monotonic()
        with self._lock:
            locked = self._localization_watchdog_locked
            reason = self._localization_watchdog_reason
            recovery_active = self._recovery_glide_active
            recovery_distance = self._recovery_glide_distance_m
            recovery_start = self._recovery_glide_start_time
            front_distance = self._front_obstacle_distance_m
            scan_fresh = (
                self._last_scan_time > 0.0
                and (mono - self._last_scan_time) <= max(0.05, float(self.localization_recovery_scan_timeout_sec))
            )
            pose_quality_state = self._localization_pose_quality_state
            pose_quality_reason = self._localization_pose_quality_reason
            system_status = self._localization_system_status
            relocalization_status = self._localization_relocalization_status

        msg = LocalizationWatchdogStatus()
        msg.header.stamp = now
        msg.locked = bool(locked)
        msg.command_blocked = bool(locked and not self._manual_override_bypasses_localization_watchdog())
        msg.recovery_glide_active = bool(recovery_active)
        msg.state = "LOCKED" if locked else "OK"
        msg.reason = reason
        msg.recovery_distance_m = float(max(0.0, recovery_distance))
        msg.recovery_remaining_m = float(max(0.0, float(self.localization_recovery_max_distance_m) - recovery_distance))
        msg.recovery_duration_sec = float(max(0.0, mono - recovery_start)) if recovery_start > 0.0 else 0.0
        msg.front_obstacle_distance_m = float(front_distance) if math.isfinite(front_distance) else -1.0
        msg.scan_fresh = bool(scan_fresh)
        msg.pose_quality_state = pose_quality_state
        msg.pose_quality_reason = pose_quality_reason
        msg.system_status = system_status
        msg.relocalization_status = relocalization_status
        self.localization_watchdog_status_pub.publish(msg)

    def _publish_diagnostics(self):
        now = rospy.Time.now()
        with self._lock:
            connected = self.connected
            level = DiagnosticStatus.OK if connected else DiagnosticStatus.ERROR
            message = "connected" if connected else (self.last_error or "disconnected")
            consecutive_failures = self.consecutive_failures
            manual_override_active = self._manual_override_active
            localization_watchdog_locked = self._localization_watchdog_locked
            localization_watchdog_reason = self._localization_watchdog_reason
            localization_watchdog_waiting_manual_release = self._localization_watchdog_waiting_manual_release
            localization_system_status = self._localization_system_status
            localization_relocalization_status = self._localization_relocalization_status
            localization_pose_quality_state = self._localization_pose_quality_state
            localization_pose_quality_reason = self._localization_pose_quality_reason
            recovery_glide_active = self._recovery_glide_active
            recovery_glide_distance_m = self._recovery_glide_distance_m
            recovery_glide_stop_reason = self._recovery_glide_stop_reason
            front_obstacle_distance_m = self._front_obstacle_distance_m
            scan_age = time.monotonic() - self._last_scan_time if self._last_scan_time > 0.0 else float("inf")

        if connected and localization_watchdog_locked:
            level = DiagnosticStatus.WARN
            message = "localization watchdog locked: {}".format(localization_watchdog_reason or "locked")

        diag = DiagnosticStatus()
        diag.name = "grinder_chassis_driver"
        diag.hardware_id = "rs485_modbus_slave_{}".format(self.slave_id)
        diag.level = level
        diag.message = message
        diag.values = [
            KeyValue(key="port", value=str(self.port)),
            KeyValue(key="baudrate", value=str(self.baudrate)),
            KeyValue(key="slave_id", value=str(self.slave_id)),
            KeyValue(key="consecutive_failures", value=str(consecutive_failures)),
            KeyValue(key="manual_override_enabled", value=str(self.manual_override_enabled)),
            KeyValue(key="manual_override_active", value=str(manual_override_active)),
            KeyValue(
                key="manual_override_bypass_localization_watchdog",
                value=str(self.manual_override_bypass_localization_watchdog),
            ),
            KeyValue(key="manual_override_cancel_navigation", value=str(self.manual_override_cancel_navigation)),
            KeyValue(key="localization_watchdog_enabled", value=str(self.localization_watchdog_enabled)),
            KeyValue(key="localization_watchdog_locked", value=str(localization_watchdog_locked)),
            KeyValue(key="localization_watchdog_reason", value=str(localization_watchdog_reason)),
            KeyValue(key="localization_watchdog_auto_release", value=str(self.localization_watchdog_auto_release)),
            KeyValue(
                key="localization_watchdog_waiting_manual_release",
                value=str(localization_watchdog_waiting_manual_release),
            ),
            KeyValue(
                key="localization_watchdog_restore_motion_on_release",
                value=str(self.localization_watchdog_restore_motion_on_release),
            ),
            KeyValue(
                key="localization_watchdog_restore_disc_on_release",
                value=str(self.localization_watchdog_restore_disc_on_release),
            ),
            KeyValue(
                key="localization_watchdog_stop_disc_on_lock",
                value=str(self.localization_watchdog_stop_disc_on_lock),
            ),
            KeyValue(
                key="localization_watchdog_disc_speed_scale",
                value=str(self.localization_watchdog_disc_speed_scale),
            ),
            KeyValue(key="disc_speed_max_step", value=str(self.disc_speed_max_step)),
            KeyValue(key="enable_disc_speed_ramp_limit", value=str(self.enable_disc_speed_ramp_limit)),
            KeyValue(key="localization_pose_quality_warn_glide", value=str(self.localization_pose_quality_warn_glide)),
            KeyValue(
                key="localization_watchdog_stop_disc_when_not_gliding",
                value=str(self.localization_watchdog_stop_disc_when_not_gliding),
            ),
            KeyValue(
                key="localization_watchdog_use_system_status",
                value=str(self.localization_watchdog_use_system_status),
            ),
            KeyValue(
                key="localization_watchdog_use_relocalization_status",
                value=str(self.localization_watchdog_use_relocalization_status),
            ),
            KeyValue(key="localization_system_status", value=str(localization_system_status)),
            KeyValue(key="localization_relocalization_status", value=str(localization_relocalization_status)),
            KeyValue(key="localization_pose_quality_topic", value=str(self.localization_pose_quality_topic)),
            KeyValue(key="localization_pose_quality_state", value=str(localization_pose_quality_state)),
            KeyValue(key="localization_pose_quality_reason", value=str(localization_pose_quality_reason)),
            KeyValue(key="recovery_glide_active", value=str(recovery_glide_active)),
            KeyValue(key="recovery_glide_distance_m", value="{:.3f}".format(recovery_glide_distance_m)),
            KeyValue(key="recovery_glide_stop_reason", value=str(recovery_glide_stop_reason)),
            KeyValue(
                key="front_obstacle_distance_m",
                value="{:.3f}".format(front_obstacle_distance_m) if math.isfinite(front_obstacle_distance_m) else "inf",
            ),
            KeyValue(key="scan_age_sec", value="{:.2f}".format(scan_age) if math.isfinite(scan_age) else "inf"),
        ]

        array = DiagnosticArray()
        array.header.stamp = now
        array.status = [diag]
        self.diagnostics_pub.publish(array)

    def _mark_connected(self):
        with self._lock:
            self.connected = True
            self.last_error = ""
            self.consecutive_failures = 0

    def _handle_transport_error(self, exc):
        with self._lock:
            self.connected = False
            self.last_error = str(exc)
            self.consecutive_failures += 1
            failures = self.consecutive_failures
        rospy.logwarn_throttle(2.0, "Modbus transport error: %s", exc)
        if failures >= self.max_retries and self.stop_on_timeout and self.enable_safe_stop_on_comm_error:
            self._issue_safe_stop_on_error()

    def _issue_safe_stop_on_error(self):
        now = time.monotonic()
        with self._lock:
            if now - self._last_safe_stop_on_error_time < max(0.0, self.safe_stop_on_error_interval):
                return
            self._last_safe_stop_on_error_time = now
        rospy.logwarn_throttle(1.0, "Safe-stop on communication error triggered.")
        with self._lock:
            self.command.left_wheel_speed = 0
            self.command.right_wheel_speed = 0
            self.command.disc_speed = 0
            self.command.disc_enable = DISC_ENABLE_OFF
        try:
            self.transport.reconnect()
            self._write_all_outputs(force=True)
        except ModbusTransportError:
            pass

    def _apply_ramp_limit(self, target, last_value):
        if not self.enable_cmd_ramp_limit:
            return int(target)
        delta = int(target) - int(last_value)
        if delta > self.max_cmd_step_rpm:
            return int(last_value) + self.max_cmd_step_rpm
        if delta < -self.max_cmd_step_rpm:
            return int(last_value) - self.max_cmd_step_rpm
        return int(target)

    def _check_echo_deviation(self, snapshot):
        with self._lock:
            if not self.enabled:
                self.echo_failure_count = 0
                return
            expected_left = self.last_sent_left_wheel_speed
            expected_right = self.last_sent_right_wheel_speed
            max_dev = self.max_echo_deviation
            max_fail = max(1, self.max_echo_failures)

        left_diff = abs(int(snapshot.left_wheel_speed) - int(expected_left))
        right_diff = abs(int(snapshot.right_wheel_speed) - int(expected_right))
        if left_diff <= max_dev and right_diff <= max_dev:
            with self._lock:
                self.echo_failure_count = 0
            return

        with self._lock:
            self.echo_failure_count += 1
            echo_failures = self.echo_failure_count
        rospy.logwarn_throttle(
            1.0,
            "Modbus echo deviation warning: left_diff=%d right_diff=%d max=%d count=%d/%d",
            left_diff,
            right_diff,
            max_dev,
            echo_failures,
            max_fail,
        )
        if echo_failures >= max_fail:
            rospy.logwarn("Echo deviation protection triggered. Issuing safe stop.")
            self._issue_safe_stop_on_error()
            with self._lock:
                self.echo_failure_count = 0

    def _on_shutdown(self):
        try:
            self._issue_safe_stop()
            time.sleep(0.03)
            self._issue_safe_stop()
        except Exception:
            pass
        self.transport.close()


def main():
    rospy.init_node("grinder_chassis_driver")
    ChassisDriverNode()
    rospy.spin()
