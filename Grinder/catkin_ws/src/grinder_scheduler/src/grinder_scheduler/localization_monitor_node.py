#!/usr/bin/env python3

import math
import threading
import time

import rospy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from slamware_ros_sdk.msg import RelocalizationStatus, SystemStatus
from std_msgs.msg import Bool


def _get_bool_param(name, default):
    value = rospy.get_param(name, default)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def _normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def _yaw_from_quaternion(quat):
    x = float(quat.x)
    y = float(quat.y)
    z = float(quat.z)
    w = float(quat.w)
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class LocalizationMonitorNode:
    STATE_OK = "OK"
    STATE_WARN = "WARN"
    STATE_FAULT = "FAULT"
    STATE_UNKNOWN = "UNKNOWN"

    def __init__(self):
        self._lock = threading.Lock()
        self._started_at = time.monotonic()

        self.slamware_pose_topic = rospy.get_param(
            "~slamware_pose_topic",
            "/slamware_ros_sdk_server_node/robot_pose",
        )
        self.amcl_pose_topic = rospy.get_param("~amcl_pose_topic", "/localization_shadow/amcl_pose")
        self.system_status_topic = rospy.get_param(
            "~system_status_topic",
            "/slamware_ros_sdk_server_node/system_status",
        )
        self.relocalization_status_topic = rospy.get_param(
            "~relocalization_status_topic",
            "/slamware_ros_sdk_server_node/relocalization_status",
        )
        self.initialpose_topic = rospy.get_param("~initialpose_topic", "/localization_shadow/initialpose")
        self.healthy_topic = rospy.get_param("~healthy_topic", "/localization_monitor/healthy")
        self.fault_topic = rospy.get_param(
            "~localization_monitor_fault_topic",
            rospy.get_param("~fault_topic", "/localization_monitor/fault"),
        )
        self.expected_frame = rospy.get_param("~expected_frame", "map").strip()
        self.action_mode = rospy.get_param("~localization_monitor_action_mode", "warn_only").strip().lower()

        self.check_hz = max(0.1, float(rospy.get_param("~localization_monitor_check_hz", 10.0)))
        self.status_publish_hz = max(
            0.1,
            float(rospy.get_param("~localization_monitor_status_publish_hz", 2.0)),
        )
        self.diagnostics_publish_hz = max(
            0.1,
            float(rospy.get_param("~localization_monitor_diagnostics_publish_hz", 1.0)),
        )
        self.pose_timeout_sec = max(0.0, float(rospy.get_param("~localization_monitor_pose_timeout_sec", 1.0)))

        self.warn_position_m = float(rospy.get_param("~localization_monitor_warn_position_m", 0.30))
        self.fault_position_m = float(rospy.get_param("~localization_monitor_fault_position_m", 0.60))
        self.clear_position_m = float(rospy.get_param("~localization_monitor_clear_position_m", 0.35))
        self.warn_yaw_rad = math.radians(float(rospy.get_param("~localization_monitor_warn_yaw_deg", 10.0)))
        self.fault_yaw_rad = math.radians(float(rospy.get_param("~localization_monitor_fault_yaw_deg", 20.0)))
        self.clear_yaw_rad = math.radians(float(rospy.get_param("~localization_monitor_clear_yaw_deg", 12.0)))
        self.warn_hold_sec = max(0.0, float(rospy.get_param("~localization_monitor_warn_hold_sec", 1.0)))
        self.fault_hold_sec = max(0.0, float(rospy.get_param("~localization_monitor_fault_hold_sec", 2.0)))
        self.clear_hold_sec = max(0.0, float(rospy.get_param("~localization_monitor_clear_hold_sec", 3.0)))

        self.amcl_max_position_stddev_m = float(
            rospy.get_param("~localization_monitor_amcl_max_position_stddev_m", 1.5)
        )
        self.amcl_max_yaw_stddev_rad = float(
            rospy.get_param("~localization_monitor_amcl_max_yaw_stddev_rad", 1.0)
        )

        self.initialize_amcl_on_startup = _get_bool_param("~initialize_amcl_on_startup", True)
        self.initialize_amcl_on_relocalization_succeed = _get_bool_param(
            "~initialize_amcl_on_relocalization_succeed",
            True,
        )
        self.initialpose_startup_delay_sec = max(
            0.0,
            float(rospy.get_param("~initialpose_startup_delay_sec", 0.5)),
        )
        self.initialpose_repeat_count = max(1, int(rospy.get_param("~initialpose_repeat_count", 3)))
        self.initialpose_repeat_interval_sec = max(
            0.05,
            float(rospy.get_param("~initialpose_repeat_interval_sec", 0.2)),
        )
        self.initialpose_covariance_xy_m = max(
            0.0,
            float(rospy.get_param("~initialpose_covariance_xy_m", 0.25)),
        )
        self.initialpose_covariance_yaw_deg = max(
            0.0,
            float(rospy.get_param("~initialpose_covariance_yaw_deg", 10.0)),
        )

        self._slamware_pose = None
        self._slamware_frame = ""
        self._slamware_time = 0.0
        self._amcl_pose = None
        self._amcl_frame = ""
        self._amcl_covariance = None
        self._amcl_time = 0.0
        self._system_status = ""
        self._relocalization_status = ""
        self._last_relocalization_status = ""

        self._state = self.STATE_UNKNOWN
        self._state_reason = "waiting_for_pose"
        self._healthy = False
        self._fault = False
        self._position_error_m = float("nan")
        self._yaw_error_rad = float("nan")
        self._warn_since = None
        self._fault_since = None
        self._clear_since = None

        self._startup_initialpose_triggered = False
        self._pending_initialpose_count = 0
        self._pending_initialpose_reason = ""
        self._last_initialpose_publish_time = 0.0

        self.initialpose_pub = rospy.Publisher(self.initialpose_topic, PoseWithCovarianceStamped, queue_size=2)
        self.healthy_pub = rospy.Publisher(self.healthy_topic, Bool, queue_size=10, latch=True)
        self.fault_pub = rospy.Publisher(self.fault_topic, Bool, queue_size=10, latch=True)
        self.diagnostics_pub = rospy.Publisher("/diagnostics", DiagnosticArray, queue_size=10)

        rospy.Subscriber(self.slamware_pose_topic, PoseStamped, self._handle_slamware_pose, queue_size=10)
        rospy.Subscriber(self.amcl_pose_topic, PoseWithCovarianceStamped, self._handle_amcl_pose, queue_size=10)
        rospy.Subscriber(self.system_status_topic, SystemStatus, self._handle_system_status, queue_size=10)
        rospy.Subscriber(
            self.relocalization_status_topic,
            RelocalizationStatus,
            self._handle_relocalization_status,
            queue_size=10,
        )

        rospy.Timer(rospy.Duration.from_sec(1.0 / self.check_hz), self._check_timer)
        rospy.Timer(rospy.Duration.from_sec(1.0 / self.status_publish_hz), self._status_timer)
        rospy.Timer(rospy.Duration.from_sec(1.0 / self.diagnostics_publish_hz), self._diagnostics_timer)

    def _handle_slamware_pose(self, msg):
        pose = msg.pose
        with self._lock:
            self._slamware_pose = pose
            self._slamware_frame = str(msg.header.frame_id or "")
            self._slamware_time = time.monotonic()

    def _handle_amcl_pose(self, msg):
        with self._lock:
            self._amcl_pose = msg.pose.pose
            self._amcl_frame = str(msg.header.frame_id or "")
            self._amcl_covariance = list(msg.pose.covariance)
            self._amcl_time = time.monotonic()

    def _handle_system_status(self, msg):
        with self._lock:
            self._system_status = str(msg.status)

    def _handle_relocalization_status(self, msg):
        status = str(msg.status)
        trigger_initialpose = False
        with self._lock:
            previous = self._last_relocalization_status
            self._relocalization_status = status
            self._last_relocalization_status = status
            if (
                self.initialize_amcl_on_relocalization_succeed
                and status == "RelocalizationSucceed"
                and previous != status
            ):
                trigger_initialpose = True
        if trigger_initialpose:
            self._request_initialpose("relocalization_succeed")

    def _request_initialpose(self, reason):
        with self._lock:
            self._pending_initialpose_count = max(self._pending_initialpose_count, self.initialpose_repeat_count)
            self._pending_initialpose_reason = str(reason or "requested")
            self._last_initialpose_publish_time = 0.0

    def _check_timer(self, _event):
        now = time.monotonic()
        if self.initialize_amcl_on_startup and not self._startup_initialpose_triggered:
            with self._lock:
                have_slamware_pose = self._slamware_pose is not None
            if have_slamware_pose and (now - self._started_at) >= self.initialpose_startup_delay_sec:
                self._startup_initialpose_triggered = True
                self._request_initialpose("startup")

        self._publish_pending_initialpose(now)
        self._update_state(now)

    def _status_timer(self, _event):
        with self._lock:
            healthy = bool(self._healthy)
            fault = bool(self._fault)
        self.healthy_pub.publish(Bool(data=healthy))
        self.fault_pub.publish(Bool(data=fault))

    def _diagnostics_timer(self, _event):
        now = rospy.Time.now()
        with self._lock:
            state = self._state
            reason = self._state_reason
            healthy = self._healthy
            fault = self._fault
            position_error_m = self._position_error_m
            yaw_error_rad = self._yaw_error_rad
            slamware_frame = self._slamware_frame
            amcl_frame = self._amcl_frame
            system_status = self._system_status
            relocalization_status = self._relocalization_status
            slamware_age = time.monotonic() - self._slamware_time if self._slamware_time > 0.0 else float("inf")
            amcl_age = time.monotonic() - self._amcl_time if self._amcl_time > 0.0 else float("inf")

        status = DiagnosticStatus()
        status.name = "localization_monitor"
        status.hardware_id = "localization_shadow"
        if fault:
            status.level = DiagnosticStatus.ERROR
        elif state in (self.STATE_WARN, self.STATE_UNKNOWN):
            status.level = DiagnosticStatus.WARN
        else:
            status.level = DiagnosticStatus.OK
        status.message = "{}: {}".format(state, reason or "ok")
        status.values = [
            KeyValue(key="state", value=str(state)),
            KeyValue(key="healthy", value=str(healthy)),
            KeyValue(key="fault", value=str(fault)),
            KeyValue(key="action_mode", value=str(self.action_mode)),
            KeyValue(key="reason", value=str(reason)),
            KeyValue(key="position_error_m", value=self._format_float(position_error_m, 3)),
            KeyValue(key="yaw_error_deg", value=self._format_float(math.degrees(yaw_error_rad), 2)),
            KeyValue(key="slamware_pose_topic", value=self.slamware_pose_topic),
            KeyValue(key="amcl_pose_topic", value=self.amcl_pose_topic),
            KeyValue(key="slamware_frame", value=slamware_frame),
            KeyValue(key="amcl_frame", value=amcl_frame),
            KeyValue(key="slamware_pose_age_sec", value=self._format_float(slamware_age, 2)),
            KeyValue(key="amcl_pose_age_sec", value=self._format_float(amcl_age, 2)),
            KeyValue(key="system_status", value=system_status),
            KeyValue(key="relocalization_status", value=relocalization_status),
            KeyValue(key="warn_position_m", value=str(self.warn_position_m)),
            KeyValue(key="fault_position_m", value=str(self.fault_position_m)),
            KeyValue(key="warn_yaw_deg", value=str(math.degrees(self.warn_yaw_rad))),
            KeyValue(key="fault_yaw_deg", value=str(math.degrees(self.fault_yaw_rad))),
        ]

        array = DiagnosticArray()
        array.header.stamp = now
        array.status = [status]
        self.diagnostics_pub.publish(array)

    def _publish_pending_initialpose(self, now):
        with self._lock:
            if self._pending_initialpose_count <= 0:
                return
            if self._slamware_pose is None:
                return
            if (now - self._last_initialpose_publish_time) < self.initialpose_repeat_interval_sec:
                return
            pose = self._slamware_pose
            frame = self.expected_frame or self._slamware_frame or "map"
            reason = self._pending_initialpose_reason
            self._pending_initialpose_count -= 1
            self._last_initialpose_publish_time = now

        msg = PoseWithCovarianceStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = frame
        msg.pose.pose = pose
        cov_xy = self.initialpose_covariance_xy_m * self.initialpose_covariance_xy_m
        cov_yaw = math.radians(self.initialpose_covariance_yaw_deg)
        msg.pose.covariance[0] = cov_xy
        msg.pose.covariance[7] = cov_xy
        msg.pose.covariance[35] = cov_yaw * cov_yaw
        self.initialpose_pub.publish(msg)
        rospy.loginfo_throttle(
            1.0,
            "Published AMCL initialpose from Slamware pose: reason=%s topic=%s",
            reason,
            self.initialpose_topic,
        )

    def _update_state(self, now):
        with self._lock:
            slamware_pose = self._slamware_pose
            slamware_frame = self._slamware_frame
            slamware_age = now - self._slamware_time if self._slamware_time > 0.0 else float("inf")
            amcl_pose = self._amcl_pose
            amcl_frame = self._amcl_frame
            amcl_age = now - self._amcl_time if self._amcl_time > 0.0 else float("inf")
            amcl_covariance = self._amcl_covariance
            fault = self._fault
            warn_since = self._warn_since
            fault_since = self._fault_since
            clear_since = self._clear_since

        reason = ""
        state = self.STATE_OK
        position_error_m = float("nan")
        yaw_error_rad = float("nan")
        healthy = True

        if slamware_pose is None or slamware_age > self.pose_timeout_sec:
            state = self.STATE_UNKNOWN
            reason = "slamware_pose_timeout"
            healthy = False
        elif amcl_pose is None or amcl_age > self.pose_timeout_sec:
            state = self.STATE_UNKNOWN
            reason = "amcl_pose_timeout"
            healthy = False
        elif self.expected_frame and slamware_frame and slamware_frame != self.expected_frame:
            state = self.STATE_UNKNOWN
            reason = "slamware_frame_mismatch"
            healthy = False
        elif self.expected_frame and amcl_frame and amcl_frame != self.expected_frame:
            state = self.STATE_UNKNOWN
            reason = "amcl_frame_mismatch"
            healthy = False
        elif not self._amcl_covariance_is_converged(amcl_covariance):
            state = self.STATE_UNKNOWN
            reason = "amcl_not_converged"
            healthy = False
        else:
            dx = float(slamware_pose.position.x) - float(amcl_pose.position.x)
            dy = float(slamware_pose.position.y) - float(amcl_pose.position.y)
            position_error_m = math.hypot(dx, dy)
            slamware_yaw = _yaw_from_quaternion(slamware_pose.orientation)
            amcl_yaw = _yaw_from_quaternion(amcl_pose.orientation)
            yaw_error_rad = abs(_normalize_angle(slamware_yaw - amcl_yaw))

            fault_candidate = position_error_m >= self.fault_position_m or yaw_error_rad >= self.fault_yaw_rad
            warn_candidate = position_error_m >= self.warn_position_m or yaw_error_rad >= self.warn_yaw_rad
            clear_candidate = position_error_m <= self.clear_position_m and yaw_error_rad <= self.clear_yaw_rad

            if fault:
                if clear_candidate:
                    if clear_since is None:
                        clear_since = now
                    if (now - clear_since) >= self.clear_hold_sec:
                        fault = False
                        clear_since = None
                        fault_since = None
                        warn_since = None
                        state = self.STATE_OK
                        reason = "recovered"
                        healthy = True
                    else:
                        state = self.STATE_FAULT
                        reason = "waiting_clear_hold"
                        healthy = False
                else:
                    clear_since = None
                    state = self.STATE_FAULT
                    reason = "position_or_yaw_error"
                    healthy = False
            elif fault_candidate:
                warn_since = None
                clear_since = None
                if fault_since is None:
                    fault_since = now
                if (now - fault_since) >= self.fault_hold_sec:
                    fault = True
                    state = self.STATE_FAULT
                    reason = "position_or_yaw_error"
                    healthy = False
                else:
                    state = self.STATE_WARN
                    reason = "fault_candidate_hold"
                    healthy = False
            elif warn_candidate:
                fault_since = None
                clear_since = None
                if warn_since is None:
                    warn_since = now
                if (now - warn_since) >= self.warn_hold_sec:
                    state = self.STATE_WARN
                    reason = "position_or_yaw_error"
                    healthy = False
                else:
                    state = self.STATE_OK
                    reason = "warn_candidate_hold"
                    healthy = True
            else:
                warn_since = None
                fault_since = None
                clear_since = None
                state = self.STATE_OK
                reason = "ok"
                healthy = True

        with self._lock:
            self._state = state
            self._state_reason = reason
            self._healthy = healthy
            self._fault = fault
            self._position_error_m = position_error_m
            self._yaw_error_rad = yaw_error_rad
            self._warn_since = warn_since
            self._fault_since = fault_since
            self._clear_since = clear_since

    def _amcl_covariance_is_converged(self, covariance):
        if not covariance or len(covariance) < 36:
            return True
        try:
            pos_var = max(float(covariance[0]), float(covariance[7]), 0.0)
            yaw_var = max(float(covariance[35]), 0.0)
            pos_stddev = math.sqrt(pos_var)
            yaw_stddev = math.sqrt(yaw_var)
            return (
                pos_stddev <= self.amcl_max_position_stddev_m
                and yaw_stddev <= self.amcl_max_yaw_stddev_rad
            )
        except Exception:
            return False

    @staticmethod
    def _format_float(value, digits):
        try:
            if math.isnan(value) or math.isinf(value):
                return str(value)
            return ("{:." + str(int(digits)) + "f}").format(float(value))
        except Exception:
            return str(value)


def main():
    rospy.init_node("localization_monitor")
    LocalizationMonitorNode()
    rospy.spin()


if __name__ == "__main__":
    main()
