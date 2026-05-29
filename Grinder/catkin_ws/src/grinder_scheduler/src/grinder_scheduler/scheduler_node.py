#!/usr/bin/env python3

import json
import math
import os
import re
import shutil
import time
import zlib
import base64
from datetime import datetime
from collections import deque
from dataclasses import asdict

import cv2
import numpy as np
import rospy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Pose, PoseStamped, Twist
from grinder_chassis_driver.msg import ChassisStatus, WheelSpeedCommand
from grinder_chassis_driver.srv import EnableChassis
from nav_msgs.msg import Path
from nav_msgs.srv import LoadMap
from std_msgs.msg import Bool, Int16, UInt16
from std_srvs.srv import Trigger, TriggerResponse

try:
    import tf2_ros
    from tf.transformations import euler_from_quaternion
except Exception:
    tf2_ros = None
    euler_from_quaternion = None

from grinder_scheduler.aurora_bridge import AuroraBridge
from grinder_scheduler.local_rtsp_server import LocalRtspStreamServer
from grinder_scheduler.map_service import MapService
from grinder_scheduler.media_streamer import FFmpegMediaStreamer
from grinder_scheduler.map_catalog_response import fill_map_catalog_response
from grinder_scheduler.models import PlannerPath, SchedulerState, TaskConfigModel, VideoStreamState
from grinder_scheduler.msg import MapPreviewMetadata, SchedulerStatus
from grinder_scheduler.planner_adapter import PlannerAdapter
from grinder_scheduler.sl_linka_adapter import SlLinkAServer

try:
    from slamware_ros_sdk.srv import SyncGetStcm, SyncSetStcm
    from slamware_ros_sdk.msg import MapKind, SetMapLocalizationRequest, SetMapUpdateRequest
except Exception:
    SyncGetStcm = None
    SyncSetStcm = None
    MapKind = None
    SetMapLocalizationRequest = None
    SetMapUpdateRequest = None

PREVIEW_MAX_EDGE_CAP = 640
DEFAULT_LIVE_MAP_ID = "LIVE_MAP"


def _format_ts_s(ts_value):
    try:
        ts = int(float(ts_value))
    except Exception:
        return ""
    if ts <= 0:
        return ""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _detect_runtime_base_dir():
    env_base = os.environ.get("GRINDER_BASE_DIR", "").strip()
    if env_base:
        return os.path.abspath(os.path.expanduser(os.path.expandvars(env_base)))
    # scheduler_node.py -> grinder_scheduler/src/grinder_scheduler/scheduler_node.py
    # repo root (Grinder) is 5 levels up.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))


def _resolve_runtime_path(path_value, base_dir):
    if path_value is None:
        return ""
    normalized = os.path.expanduser(os.path.expandvars(str(path_value).strip()))
    if not normalized:
        return ""
    if os.path.isabs(normalized):
        return os.path.normpath(normalized)
    return os.path.normpath(os.path.join(base_dir, normalized))


class SchedulerNode:
    @staticmethod
    def _sanitize_preview_edge(value, default_edge=PREVIEW_MAX_EDGE_CAP, cap_edge=PREVIEW_MAX_EDGE_CAP):
        if value is None:
            edge = int(default_edge)
        else:
            try:
                edge = int(value)
            except Exception:
                edge = int(default_edge)
        edge = max(64, edge)
        return min(int(cap_edge), edge)

    def __init__(self):
        self.state = SchedulerState.IDLE
        self.task_config = TaskConfigModel()
        self._load_robot_config_from_params()
        self._progress_history = deque(maxlen=180)
        self.last_error = ""
        self.replan_requested = False
        self.current_path = None
        self.current_path_index = 0
        self._goal_points = []
        self._goal_segment_yaw_threshold_deg = max(
            1.0, float(rospy.get_param("~path_goal_segment_yaw_threshold_deg", 25.0))
        )
        self.last_chassis_status = None
        self._exec_mode = str(rospy.get_param("~path_execution_mode", "move_base_goal")).strip().lower()
        if self._exec_mode != "move_base_goal":
            rospy.logwarn(
                "path_execution_mode=%s is deprecated in scheduler; force to move_base_goal (cmd_vel now handled by chassis_driver)",
                self._exec_mode,
            )
            self._exec_mode = "move_base_goal"
        # Deprecated: scheduler no longer publishes goals to /move_base_simple/goal.
        self._exec_goal_topic = rospy.get_param("~path_goal_topic", "/move_base_simple/goal")
        self._task_enable_topic = rospy.get_param("~task_enable_topic", "/chassis/task_enable")
        self._task_enable_runtime_active = False
        self._path_plan_request_use_all_regions = bool(rospy.get_param("~path_plan_request_use_all_regions", True))
        self._exec_goal_reach_dist = max(0.05, float(rospy.get_param("~path_goal_reach_dist", 0.25)))
        self._exec_goal_interval = max(0.1, float(rospy.get_param("~path_goal_interval", 1.0)))
        self._exec_segment_timeout = max(2.0, float(rospy.get_param("~path_segment_timeout", 60.0)))
        self._exec_max_linear = max(0.05, float(rospy.get_param("~path_exec_max_linear", 0.35)))
        self._exec_max_angular = max(0.1, float(rospy.get_param("~path_exec_max_angular", 0.9)))
        self._exec_k_linear = max(0.05, float(rospy.get_param("~path_exec_k_linear", 0.8)))
        self._exec_k_angular = max(0.05, float(rospy.get_param("~path_exec_k_angular", 1.5)))
        self._exec_active = False
        self._exec_goal_index = 0
        self._exec_last_send_time = 0.0
        self._exec_last_force_send_time = 0.0
        self._exec_goal_start_time = 0.0
        self._exec_publish_start_pose_once = False
        self._exec_region_order = []
        self._exec_region_index = -1
        self._exec_region_repeat_done = {}
        self._disc_follow_path_type = bool(rospy.get_param("~disc_follow_path_type", True))
        self._disc_last_mode = ""  # "cover" | "transition" | ""
        self._task_stop_reason = ""
        self._last_task_result = {}
        # Task result color palette (repeat index -> color, BGR).
        self._task_result_palette_bgr = [
            (74, 201, 245),   # 1
            (90, 210, 120),   # 2
            (180, 170, 70),   # 3
            (220, 120, 70),   # 4
            (200, 90, 160),   # 5
            (160, 70, 210),   # 6
            (80, 80, 230),    # 7
        ]
        self._current_plan_scope = "single"
        self._task_bindings = {}
        self._map_registry = {}
        self._chassis_settings = {
            "work_mode": 1,  # 1:auto, 2:manual
            "disc_speed_rpm": 1200,
            "run_speed": float(rospy.get_param("~default_chassis_run_speed", 0.4)),
        }
        self._live_map_id = str(rospy.get_param("~live_map_id", DEFAULT_LIVE_MAP_ID)).strip() or DEFAULT_LIVE_MAP_ID
        self._active_map_id = self._live_map_id
        self._last_seen_map_id = ""
        runtime_base_param = rospy.get_param("~runtime_base_dir", "").strip()
        self._runtime_base_dir = (
            _resolve_runtime_path(runtime_base_param, os.getcwd())
            if runtime_base_param
            else _detect_runtime_base_dir()
        )
        self._preview_max_edge_cap = max(64, int(rospy.get_param("~preview_max_edge_cap", PREVIEW_MAX_EDGE_CAP)))
        self._robot_config_yaml_path = _resolve_runtime_path(
            rospy.get_param("~robot_config_yaml_path", "catkin_ws/src/grinder_scheduler/config/scheduler.yaml"),
            self._runtime_base_dir,
        )
        self._initial_map_preview_saved = False
        self._initial_map_preview_dir = _resolve_runtime_path(
            rospy.get_param("~initial_map_preview_dir", "temp"),
            self._runtime_base_dir,
        )
        self._initial_map_preview_max_edge = self._sanitize_preview_edge(
            rospy.get_param("~initial_map_preview_max_edge", PREVIEW_MAX_EDGE_CAP),
            cap_edge=self._preview_max_edge_cap,
        )
        self._initial_map_preview_format = rospy.get_param("~initial_map_preview_format", "jpg")
        self._planned_path_preview_dir = _resolve_runtime_path(
            rospy.get_param("~planned_path_preview_dir", "temp"),
            self._runtime_base_dir,
        )
        self._planned_path_debug_dir = _resolve_runtime_path(
            rospy.get_param("~planned_path_debug_dir", "temp/path_debug"),
            self._runtime_base_dir,
        )
        self._planned_path_preview_max_edge = self._sanitize_preview_edge(
            rospy.get_param("~planned_path_preview_max_edge", PREVIEW_MAX_EDGE_CAP),
            cap_edge=self._preview_max_edge_cap,
        )
        self._planned_path_preview_format = rospy.get_param("~planned_path_preview_format", "jpg")
        self._planned_path_preview_include_overlay = bool(rospy.get_param("~planned_path_preview_include_overlay", True))
        # Path preview annotation policy:
        # disable direction arrows / target index overlays to keep the preview clean.
        self._planned_path_preview_show_direction = False
        self._planned_path_preview_arrow_step = max(
            1, int(rospy.get_param("~planned_path_preview_arrow_step", 10))
        )
        self._planned_path_preview_arrow_len_px = max(
            4, int(rospy.get_param("~planned_path_preview_arrow_len_px", 12))
        )
        requested_use_all = bool(rospy.get_param("~plan_use_all_work_regions", False))
        # Single-region planning policy:
        # even if param is set, enforce one work region per planning request.
        self._plan_use_all_work_regions = False
        if requested_use_all:
            rospy.logwarn("plan_use_all_work_regions is ignored: single-region planning mode is enforced.")
        self._reload_navigation_map_on_plan = bool(rospy.get_param("~reload_navigation_map_on_plan", True))
        self._persist_state_enabled = bool(rospy.get_param("~persist_state_enabled", True))
        # Runtime-task persistence switch:
        # False => task is realtime-only and must be re-sent by APP every launch.
        self._persist_runtime_task_state = bool(rospy.get_param("~persist_runtime_task_state", False))
        self._persist_state_dir = _resolve_runtime_path(
            rospy.get_param("~persist_state_dir", "temp/grinder_scheduler_state"),
            self._runtime_base_dir,
        )
        self._map_registry_state_file = os.path.join(self._persist_state_dir, "map_registry.json")
        self._task_registry_state_file = os.path.join(self._persist_state_dir, "task_registry.json")
        self._live_preview_enabled = bool(rospy.get_param("~live_preview_enabled", True))
        self._live_preview_hz = max(0.1, float(rospy.get_param("~live_preview_hz", 1.0)))
        self._live_preview_max_edge = self._sanitize_preview_edge(
            rospy.get_param("~live_preview_max_edge", PREVIEW_MAX_EDGE_CAP),
            cap_edge=self._preview_max_edge_cap,
        )
        self._live_preview_format = rospy.get_param("~live_preview_format", "jpg")
        self._live_preview_file = _resolve_runtime_path(
            rospy.get_param("~live_preview_file", "temp/aurora_map_preview_latest.jpg"),
            self._runtime_base_dir,
        )
        self._live_preview_next_time = 0.0
        self._live_map_enabled = bool(rospy.get_param("~live_map_enabled", True))
        self._live_map_hz = max(0.1, float(rospy.get_param("~live_map_hz", 1.0)))
        self._live_map_dir = _resolve_runtime_path(
            rospy.get_param("~live_map_dir", "temp/live_map"),
            self._runtime_base_dir,
        )
        self._live_map_yaml_name = rospy.get_param("~live_map_yaml_name", "map.yaml")
        self._live_map_image_name = rospy.get_param("~live_map_image_name", "map1.pgm")
        self._live_map_next_time = 0.0
        self._live_map_crop_to_free_space = bool(rospy.get_param("~live_map_crop_to_free_space", True))
        self._live_map_crop_margin_m = max(0.0, float(rospy.get_param("~live_map_crop_margin_m", 0.5)))
        self._live_map_cache_clear_mode = str(
            rospy.get_param("~live_map_cache_clear_mode", "all")
        ).strip().lower()
        if self._live_map_cache_clear_mode not in ("all", "memory_only"):
            self._live_map_cache_clear_mode = "all"
        self._live_map_align_to_initial_yaw = bool(
            rospy.get_param("~live_map_align_to_initial_yaw", True)
        )
        self._live_map_source_frame = str(rospy.get_param("~live_map_source_frame", "map")).strip() or "map"
        self._live_map_aligned_frame = str(rospy.get_param("~live_map_aligned_frame", "map_aligned")).strip() or "map_aligned"
        self._live_map_align_yaw_timeout = max(
            0.01, float(rospy.get_param("~live_map_align_yaw_timeout", 0.05))
        )
        self._live_map_last_rotated_version = None
        self._live_map_last_rotated_yaw = None
        self._live_map_last_rotated_grid = None
        self._live_map_last_rotated_origin = None
        self._initial_pose_alignment_yaw = None
        self._tf_buffer = None
        self._tf_listener = None
        if self._live_map_align_to_initial_yaw and tf2_ros is not None:
            try:
                self._tf_buffer = tf2_ros.Buffer(cache_time=rospy.Duration(10.0))
                self._tf_listener = tf2_ros.TransformListener(self._tf_buffer)
            except Exception as exc:
                rospy.logwarn("Failed to init tf2 listener for live map alignment: %s", exc)
                self._tf_buffer = None
                self._tf_listener = None
        self._saved_map_thumb_max_edge = max(64, int(rospy.get_param("~saved_map_thumb_max_edge", 192)))
        self._saved_map_thumb_jpeg_quality = max(30, min(95, int(rospy.get_param("~saved_map_thumb_jpeg_quality", 70))))
        self._map_catalog_max_items = max(1, int(rospy.get_param("~map_catalog_max_items", 200)))
        self._map_catalog_include_thumbnails = bool(rospy.get_param("~map_catalog_include_thumbnails", True))
        self._map_catalog_max_thumbnail_b64_total = max(
            0, int(rospy.get_param("~map_catalog_max_thumbnail_b64_total", 512000))
        )
        self._last_manual_enable_try = 0.0
        manual_base_default = 600
        manual_base_from_chassis = rospy.get_param(
            "/chassis_driver/manual_drive_max_wheel_speed",
            rospy.get_param("/chassis_driver/cmd_vel_max_abs_wheel_rpm", manual_base_default),
        )
        self._manual_drive_base_speed = max(1, int(manual_base_from_chassis))
        self._manual_reverse_guard_sec = max(0.0, float(rospy.get_param("~manual_reverse_guard_sec", 0.25)))
        self._manual_reverse_until = 0.0
        self._manual_last_left_cmd = 0
        self._manual_last_right_cmd = 0
        self._map_request_encoding = str(rospy.get_param("~map_request_encoding", "png")).strip().lower()
        self._nav_map_yaml_path = _resolve_runtime_path(
            rospy.get_param(
                "~navigation_map_yaml_path",
                "catkin_ws/src/2-dnavigation-package/2dnavigation/teb_local_planner_tutorials/maps/map.yaml",
            ),
            self._runtime_base_dir,
        )
        self._stcm_local_dir = _resolve_runtime_path(
            rospy.get_param("~stcm_local_dir", "maps/raw"),
            self._runtime_base_dir,
        )
        self._sync_get_stcm_service = rospy.get_param(
            "~sync_get_stcm_service", "/slamware_ros_sdk_server_node/sync_get_stcm"
        )
        self._sync_set_stcm_service = rospy.get_param(
            "~sync_set_stcm_service", "/slamware_ros_sdk_server_node/sync_set_stcm"
        )
        self._change_map_service = rospy.get_param("~change_map_service", "/change_map")
        self._set_map_update_topic = rospy.get_param(
            "~set_map_update_topic", "/slamware_ros_sdk_server_node/set_map_update"
        )
        self._set_map_localization_topic = rospy.get_param(
            "~set_map_localization_topic", "/slamware_ros_sdk_server_node/set_map_localization"
        )
        self._sync_get_proxy = None
        self._sync_set_proxy = None
        self._change_map_proxy = None

        self.map_service = MapService()
        self.map_service.set_draw_region_id_on_preview(
            bool(rospy.get_param("~draw_region_id_on_preview", True))
        )
        self.map_service.set_draw_region_label_on_preview(
            bool(rospy.get_param("~draw_region_label_on_preview", True))
        )
        self._load_local_state()
        self.aurora_bridge = AuroraBridge(
            map_topic=rospy.get_param("~map_topic", "/slamware_ros_sdk_server_node/map"),
            odom_topic=rospy.get_param("~odom_topic", "/slamware_ros_sdk_server_node/odom"),
            left_image_topic=rospy.get_param("~left_image_topic", "/slamware_ros_sdk_server_node/left_image_raw"),
            right_image_topic=rospy.get_param("~right_image_topic", "/slamware_ros_sdk_server_node/right_image_raw"),
            first_frame_save_dir=_resolve_runtime_path(
                rospy.get_param("~first_frame_save_dir", "temp"),
                self._runtime_base_dir,
            ),
            save_first_frame_on_startup=bool(rospy.get_param("~save_first_frame_on_startup", False)),
            use_depth_colorized_image=rospy.get_param("~use_depth_colorized_image", True),
            depth_image_colorized_topic=rospy.get_param("~depth_image_colorized_topic", "/slamware_ros_sdk_server_node/depth_image_colorized"),
        )
        self.planner = PlannerAdapter(
            _resolve_runtime_path(
                rospy.get_param("~planner_script_path", "third_party/path_planner/mst25.py"),
                self._runtime_base_dir,
            )
        )
        self.media_streamer = FFmpegMediaStreamer(
            stream_url=rospy.get_param("~stream_url", ""),
            fps=rospy.get_param("~stream_fps", 8),
            width=rospy.get_param("~stream_width", 1280),
            enabled=rospy.get_param("~stream_enabled", True),
        )
        self.local_stream_server = LocalRtspStreamServer(
            host=rospy.get_param("~local_rtsp_host", "0.0.0.0"),
            public_host=rospy.get_param("~local_rtsp_public_host", "auto"),
            port=rospy.get_param("~local_rtsp_port", 8554),
            fps=rospy.get_param("~local_rtsp_fps", 12),
            width=rospy.get_param("~local_rtsp_width", 960),
            enabled=rospy.get_param("~local_rtsp_enabled", True),
            start_server=rospy.get_param("~local_rtsp_start_server", True),
            preferred_encoder=str(rospy.get_param("~local_rtsp_encoder", "auto")).strip().lower(),
            mediamtx_path=_resolve_runtime_path(
                rospy.get_param("~local_rtsp_mediamtx_path", "tools/mediamtx/mediamtx"),
                self._runtime_base_dir,
            ),
            log_dir=_resolve_runtime_path(
                rospy.get_param("~local_rtsp_log_dir", "temp"),
                self._runtime_base_dir,
            ),
        )
        self._local_rtsp_max_frame_age = max(0.1, float(rospy.get_param("~local_rtsp_max_frame_age", 0.4)))
        self.local_stream_server.start()

        self._global_plan_topic = rospy.get_param("~global_plan_topic", "/grinder/GlobalPlanner/plan")
        self.global_plan_pub = rospy.Publisher(self._global_plan_topic, Path, queue_size=1, latch=True)
        self.goal_pub = rospy.Publisher(self._exec_goal_topic, PoseStamped, queue_size=10)
        self.task_enable_pub = rospy.Publisher(self._task_enable_topic, Bool, queue_size=10, latch=True)
        self.status_pub = rospy.Publisher("/scheduler/status", SchedulerStatus, queue_size=10)
        self.preview_meta_pub = rospy.Publisher("/scheduler/map_preview_metadata", MapPreviewMetadata, queue_size=10, latch=True)
        self.diagnostics_pub = rospy.Publisher("/diagnostics", DiagnosticArray, queue_size=10)
        self._set_map_update_pub = None
        self._set_map_localization_pub = None
        if SetMapUpdateRequest is not None:
            self._set_map_update_pub = rospy.Publisher(
                self._set_map_update_topic, SetMapUpdateRequest, queue_size=2
            )
        if SetMapLocalizationRequest is not None:
            self._set_map_localization_pub = rospy.Publisher(
                self._set_map_localization_topic, SetMapLocalizationRequest, queue_size=2
            )

        self.wheel_cmd_pub = rospy.Publisher("/chassis/wheel_speed_cmd", WheelSpeedCommand, queue_size=10)
        self.disc_speed_pub = rospy.Publisher("/chassis/disc_speed_cmd", Int16, queue_size=10)
        self.disc_enable_pub = rospy.Publisher("/chassis/disc_enable_cmd", Bool, queue_size=10)
        self.work_mode_pub = rospy.Publisher("/chassis/work_mode_cmd", UInt16, queue_size=10)
        self.disc_lift_pub = rospy.Publisher("/chassis/disc_lift_cmd", UInt16, queue_size=10)
        self.light_pub = rospy.Publisher("/chassis/light_cmd", Bool, queue_size=10)

        rospy.Subscriber("/chassis/status", ChassisStatus, self._chassis_status_callback, queue_size=10)
        rospy.Service("~plan_now", Trigger, self._handle_plan_now)

        self.enable_service = rospy.ServiceProxy("/chassis/enable", EnableChassis)

        self.sl_link_server = SlLinkAServer(
            sdk_dir=_resolve_runtime_path(
                rospy.get_param("~sl_linka_python_sdk_dir", "third_party/sl_linka/sdk/python"),
                self._runtime_base_dir,
            ),
            host=rospy.get_param("~sl_linka_host", "0.0.0.0"),
            port=rospy.get_param("~sl_linka_port", 8002),
            callback_handler=self,
        )
        self.sl_link_server.start()

        tick_hz = max(1.0, float(rospy.get_param("~scheduler_tick_hz", 5.0)))
        stream_push_hz = max(5.0, float(rospy.get_param("~stream_push_hz", 20.0)))
        self.timer = rospy.Timer(rospy.Duration(1.0 / tick_hz), self._tick)
        self.stream_timer = rospy.Timer(rospy.Duration(1.0 / stream_push_hz), self._stream_tick)
        plan_pub_hz = max(0.2, float(rospy.get_param("~global_plan_publish_hz", 1.0)))
        self.global_plan_timer = rospy.Timer(rospy.Duration(1.0 / plan_pub_hz), self._publish_global_plan_tick)
        # Default: do not allow chassis to consume /cmd_vel until task starts.
        self.task_enable_pub.publish(Bool(data=False))

    def _set_cmd_vel_forward_runtime_active(self, enabled, publish_zero=False, reason=""):
        # Compatibility wrapper: runtime task control now uses /chassis/task_enable.
        enabled = bool(enabled)
        changed = (self._task_enable_runtime_active != enabled)
        if changed:
            self._task_enable_runtime_active = enabled
            self.task_enable_pub.publish(Bool(data=enabled))
            rospy.loginfo(
                "task_enable runtime %s%s",
                "enabled" if enabled else "disabled",
                (" reason={}".format(reason) if reason else ""),
            )

    def _stream_tick(self, _event):
        left, right, left_stamp, right_stamp = self.aurora_bridge.get_latest_frames()
        now = rospy.Time.now()
        max_age = rospy.Duration.from_sec(self._local_rtsp_max_frame_age)
        if left is not None and left_stamp and left_stamp != rospy.Time(0):
            if now > left_stamp and (now - left_stamp) > max_age:
                rospy.logwarn_throttle(
                    2.0,
                    "Drop stale left frame for RTSP: age=%.3fs (max=%.3fs)",
                    (now - left_stamp).to_sec(),
                    self._local_rtsp_max_frame_age,
                )
                left = None
        if right is not None and right_stamp and right_stamp != rospy.Time(0):
            if now > right_stamp and (now - right_stamp) > max_age:
                rospy.logwarn_throttle(
                    2.0,
                    "Drop stale right frame for RTSP: age=%.3fs (max=%.3fs)",
                    (now - right_stamp).to_sec(),
                    self._local_rtsp_max_frame_age,
                )
                right = None
        if left is not None:
            self.local_stream_server.push_frame("left", left)
        if right is not None:
            self.local_stream_server.push_frame("right", right)

    def _publish_global_plan_tick(self, _event):
        try:
            if self.current_path is None or self.current_path.nav_path is None or not self.current_path.nav_path.poses:
                return
            self.global_plan_pub.publish(self._build_navigation_path_for_move_base())
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to publish global plan periodically: %s", exc)

    def _publish_path_to_navigation(self, publish_goal=False, reason=""):
        try:
            if self.current_path is None or self.current_path.nav_path is None or not self.current_path.nav_path.poses:
                return
            msg = self._build_navigation_path_for_move_base()
            self.global_plan_pub.publish(msg)
            if publish_goal:
                self._publish_path_endpoint_goal(reason=reason or "sync_with_global_plan")
            rospy.loginfo_throttle(2.0, "Published planned path to navigation: points=%d", len(msg.poses))
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to publish path to navigation: %s", exc)

    def _navigation_alignment_yaw(self):
        if not self._live_map_align_to_initial_yaw:
            return None
        yaw = self._lookup_live_map_alignment_yaw()
        if yaw is None:
            return None
        return float(yaw)

    @staticmethod
    def _yaw_from_quaternion(quat):
        try:
            x = float(quat.get("x", 0.0))
            y = float(quat.get("y", 0.0))
            z = float(quat.get("z", 0.0))
            w = float(quat.get("w", 1.0))
        except Exception:
            return 0.0
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    def _quaternion_to_navigation_frame(self, quat, alignment_yaw):
        if alignment_yaw is None:
            return quat
        return self._yaw_to_quaternion(self._yaw_from_quaternion(quat) + float(alignment_yaw))

    def _point_to_navigation_frame(self, x, y, alignment_yaw):
        if alignment_yaw is None:
            return float(x), float(y)
        return self._transform_point_by_yaw(x, y, float(alignment_yaw))

    def _build_navigation_path_for_move_base(self):
        nav_path = Path()
        if self.current_path is None:
            return nav_path
        alignment_yaw = self._navigation_alignment_yaw()
        source_frame = (
            self.current_path.nav_path.header.frame_id
            if self.current_path.nav_path is not None and self.current_path.nav_path.header.frame_id
            else self._live_map_source_frame
        )
        nav_path.header.frame_id = self._live_map_aligned_frame if alignment_yaw is not None else source_frame
        nav_path.header.stamp = rospy.Time.now()
        points = list(self.current_path.points or [])
        cached_xy = [(float(p.get("x", 0.0)), float(p.get("y", 0.0))) for p in points]
        for index, point in enumerate(points):
            raw_x = float(point.get("x", 0.0))
            raw_y = float(point.get("y", 0.0))
            nav_x, nav_y = self._point_to_navigation_frame(raw_x, raw_y, alignment_yaw)
            quat = self._resolve_point_orientation(point, index, cached_xy)
            quat = self._quaternion_to_navigation_frame(quat, alignment_yaw)
            pose = PoseStamped()
            pose.header = nav_path.header
            pose.pose.position.x = float(nav_x)
            pose.pose.position.y = float(nav_y)
            pose.pose.orientation.x = float(quat["x"])
            pose.pose.orientation.y = float(quat["y"])
            pose.pose.orientation.z = float(quat["z"])
            pose.pose.orientation.w = float(quat["w"])
            nav_path.poses.append(pose)
        return nav_path

    def _build_navigation_goal_msg(self, point, index, quat=None):
        alignment_yaw = self._navigation_alignment_yaw()
        source_frame = (
            self.current_path.nav_path.header.frame_id
            if self.current_path is not None
            and self.current_path.nav_path is not None
            and self.current_path.nav_path.header.frame_id
            else self._live_map_source_frame
        )
        if quat is None:
            cached_xy = [(float(p.get("x", 0.0)), float(p.get("y", 0.0))) for p in self.current_path.points]
            quat = self._resolve_point_orientation(point, index, cached_xy)
        nav_x, nav_y = self._point_to_navigation_frame(
            float(point.get("x", 0.0)),
            float(point.get("y", 0.0)),
            alignment_yaw,
        )
        quat = self._quaternion_to_navigation_frame(quat, alignment_yaw)
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self._live_map_aligned_frame if alignment_yaw is not None else source_frame
        msg.pose.position.x = float(nav_x)
        msg.pose.position.y = float(nav_y)
        msg.pose.orientation.x = float(quat["x"])
        msg.pose.orientation.y = float(quat["y"])
        msg.pose.orientation.z = float(quat["z"])
        msg.pose.orientation.w = float(quat["w"])
        return msg

    def _publish_path_endpoint_goal(self, reason=""):
        if self.current_path is None or not self.current_path.points:
            return
        endpoint_index = len(self.current_path.points) - 1
        target_index = endpoint_index
        try:
            pose = self.aurora_bridge.get_pose() or {}
            rx = float(pose.get("x", 0.0))
            ry = float(pose.get("y", 0.0))
            nearest_index = 0
            nearest_distance = float("inf")
            for idx, point in enumerate(self.current_path.points):
                dist = math.hypot(float(point.get("x", 0.0)) - rx, float(point.get("y", 0.0)) - ry)
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_index = idx
            # Keep cursor in sync for status/progress logic.
            self.current_path_index = nearest_index
            target_index = self._select_precomputed_goal_index(nearest_index)
        except Exception:
            target_index = endpoint_index
        endpoint = self.current_path.points[target_index]
        cached_xy = [(float(p.get("x", 0.0)), float(p.get("y", 0.0))) for p in self.current_path.points]
        quat = self._resolve_point_orientation(endpoint, target_index, cached_xy)
        self.goal_pub.publish(self._build_navigation_goal_msg(endpoint, target_index, quat))

    # Backward compatibility for older internal calls; keeps behavior periodic.
    def _publish_path_endpoint_goal_once(self, reason=""):
        self._publish_path_endpoint_goal(reason=reason)

    def _select_precomputed_goal_index(self, nearest_index):
        if not self._goal_points:
            return self._resolve_straight_segment_end_index(nearest_index)
        for item in self._goal_points:
            idx = int(item.get("path_index", 0))
            if idx >= int(nearest_index):
                return idx
        return int(self._goal_points[-1].get("path_index", 0))

    def _tick(self, _event):
        raw_map = self.aurora_bridge.get_map()
        if raw_map is not None:
            self.map_service.set_raw_map(raw_map)
            current_map_id = self._current_map_id()
            if current_map_id != self._last_seen_map_id:
                self._last_seen_map_id = current_map_id
                self._sync_task_map_binding(update_binding=False)
                self._sync_task_regions_from_overlay()
                rospy.loginfo(
                    "Map switched, loaded task-map binding: map_id=%s task_id=%s selected_regions=%s",
                    self.task_config.map_id or "<empty>",
                    self.task_config.task_id or "<empty>",
                    ",".join(self.task_config.selected_work_region_ids or []) or "<none>",
                )
            self._save_initial_map_preview_once()
            self._update_live_preview(raw_map)
            self._update_live_map_files(raw_map)

        if self.replan_requested and self.state == SchedulerState.RUNNING:
            self._safe_stop_motion()
            if self._plan_current_task():
                self.replan_requested = False
                self._resume_execution()

        self._tick_path_execution()
        self._update_progress()
        self._publish_status()
        self._publish_diagnostics()

    def _save_initial_map_preview_once(self):
        if self._initial_map_preview_saved:
            return
        try:
            snapshot = self.map_service.create_preview(
                self.aurora_bridge.get_pose(),
                self._initial_map_preview_max_edge,
                self._initial_map_preview_format,
                True,
                **self._map_preview_alignment_kwargs()
            )
            os.makedirs(self._initial_map_preview_dir, exist_ok=True)
            preview_width, preview_height, shrink_factor = self._preview_meta(
                snapshot.width, snapshot.height, self._initial_map_preview_max_edge
            )
            filename = (
                "aurora_map_preview"
                "_s{}"
                "_res{}"
                "_ox{}"
                "_oy{}"
                "_ow{}"
                "_oh{}"
                "_pw{}"
                "_ph{}"
                "_v{}"
                ".{}"
            ).format(
                self._safe_num(shrink_factor),
                self._safe_num(snapshot.resolution),
                self._safe_num(snapshot.origin_x),
                self._safe_num(snapshot.origin_y),
                snapshot.width,
                snapshot.height,
                preview_width,
                preview_height,
                snapshot.map_version,
                snapshot.preview_format,
            )
            full_path = os.path.join(self._initial_map_preview_dir, filename)
            with open(full_path, "wb") as handle:
                handle.write(snapshot.preview_data)
            self._initial_map_preview_saved = True
            rospy.loginfo("Saved initial map preview to %s", full_path)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to save initial map preview: %s", exc)

    def _preview_meta(self, orig_w, orig_h, max_edge):
        max_edge = max(64.0, float(max_edge))
        max_wh = float(max(orig_w, orig_h))
        scale = min(max_edge / max_wh, 1.0)
        preview_w = max(1, int(round(float(orig_w) * scale)))
        preview_h = max(1, int(round(float(orig_h) * scale)))
        shrink_factor = (max_wh / float(max(preview_w, preview_h))) if scale < 1.0 else 1.0
        return preview_w, preview_h, shrink_factor

    @staticmethod
    def _apply_response_map_info(response, map_info):
        if not isinstance(map_info, dict):
            return
        response.width = int(map_info.get("width", 0))
        response.height = int(map_info.get("height", 0))
        response.resolution = float(map_info.get("resolution", 0.0))
        response.origin.x = float(map_info.get("origin_x", 0.0))
        response.origin.y = float(map_info.get("origin_y", 0.0))
        response.origin.heading_deg = 0.0
        response.frame_id = str(map_info.get("frame_id", ""))

    def _load_robot_config_from_params(self):
        self.task_config.vehicle_width = max(
            0.1, float(rospy.get_param("~vehicle_width", self.task_config.vehicle_width))
        )
        self.task_config.vehicle_length = max(
            0.1, float(rospy.get_param("~vehicle_length", self.task_config.vehicle_length))
        )
        self.task_config.default_path_spacing = max(
            0.2, float(rospy.get_param("~default_path_spacing", self.task_config.default_path_spacing))
        )
        self.task_config.turn_radius = max(
            0.1, float(rospy.get_param("~turn_radius", self.task_config.turn_radius))
        )
        self.task_config.overlap_ratio = max(
            0.0, min(0.95, float(rospy.get_param("~overlap_ratio", self.task_config.overlap_ratio)))
        )
        self.task_config.inflation_radius = max(
            0.0, float(rospy.get_param("~inflation_radius", self.task_config.inflation_radius))
        )

    def _sync_robot_config_to_yaml(self):
        path = self._robot_config_yaml_path
        if not path:
            return
        keys = {
            "vehicle_width": float(self.task_config.vehicle_width),
            "vehicle_length": float(self.task_config.vehicle_length),
            "default_path_spacing": float(self.task_config.default_path_spacing),
            "turn_radius": float(self.task_config.turn_radius),
            "overlap_ratio": float(self.task_config.overlap_ratio),
            "inflation_radius": float(self.task_config.inflation_radius),
        }

        def _fmt(value):
            text = "{:.6f}".format(float(value)).rstrip("0").rstrip(".")
            return text if text else "0"

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        content = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        for key, value in keys.items():
            pattern = r"^(\s*" + re.escape(key) + r"\s*:\s*).*$"
            if re.search(pattern, content, flags=re.MULTILINE):
                # Use callable replacement to avoid backreference ambiguity like "\10.5".
                content = re.sub(
                    pattern,
                    lambda m, v=_fmt(value): "{}{}".format(m.group(1), v),
                    content,
                    flags=re.MULTILINE,
                )
            else:
                if content and not content.endswith("\n"):
                    content += "\n"
                content += "{}: {}\n".format(key, _fmt(value))
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_path, path)

    def _reload_robot_config_from_yaml(self):
        path = self._robot_config_yaml_path
        if not path or (not os.path.exists(path)):
            return False

        values = {}
        with open(path, "r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if (not line) or line.startswith("#") or (":" not in line):
                    continue
                key, value = line.split(":", 1)
                key = key.strip()
                if key not in (
                    "vehicle_width",
                    "vehicle_length",
                    "default_path_spacing",
                    "turn_radius",
                    "overlap_ratio",
                    "inflation_radius",
                ):
                    continue
                token = value.split("#", 1)[0].strip()
                if not token:
                    continue
                try:
                    values[key] = float(token)
                except Exception:
                    continue

        if not values:
            return False

        if "vehicle_width" in values:
            self.task_config.vehicle_width = max(0.1, float(values["vehicle_width"]))
        if "vehicle_length" in values:
            self.task_config.vehicle_length = max(0.1, float(values["vehicle_length"]))
        if "default_path_spacing" in values:
            self.task_config.default_path_spacing = max(0.2, float(values["default_path_spacing"]))
        if "turn_radius" in values:
            self.task_config.turn_radius = max(0.1, float(values["turn_radius"]))
        if "overlap_ratio" in values:
            self.task_config.overlap_ratio = max(0.0, min(0.95, float(values["overlap_ratio"])))
        if "inflation_radius" in values:
            self.task_config.inflation_radius = max(0.0, float(values["inflation_radius"]))
        return True

    def _safe_num(self, value):
        text = "{:.4f}".format(float(value)).rstrip("0").rstrip(".")
        if text == "-0":
            text = "0"
        return text.replace("-", "m").replace(".", "p")

    def _update_live_preview(self, raw_map):
        if not self._live_preview_enabled:
            return
        now = time.time()
        if now < self._live_preview_next_time:
            return
        self._live_preview_next_time = now + (1.0 / self._live_preview_hz)
        try:
            snapshot = self.map_service.create_preview(
                self.aurora_bridge.get_pose(),
                self._live_preview_max_edge,
                self._live_preview_format,
                True,
                **self._map_preview_alignment_kwargs()
            )
            os.makedirs(os.path.dirname(self._live_preview_file) or ".", exist_ok=True)
            tmp_path = self._live_preview_file + ".tmp"
            with open(tmp_path, "wb") as handle:
                handle.write(snapshot.preview_data)
            os.replace(tmp_path, self._live_preview_file)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to update live map preview: %s", exc)

    def _update_live_map_files(self, raw_map):
        if not self._live_map_enabled:
            return
        now = time.time()
        if now < self._live_map_next_time:
            return
        self._live_map_next_time = now + (1.0 / self._live_map_hz)
        try:
            map_info = self.map_service.get_map_info()
            composed_map = self.map_service.compose_map()
            if map_info is not None and composed_map is not None:
                self._export_runtime_map(
                    raw_map,
                    self._live_map_dir,
                    self._live_map_yaml_name,
                    self._live_map_image_name,
                    grid_override=composed_map,
                    map_info_override=map_info,
                )
            else:
                self._export_runtime_map(raw_map, self._live_map_dir, self._live_map_yaml_name, self._live_map_image_name)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to export live map files: %s", exc)

    def _export_runtime_map(self, raw_map, out_dir, yaml_name, image_name, grid_override=None, map_info_override=None):
        os.makedirs(out_dir, exist_ok=True)
        if grid_override is not None and map_info_override is not None:
            width = int(map_info_override["width"])
            height = int(map_info_override["height"])
            grid = np.array(grid_override, dtype=np.int16).reshape((height, width))
            origin_x = float(map_info_override["origin_x"])
            origin_y = float(map_info_override["origin_y"])
            resolution = float(map_info_override["resolution"])
            map_version = int(map_info_override.get("map_version", -1))
        else:
            info = raw_map.info
            width = int(info.width)
            height = int(info.height)
            grid = np.array(raw_map.data, dtype=np.int16).reshape((height, width))
            origin_x = float(info.origin.position.x)
            origin_y = float(info.origin.position.y)
            resolution = float(info.resolution)
            map_version = -1

        if (
            self._live_map_align_to_initial_yaw
            and self._tf_buffer is not None
            and euler_from_quaternion is not None
            and width > 0
            and height > 0
        ):
            yaw = self._lookup_live_map_alignment_yaw()
            if yaw is not None and abs(float(yaw)) > 1e-6:
                cache_hit = (
                    self._live_map_last_rotated_grid is not None
                    and self._live_map_last_rotated_origin is not None
                    and map_version >= 0
                    and self._live_map_last_rotated_version == map_version
                    and self._live_map_last_rotated_yaw is not None
                    and abs(float(self._live_map_last_rotated_yaw) - float(yaw)) < 1e-9
                )
                if cache_hit:
                    grid = self._live_map_last_rotated_grid
                    origin_x, origin_y = self._live_map_last_rotated_origin
                    height, width = grid.shape[:2]
                else:
                    grid, origin_x, origin_y = self._rotate_grid_to_aligned_frame(
                        grid, origin_x, origin_y, resolution, float(yaw)
                    )
                    height, width = grid.shape[:2]
                    self._live_map_last_rotated_version = map_version
                    self._live_map_last_rotated_yaw = float(yaw)
                    self._live_map_last_rotated_grid = grid
                    self._live_map_last_rotated_origin = (float(origin_x), float(origin_y))

        if self._live_map_crop_to_free_space and width > 0 and height > 0:
            free_rows, free_cols = np.where(grid == 0)
            if free_rows.size > 0 and free_cols.size > 0:
                margin_cells = int(round(self._live_map_crop_margin_m / max(resolution, 1e-6)))
                min_row = max(0, int(free_rows.min()) - margin_cells)
                max_row = min(height - 1, int(free_rows.max()) + margin_cells)
                min_col = max(0, int(free_cols.min()) - margin_cells)
                max_col = min(width - 1, int(free_cols.max()) + margin_cells)
                grid = grid[min_row:max_row + 1, min_col:max_col + 1]
                height, width = grid.shape[:2]
                origin_x += float(min_col) * resolution
                origin_y += float(min_row) * resolution
                rospy.loginfo_throttle(
                    5.0,
                    "Live map cropped to free-space bbox: size=%dx%d margin=%.2fm",
                    width,
                    height,
                    self._live_map_crop_margin_m,
                )
        image = np.full((height, width), 205, dtype=np.uint8)
        image[grid == 0] = 254
        image[grid >= 100] = 0
        image = np.flipud(image)

        image_path = os.path.join(out_dir, image_name)
        yaml_path = os.path.join(out_dir, yaml_name)
        if not cv2.imwrite(image_path, image):
            raise RuntimeError("Failed to write map image: {}".format(image_path))
        yaml_text = "\n".join(
            [
                "image: {}".format(image_name),
                "resolution: {:.6f}".format(resolution),
                "origin: [{:.6f}, {:.6f}, 0.000000]".format(origin_x, origin_y),
                "negate: 0",
                "occupied_thresh: 0.65",
                "free_thresh: 0.196",
                "",
            ]
        )
        tmp_yaml = yaml_path + ".tmp"
        with open(tmp_yaml, "w", encoding="utf-8") as handle:
            handle.write(yaml_text)
        os.replace(tmp_yaml, yaml_path)
        return yaml_path, image_path

    def _lookup_live_map_alignment_yaw(self):
        if self._tf_buffer is not None:
            try:
                transform = self._tf_buffer.lookup_transform(
                    self._live_map_aligned_frame,
                    self._live_map_source_frame,
                    rospy.Time(0),
                    rospy.Duration(self._live_map_align_yaw_timeout),
                )
                q = transform.transform.rotation
                _, _, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
                if math.isfinite(float(yaw)):
                    return float(yaw)
            except Exception as exc:
                rospy.logwarn_throttle(2.0, "Failed to lookup live map alignment yaw: %s", exc)
        return self._initial_pose_alignment_yaw_from_pose(self.aurora_bridge.get_initial_pose())

    def _initial_pose_alignment_yaw_from_pose(self, pose):
        if self._initial_pose_alignment_yaw is not None:
            return self._initial_pose_alignment_yaw
        if not isinstance(pose, dict) or "orientation" not in pose:
            return None
        try:
            heading_deg = float(pose.get("heading_deg", 0.0))
        except Exception:
            return None
        if not math.isfinite(heading_deg):
            return None
        self._initial_pose_alignment_yaw = -math.radians(heading_deg)
        rospy.loginfo("Map preview yaw alignment initialized from odom: %.6f rad", self._initial_pose_alignment_yaw)
        return self._initial_pose_alignment_yaw

    def _map_preview_alignment_kwargs(self):
        if not self._live_map_align_to_initial_yaw:
            return {}
        yaw = self._lookup_live_map_alignment_yaw()
        if yaw is None:
            return {}
        return {
            "alignment_yaw": yaw,
            "aligned_frame_id": self._live_map_aligned_frame,
        }

    @staticmethod
    def _transform_point_by_yaw(point_x, point_y, yaw):
        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)
        return (
            cos_yaw * float(point_x) - sin_yaw * float(point_y),
            sin_yaw * float(point_x) + cos_yaw * float(point_y),
        )

    def _point_from_aligned_to_source_map(self, point, alignment_yaw):
        source_x, source_y = self._transform_point_by_yaw(
            point.get("x", 0.0),
            point.get("y", 0.0),
            -float(alignment_yaw),
        )
        return {"x": source_x, "y": source_y}

    def _points_from_aligned_to_source_map(self, points, alignment_yaw):
        if not points:
            return []
        return [self._point_from_aligned_to_source_map(point, alignment_yaw) for point in points]

    def _pose_from_aligned_to_source_map(self, pose, alignment_yaw):
        if not isinstance(pose, dict) or not pose:
            return {}
        source_x, source_y = self._transform_point_by_yaw(
            pose.get("x", 0.0),
            pose.get("y", 0.0),
            -float(alignment_yaw),
        )
        source_pose = dict(pose)
        source_pose["x"] = source_x
        source_pose["y"] = source_y
        try:
            source_pose["heading_deg"] = float(pose.get("heading_deg", 0.0)) - math.degrees(float(alignment_yaw))
        except Exception:
            source_pose["heading_deg"] = 0.0
        return source_pose

    def _map_point_to_render_frame(self, point, render_map_info):
        try:
            point_x = float(point.get("x", 0.0))
            point_y = float(point.get("y", 0.0))
        except Exception:
            point_x = 0.0
            point_y = 0.0
        try:
            alignment_yaw = render_map_info.get("alignment_yaw", None)
            if alignment_yaw is not None:
                yaw = float(alignment_yaw)
                if math.isfinite(yaw) and abs(yaw) > 1e-6:
                    point_x, point_y = self._transform_point_by_yaw(point_x, point_y, yaw)
        except Exception:
            pass
        return point_x, point_y

    def _map_point_to_preview_pixel(self, point, render_map_info, scale_x, scale_y, preview_w, preview_h):
        point_x, point_y = self._map_point_to_render_frame(point, render_map_info)
        resolution = max(float(render_map_info["resolution"]), 1e-6)
        col = (point_x - float(render_map_info["origin_x"])) / resolution
        row = (point_y - float(render_map_info["origin_y"])) / resolution
        row = float(render_map_info["height"] - 1) - row
        pixel_x = int(round(col * float(scale_x)))
        pixel_y = int(round(row * float(scale_y)))
        pixel_x = max(0, min(int(preview_w) - 1, pixel_x))
        pixel_y = max(0, min(int(preview_h) - 1, pixel_y))
        return pixel_x, pixel_y

    @staticmethod
    def _rotate_grid_to_aligned_frame(grid, origin_x, origin_y, resolution, yaw):
        height, width = grid.shape[:2]
        if height <= 0 or width <= 0:
            return grid, origin_x, origin_y
        if abs(float(yaw)) <= 1e-12:
            return grid, origin_x, origin_y

        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)
        rot = np.array([[cos_yaw, -sin_yaw], [sin_yaw, cos_yaw]], dtype=np.float64)

        x0 = float(origin_x)
        y0 = float(origin_y)
        x1 = x0 + float(width) * float(resolution)
        y1 = y0 + float(height) * float(resolution)
        corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]], dtype=np.float64)
        rotated = corners @ rot.T

        min_x = float(rotated[:, 0].min())
        max_x = float(rotated[:, 0].max())
        min_y = float(rotated[:, 1].min())
        max_y = float(rotated[:, 1].max())

        out_width = max(1, int(math.ceil((max_x - min_x) / max(float(resolution), 1e-12))))
        out_height = max(1, int(math.ceil((max_y - min_y) / max(float(resolution), 1e-12))))

        cols = np.arange(out_width, dtype=np.float64)
        rows = np.arange(out_height, dtype=np.float64)
        x_aligned = min_x + (cols + 0.5) * float(resolution)
        y_aligned = min_y + (rows + 0.5) * float(resolution)

        xx, yy = np.meshgrid(x_aligned, y_aligned)
        # Inverse rotation: map = R(-yaw) * aligned.
        x_map = cos_yaw * xx + sin_yaw * yy
        y_map = -sin_yaw * xx + cos_yaw * yy

        src_col = np.floor((x_map - x0) / max(float(resolution), 1e-12)).astype(np.int64)
        src_row = np.floor((y_map - y0) / max(float(resolution), 1e-12)).astype(np.int64)

        valid = (
            (src_col >= 0)
            & (src_col < int(width))
            & (src_row >= 0)
            & (src_row < int(height))
        )
        out_grid = np.full((out_height, out_width), -1, dtype=np.int16)
        if int(np.count_nonzero(valid)) > 0:
            out_grid[valid] = grid[src_row[valid], src_col[valid]]

        return out_grid, float(min_x), float(min_y)

    def _reload_navigation_map(self, yaml_path):
        try:
            if self._change_map_proxy is None:
                self._change_map_proxy = rospy.ServiceProxy(self._change_map_service, LoadMap)
            response = self._change_map_proxy(map_url=yaml_path)
            result_code = int(response.result)
            return result_code == 0, result_code
        except Exception as exc:
            rospy.logwarn("Failed to reload navigation map via %s: %s", self._change_map_service, exc)
            return False, None

    def _ensure_sync_proxies(self):
        if SyncGetStcm is None or SyncSetStcm is None:
            raise RuntimeError("slamware_ros_sdk python services are unavailable")
        if self._sync_get_proxy is None:
            self._sync_get_proxy = rospy.ServiceProxy(self._sync_get_stcm_service, SyncGetStcm)
        if self._sync_set_proxy is None:
            self._sync_set_proxy = rospy.ServiceProxy(self._sync_set_stcm_service, SyncSetStcm)

    def _map_state_dirname(self, map_id):
        text = str(map_id or "").strip() or self._live_map_id
        safe = re.sub(r"[^0-9A-Za-z._-]", "_", text)
        safe = safe.strip("._") or "LIVE_MAP"
        return safe[:96]

    def _map_state_dir(self, map_id=None):
        effective = self._current_map_id() if map_id is None else map_id
        return os.path.join(self._persist_state_dir, "map_states", self._map_state_dirname(effective))

    def _remove_map_overlay_state_for_map(self, map_id):
        if not self._persist_state_enabled:
            return False
        target_dir = self._map_state_dir(map_id)
        if not os.path.isdir(target_dir):
            return False
        try:
            shutil.rmtree(target_dir)
            rospy.loginfo("Removed map overlay state: map_id=%s dir=%s", map_id, target_dir)
            return True
        except Exception as exc:
            rospy.logwarn("Failed to remove map overlay state for map_id=%s dir=%s: %s", map_id, target_dir, exc)
            return False

    def _clear_live_map_files(self):
        target_dir = os.path.abspath(str(self._live_map_dir or "").strip())
        if not target_dir:
            raise RuntimeError("live_map_dir is empty")
        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)
        rospy.loginfo("Cleared LIVE_MAP files dir: %s", target_dir)

    def _save_map_overlay_state_for_map(self, map_id):
        if not self._persist_state_enabled:
            return
        try:
            target_dir = self._map_state_dir(map_id)
            os.makedirs(target_dir, exist_ok=True)
            self.map_service.save_local_state(target_dir)
        except Exception as exc:
            rospy.logwarn("Failed to save overlay state for map_id=%s: %s", map_id, exc)

    def _copy_map_overlay_state(self, src_map_id, dst_map_id, overwrite=True):
        if not self._persist_state_enabled:
            return False
        src_dir = self._map_state_dir(src_map_id)
        dst_dir = self._map_state_dir(dst_map_id)
        if not os.path.isdir(src_dir):
            return False
        try:
            if overwrite and os.path.isdir(dst_dir):
                shutil.rmtree(dst_dir)
            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=overwrite)
            rospy.loginfo(
                "Copied map overlay state: %s -> %s",
                str(src_map_id),
                str(dst_map_id),
            )
            return True
        except Exception as exc:
            rospy.logwarn(
                "Failed to copy map overlay state: %s -> %s, err=%s",
                str(src_map_id),
                str(dst_map_id),
                str(exc),
            )
            return False

    def _load_map_overlay_state_for_map(self, map_id):
        if not self._persist_state_enabled:
            return False
        target_dir = self._map_state_dir(map_id)
        loaded = False
        try:
            loaded = bool(self.map_service.load_local_state(target_dir))
        except Exception:
            loaded = False
        if loaded:
            rospy.loginfo("Loaded map overlay state: map_id=%s dir=%s", map_id, target_dir)
            return True
        # one-time compatibility: fallback to legacy single-file overlay state
        legacy_meta = os.path.join(self._persist_state_dir, "map_overlay_state.json")
        if os.path.exists(legacy_meta):
            try:
                legacy_loaded = bool(self.map_service.load_local_state(self._persist_state_dir))
            except Exception:
                legacy_loaded = False
            if legacy_loaded:
                self._save_map_overlay_state_for_map(map_id)
                rospy.loginfo(
                    "Migrated legacy overlay state into map-specific state: map_id=%s dir=%s",
                    map_id,
                    target_dir,
                )
                return True
        self.map_service.reset_local_state()
        rospy.loginfo("No overlay state for map_id=%s, reset to empty overlay", map_id)
        return False

    def _save_local_state(self):
        if not self._persist_state_enabled:
            return
        try:
            os.makedirs(self._persist_state_dir, exist_ok=True)
            self._save_map_overlay_state_for_map(self._current_map_id())
            self._save_map_registry_state()
            self._save_task_registry_state()
            payload = {
                "chassis_settings": dict(self._chassis_settings),
                "active_map_id": self._current_map_id(),
                "state": self.state.value,
                "replan_requested": bool(self.replan_requested),
                "saved_at": int(time.time()),
                "persist_runtime_task_state": bool(self._persist_runtime_task_state),
            }
            if self._persist_runtime_task_state:
                payload["task_config"] = asdict(self.task_config)
                payload["task_bindings"] = dict(self._task_bindings)
                payload["current_path"] = None
            if self._persist_runtime_task_state and self.current_path is not None:
                payload["current_path"] = {
                    "task_id": self.current_path.task_id,
                    "path_version": int(self.current_path.path_version),
                    "length_m": float(self.current_path.length_m),
                    "points": self.current_path.points,
                    "frame_id": self.current_path.nav_path.header.frame_id if self.current_path.nav_path is not None else "map",
                }
            tmp_path = os.path.join(self._persist_state_dir, "scheduler_state.json.tmp")
            final_path = os.path.join(self._persist_state_dir, "scheduler_state.json")
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_path, final_path)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to save scheduler local state: %s", exc)

    def _load_local_state(self):
        if not self._persist_state_enabled:
            return
        try:
            os.makedirs(self._persist_state_dir, exist_ok=True)
            state_path = os.path.join(self._persist_state_dir, "scheduler_state.json")
            self._load_map_registry_state()
            if not os.path.exists(state_path):
                self.task_config.map_id = self._current_map_id()
                self._load_map_overlay_state_for_map(self._current_map_id())
                return
            with open(state_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if (not self._map_registry) and isinstance(payload.get("map_registry", {}), dict):
                # Backward compatibility: migrate old embedded map_registry.
                self._map_registry = payload.get("map_registry", {})
                self._save_map_registry_state()
            loaded_chassis = payload.get("chassis_settings", {})
            if isinstance(loaded_chassis, dict):
                self._chassis_settings["work_mode"] = int(loaded_chassis.get("work_mode", self._chassis_settings["work_mode"]))
                self._chassis_settings["disc_speed_rpm"] = int(loaded_chassis.get("disc_speed_rpm", self._chassis_settings["disc_speed_rpm"]))
                self._chassis_settings["run_speed"] = float(loaded_chassis.get("run_speed", self._chassis_settings["run_speed"]))
            saved_active_map_id = str(payload.get("active_map_id", "")).strip()
            if saved_active_map_id:
                self._active_map_id = saved_active_map_id
            self._task_bindings = {}
            self.current_path = None
            self.current_path_index = 0
            if self._persist_runtime_task_state:
                self._task_bindings = payload.get("task_bindings", {}) if isinstance(payload.get("task_bindings", {}), dict) else {}
                task_cfg = payload.get("task_config", {})
                self.task_config = TaskConfigModel(
                    task_id=task_cfg.get("task_id", ""),
                    map_id=task_cfg.get("map_id", ""),
                    work_regions=task_cfg.get("work_regions", []),
                    obstacle_regions=task_cfg.get("obstacle_regions", []),
                    erase_regions=task_cfg.get("erase_regions", []),
                    crop_region=task_cfg.get("crop_region", {}),
                    active_work_region_id=task_cfg.get("active_work_region_id", ""),
                    selected_work_region_ids=task_cfg.get("selected_work_region_ids", []),
                    region_repeat_config=task_cfg.get("region_repeat_config", {}),
                    vehicle_width=self.task_config.vehicle_width,
                    vehicle_length=self.task_config.vehicle_length,
                    default_path_spacing=self.task_config.default_path_spacing,
                    global_direction=str(task_cfg.get("global_direction", "x") or "x"),
                    turn_radius=self.task_config.turn_radius,
                    overlap_ratio=self.task_config.overlap_ratio,
                    inflation_radius=self.task_config.inflation_radius,
                )
                cfg_map_id = str(self.task_config.map_id or "").strip()
                if cfg_map_id:
                    self._active_map_id = cfg_map_id
            self._load_task_registry_state()
            self.task_config.map_id = self._current_map_id()
            self._load_map_overlay_state_for_map(self._current_map_id())
            if self._persist_runtime_task_state:
                self._sync_task_map_binding(update_binding=False)
            self.replan_requested = bool(payload.get("replan_requested", False))

            path_payload = payload.get("current_path")
            if self._persist_runtime_task_state and path_payload and path_payload.get("points"):
                nav_path = self._build_nav_path_from_points(path_payload.get("points", []), path_payload.get("frame_id", "map"))
                self.current_path = PlannerPath(
                    task_id=path_payload.get("task_id", self.task_config.task_id or "task"),
                    path_version=int(path_payload.get("path_version", 0)),
                    points=path_payload.get("points", []),
                    nav_path=nav_path,
                    length_m=float(path_payload.get("length_m", 0.0)),
                )
                self.current_path_index = 0
                self._rebuild_goal_points()
            rospy.loginfo("Loaded scheduler local state from %s", self._persist_state_dir)
        except Exception as exc:
            rospy.logwarn("Failed to load scheduler local state: %s", exc)

    def _save_map_registry_state(self):
        if not self._persist_state_enabled:
            return
        try:
            os.makedirs(self._persist_state_dir, exist_ok=True)
            payload = {
                "map_registry": dict(self._map_registry),
                "saved_at": int(time.time()),
            }
            tmp_path = self._map_registry_state_file + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self._map_registry_state_file)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to save map registry state: %s", exc)

    def _save_task_registry_state(self):
        if not self._persist_state_enabled:
            return
        try:
            os.makedirs(self._persist_state_dir, exist_ok=True)
            now_ts = int(time.time())
            by_map = {}
            for _key, record in dict(self._task_bindings or {}).items():
                if not isinstance(record, dict):
                    continue
                map_id = str(record.get("map_id", "") or "").strip()
                task_id = str(record.get("task_id", "") or "").strip()
                if not map_id:
                    continue
                item = {
                    "map_id": map_id,
                    "task_id": task_id,
                    "selected_work_region_ids": list(record.get("selected_work_region_ids", []) or []),
                    "region_repeat_config": dict(record.get("region_repeat_config", {}) or {}),
                    "active_work_region_id": str(record.get("active_work_region_id", "") or ""),
                    "updated_at": int(record.get("updated_at", now_ts) or now_ts),
                    "task_result": dict(record.get("task_result", {}) or {}),
                }
                # one map keeps one latest task
                old = by_map.get(map_id)
                if (not isinstance(old, dict)) or int(item["updated_at"]) >= int(old.get("updated_at", 0) or 0):
                    by_map[map_id] = item
            payload = {
                "map_tasks": by_map,
                "saved_at": now_ts,
            }
            tmp_path = self._task_registry_state_file + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self._task_registry_state_file)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Failed to save task registry state: %s", exc)

    def _load_task_registry_state(self):
        if not self._persist_state_enabled:
            return
        try:
            if not os.path.exists(self._task_registry_state_file):
                return
            with open(self._task_registry_state_file, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            map_tasks = payload.get("map_tasks", {}) if isinstance(payload, dict) else {}
            if not isinstance(map_tasks, dict):
                return
            restored = 0
            for map_id, item in map_tasks.items():
                if not isinstance(item, dict):
                    continue
                map_id_text = str(map_id or item.get("map_id", "")).strip()
                task_id_text = str(item.get("task_id", "")).strip() or "task"
                if not map_id_text:
                    continue
                key = "{}::{}".format(map_id_text, task_id_text)
                self._task_bindings[key] = {
                    "task_id": task_id_text,
                    "map_id": map_id_text,
                    "selected_work_region_ids": list(item.get("selected_work_region_ids", []) or []),
                    "region_repeat_config": dict(item.get("region_repeat_config", {}) or {}),
                    "active_work_region_id": str(item.get("active_work_region_id", "") or ""),
                    "updated_at": int(item.get("updated_at", int(time.time())) or int(time.time())),
                    "task_result": dict(item.get("task_result", {}) or {}),
                }
                restored += 1
            if restored > 0:
                rospy.loginfo("Loaded task registry state: %d map-bound tasks", restored)
        except Exception as exc:
            rospy.logwarn("Failed to load task registry state: %s", exc)

    def _load_map_registry_state(self):
        if not self._persist_state_enabled:
            return
        try:
            self._map_registry = {}
            if not os.path.exists(self._map_registry_state_file):
                return
            with open(self._map_registry_state_file, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, dict):
                registry = payload.get("map_registry", {})
                if isinstance(registry, dict):
                    self._map_registry = registry
        except Exception as exc:
            rospy.logwarn("Failed to load map registry state: %s", exc)

    def _build_nav_path_from_points(self, points, frame_id):
        nav_path = Path()
        nav_path.header.frame_id = frame_id or "map"
        cached_xy = []
        for item in points:
            cached_xy.append((float(item.get("x", 0.0)), float(item.get("y", 0.0))))
        for idx, item in enumerate(points):
            pose = PoseStamped()
            pose.header.frame_id = nav_path.header.frame_id
            x, y = cached_xy[idx]
            pose.pose.position.x = x
            pose.pose.position.y = y
            quat = self._resolve_point_orientation(item, idx, cached_xy)
            pose.pose.orientation.x = float(quat["x"])
            pose.pose.orientation.y = float(quat["y"])
            pose.pose.orientation.z = float(quat["z"])
            pose.pose.orientation.w = float(quat["w"])
            nav_path.poses.append(pose)
        return nav_path

    def shutdown(self):
        self._save_local_state()
        self.media_streamer.close()
        self.local_stream_server.stop()
        self.sl_link_server.stop()

    def _chassis_status_callback(self, msg):
        self.last_chassis_status = msg

    def _sync_task_regions_from_overlay(self):
        overlay_regions = self.map_service.get_overlay_regions() or {}
        crop_region = overlay_regions.get("crop_region")
        if isinstance(crop_region, dict) and bool(crop_region.get("enabled", True)):
            points = crop_region.get("points", []) or []
            if len(points) >= 3:
                self.task_config.crop_region = {
                    "region_id": crop_region.get("region_id", "crop_region_1"),
                    "name": crop_region.get("name", "crop_region"),
                    "points": points,
                    "region_type": 4,
                }
            else:
                self.task_config.crop_region = {}
        else:
            self.task_config.crop_region = {}
        self.task_config.work_regions = []
        for item in overlay_regions.get("work_regions", []):
            points = item.get("points", []) or []
            if len(points) < 3:
                continue
            if not bool(item.get("enabled", True)):
                continue
            region_type = int(item.get("region_type", 1))
            if region_type != 1:
                continue
            self.task_config.work_regions.append(
                {
                    "region_id": item.get("region_id", ""),
                    "name": item.get("name", ""),
                    "points": points,
                    "global_direction": str(item.get("global_direction", "x") or "x").strip().lower(),
                    "start_pose": dict(item.get("start_pose", {}) or {}),
                    "end_pose": dict(item.get("end_pose", {}) or {}),
                    "order_index": int(item.get("order_index", 0)),
                    "region_type": region_type,
                }
            )
        self.task_config.obstacle_regions = []
        self.task_config.erase_regions = []
        for item in overlay_regions.get("obstacle_regions", []):
            points = item.get("points", []) or []
            if len(points) < 3:
                continue
            if not bool(item.get("enabled", True)):
                continue
            region_type = int(item.get("region_type", 2))
            normalized = {
                "region_id": item.get("region_id", ""),
                "name": item.get("name", ""),
                "points": points,
                "order_index": int(item.get("order_index", 0)),
                "region_type": region_type,
            }
            if region_type == 3:
                self.task_config.erase_regions.append(normalized)
            elif region_type == 2:
                self.task_config.obstacle_regions.append(normalized)
        valid_region_ids = set()
        for region in self.task_config.work_regions:
            rid = str(region.get("region_id", "")).strip()
            if rid:
                valid_region_ids.add(rid)
        active_id = (self.task_config.active_work_region_id or "").strip()
        if active_id:
            if active_id not in valid_region_ids:
                self.task_config.active_work_region_id = ""
        selected = []
        for rid in list(self.task_config.selected_work_region_ids or []):
            rid_text = str(rid).strip()
            if rid_text and rid_text in valid_region_ids and rid_text not in selected:
                selected.append(rid_text)
        self.task_config.selected_work_region_ids = selected
        repeat_cfg = {}
        for rid, count in dict(self.task_config.region_repeat_config or {}).items():
            rid_text = str(rid).strip()
            if rid_text not in valid_region_ids:
                continue
            try:
                repeat_cfg[rid_text] = max(1, int(count))
            except Exception:
                repeat_cfg[rid_text] = 1
        self.task_config.region_repeat_config = repeat_cfg
        # Enforce single-region planning policy permanently.
        if self._plan_use_all_work_regions:
            self._plan_use_all_work_regions = False
            rospy.logwarn("Forced single-region planning mode: plan_use_all_work_regions=false")
        self._sync_task_map_binding(update_binding=True)

    def _current_map_id(self):
        return str(self._active_map_id or self._live_map_id).strip() or self._live_map_id

    def _set_active_map_id(self, map_id, reason="", migrate_bindings=False):
        next_map_id = str(map_id or "").strip() or self._live_map_id
        prev_map_id = str(self._active_map_id or "").strip() or self._live_map_id
        if next_map_id == prev_map_id:
            self.task_config.map_id = next_map_id
            return

        self._save_map_overlay_state_for_map(prev_map_id)

        if migrate_bindings:
            moved = 0
            prefix = "{}::".format(prev_map_id)
            for key in list(self._task_bindings.keys()):
                key_text = str(key)
                if not key_text.startswith(prefix):
                    continue
                task_id = key_text[len(prefix) :]
                new_key = "{}::{}".format(next_map_id, task_id)
                record = self._task_bindings.pop(key, {})
                if isinstance(record, dict):
                    record["map_id"] = next_map_id
                    self._task_bindings[new_key] = record
                    moved += 1
            if moved > 0:
                rospy.loginfo(
                    "Migrated task-map bindings: count=%d %s -> %s",
                    moved,
                    prev_map_id,
                    next_map_id,
                )

        self._active_map_id = next_map_id
        self.task_config.map_id = next_map_id
        self._load_map_overlay_state_for_map(next_map_id)
        # Force one-shot map switch sync in next tick.
        self._last_seen_map_id = ""
        rospy.loginfo(
            "Active map switched: %s -> %s%s",
            prev_map_id,
            next_map_id,
            (" reason={}".format(reason) if reason else ""),
        )

    def _sync_task_map_binding(self, update_binding=True):
        map_id = self._current_map_id()
        self.task_config.map_id = map_id
        task_id = (self.task_config.task_id or "task").strip() or "task"
        key = "{}::{}".format(map_id, task_id)
        if update_binding:
            old_record = self._task_bindings.get(key, {}) if isinstance(self._task_bindings.get(key, {}), dict) else {}
            # Keep only one task record per map: new task replaces old task on same map.
            for old_key in list(self._task_bindings.keys()):
                if not isinstance(old_key, str):
                    continue
                if old_key.startswith("{}::".format(map_id)) and old_key != key:
                    self._task_bindings.pop(old_key, None)
            self._task_bindings[key] = {
                "task_id": task_id,
                "map_id": map_id,
                "selected_work_region_ids": list(self.task_config.selected_work_region_ids or []),
                "region_repeat_config": dict(self.task_config.region_repeat_config or {}),
                "active_work_region_id": self.task_config.active_work_region_id or "",
                "updated_at": int(time.time()),
                "task_result": dict(old_record.get("task_result", {}) or {}),
            }
            return
        binding = self._task_bindings.get(key)
        if not isinstance(binding, dict):
            return
        selected = []
        for rid in list(binding.get("selected_work_region_ids", []) or []):
            rid_text = str(rid).strip()
            if rid_text and rid_text not in selected:
                selected.append(rid_text)
        repeat_cfg = {}
        for rid, count in dict(binding.get("region_repeat_config", {}) or {}).items():
            rid_text = str(rid).strip()
            if not rid_text:
                continue
            try:
                repeat_cfg[rid_text] = max(1, int(count))
            except Exception:
                repeat_cfg[rid_text] = 1
        self.task_config.selected_work_region_ids = selected
        self.task_config.region_repeat_config = repeat_cfg
        active = str(binding.get("active_work_region_id", "")).strip()
        if active:
            self.task_config.active_work_region_id = active

    def _validate_requested_map_id(self, requested_map_id, op_name, keep_current_on_empty=False):
        req = str(requested_map_id or "").strip()
        current = self._current_map_id()
        if not req:
            if keep_current_on_empty:
                return True, current
            # Empty map_id defaults to realtime live map for legacy behavior.
            if current != self._live_map_id:
                self._set_active_map_id(
                    self._live_map_id,
                    reason="{}_default_live_map".format(op_name),
                    migrate_bindings=False,
                )
            return True, self._live_map_id
        if req == self._live_map_id:
            # Empty map_id or explicit LIVE_MAP always means realtime live map.
            if current != self._live_map_id:
                self._set_active_map_id(
                    self._live_map_id,
                    reason="{}_default_live_map".format(op_name),
                    migrate_bindings=False,
                )
            return True, self._live_map_id
        if req != current:
            # If caller provides a recorded map_id, switch active map on-demand
            # instead of hard rejecting due to map mismatch.
            record = self._find_recorded_map_by_id(req)
            if record is None:
                rospy.logwarn(
                    "%s rejected: requested_map_id=%s current_map_id=%s (map_id not found)",
                    op_name,
                    req,
                    current,
                )
                return False, current
            self._set_active_map_id(
                req,
                reason="{}_requested_map_switch".format(op_name),
                migrate_bindings=False,
            )
            rospy.loginfo(
                "%s auto-switched active map: %s -> %s",
                op_name,
                current,
                req,
            )
            return True, req
        return True, current

    def _effective_selected_work_region_ids(self, ordered_regions):
        selected = []
        configured = list(self.task_config.selected_work_region_ids or [])
        valid_ids = []
        for region in ordered_regions:
            rid = str(region.get("region_id", "")).strip()
            if rid:
                valid_ids.append(rid)
        valid_set = set(valid_ids)
        for rid in configured:
            rid_text = str(rid).strip()
            if rid_text and rid_text in valid_set and rid_text not in selected:
                selected.append(rid_text)
        if selected:
            return selected
        active_id = (self.task_config.active_work_region_id or "").strip()
        if active_id and active_id in valid_set:
            return [active_id]
        return valid_ids

    def _resolve_plan_work_regions(self, force_use_all_regions=False):
        regions = list(self.task_config.work_regions or [])
        if not regions:
            return []
        # Base order: order_index (stable sort keeps insertion order for ties).
        regions.sort(key=lambda region: int(region.get("order_index", 0)))
        region_by_id = {}
        for region in regions:
            rid = str(region.get("region_id", "")).strip()
            if rid and rid not in region_by_id:
                region_by_id[rid] = region
        if force_use_all_regions:
            selected_ids = [str(region.get("region_id", "")).strip() for region in regions if str(region.get("region_id", "")).strip()]
        else:
            selected_ids = self._effective_selected_work_region_ids(regions)
        selected_set = set(selected_ids)
        filtered = [region for region in regions if str(region.get("region_id", "")).strip() in selected_set]
        # If task explicitly provides selected_work_region_ids, respect that exact order.
        if (not force_use_all_regions) and selected_ids:
            ordered = []
            seen = set()
            for rid in selected_ids:
                rid_text = str(rid).strip()
                if (not rid_text) or (rid_text in seen):
                    continue
                region = region_by_id.get(rid_text)
                if region is not None:
                    ordered.append(region)
                    seen.add(rid_text)
            if ordered:
                filtered = ordered
        if not filtered:
            return []
        # Keep original region_id here.
        # Repeat expansion is handled centrally in planner_adapter by region_repeat_config.
        # If we rewrite IDs to "__lap_n" here, selected_work_region_ids matching may fail.
        return filtered

    def _sorted_work_region_ids(self):
        regions = list(self.task_config.work_regions or [])
        regions.sort(key=lambda region: int(region.get("order_index", 0)))
        return self._effective_selected_work_region_ids(regions)

    def _advance_active_work_region_for_request(self):
        """Round-robin select active work region for each explicit PathPlanRequest."""
        regions = list(self.task_config.work_regions or [])
        if not regions:
            self.task_config.active_work_region_id = ""
            return
        regions.sort(key=lambda region: int(region.get("order_index", 0)))
        region_ids = [str(item.get("region_id", "")).strip() for item in regions]
        region_ids = [item for item in region_ids if item]
        if not region_ids:
            self.task_config.active_work_region_id = ""
            return
        current = (self.task_config.active_work_region_id or "").strip()
        if current not in region_ids:
            self.task_config.active_work_region_id = region_ids[0]
            return
        next_idx = (region_ids.index(current) + 1) % len(region_ids)
        self.task_config.active_work_region_id = region_ids[next_idx]

    def _effective_crop_region(self):
        crop = self.task_config.crop_region if isinstance(self.task_config.crop_region, dict) else {}
        points = crop.get("points", []) if isinstance(crop, dict) else []
        if len(points) >= 3 and bool(crop.get("enabled", True)):
            return crop
        try:
            overlay = self.map_service.get_overlay_regions() or {}
            overlay_crop = overlay.get("crop_region")
            if isinstance(overlay_crop, dict):
                overlay_points = overlay_crop.get("points", []) or []
                if len(overlay_points) >= 3 and bool(overlay_crop.get("enabled", True)):
                    return overlay_crop
        except Exception:
            pass
        return {}

    def _crop_preview_image_by_region(self, image, map_info):
        if image is None or map_info is None:
            return image
        crop_region = self._effective_crop_region()
        crop_points = crop_region.get("points", []) if isinstance(crop_region, dict) else []
        if len(crop_points) < 3:
            return image
        preview_h, preview_w = image.shape[:2]
        scale_x = float(preview_w) / float(max(1, map_info["width"]))
        scale_y = float(preview_h) / float(max(1, map_info["height"]))
        polygon = []
        for point in crop_points:
            pixel_x, pixel_y = self._map_point_to_preview_pixel(
                point,
                map_info,
                scale_x,
                scale_y,
                preview_w,
                preview_h,
            )
            polygon.append([pixel_x, pixel_y])
        if len(polygon) < 3:
            return image
        arr = np.array(polygon, dtype=np.int32)
        min_x = int(max(0, np.min(arr[:, 0])))
        max_x = int(min(preview_w - 1, np.max(arr[:, 0])))
        min_y = int(max(0, np.min(arr[:, 1])))
        max_y = int(min(preview_h - 1, np.max(arr[:, 1])))
        if not (max_x > min_x and max_y > min_y):
            return image
        pad = 4
        x0 = max(0, min_x - pad)
        y0 = max(0, min_y - pad)
        x1 = min(preview_w, max_x + 1 + pad)
        y1 = min(preview_h, max_y + 1 + pad)
        cropped = image[y0:y1, x0:x1]
        rospy.loginfo_throttle(
            2.0,
            "Path preview crop applied: src=%dx%d dst=%dx%d crop_bbox=(%d,%d)-(%d,%d)",
            preview_w,
            preview_h,
            int(cropped.shape[1]),
            int(cropped.shape[0]),
            x0,
            y0,
            x1,
            y1,
        )
        return cropped

    def _handle_plan_now(self, _req):
        success = self._plan_current_task()
        if success and self.current_path is not None:
            return TriggerResponse(
                success=True,
                message="planning_ok path_version={} points={}".format(
                    self.current_path.path_version,
                    len(self.current_path.points),
                ),
            )
        return TriggerResponse(success=False, message=self.last_error or "planning_failed")

    def _plan_current_task(self, force_use_all_regions=False, request_start_pose=None, request_end_pose=None, request_global_direction="x"):
        # Always plan against the latest map edit overlay (work/obstacle regions).
        self._sync_task_regions_from_overlay()
        self._sync_task_map_binding(update_binding=True)
        if self._reload_navigation_map_on_plan:
            try:
                raw_map_for_nav = self.aurora_bridge.get_map()
                if raw_map_for_nav is not None:
                    # Keep map_service raw cache in sync before export.
                    self.map_service.set_raw_map(raw_map_for_nav)
                map_info_for_nav = self.map_service.get_map_info()
                composed_for_nav = self.map_service.compose_map()
                if map_info_for_nav is None or composed_for_nav is None:
                    raise RuntimeError("composed map unavailable")
                nav_dir = os.path.dirname(self._nav_map_yaml_path)
                nav_yaml_name = os.path.basename(self._nav_map_yaml_path)
                nav_image_name = "map1.pgm"
                nav_yaml_path, _ = self._export_runtime_map(
                    raw_map_for_nav,
                    nav_dir,
                    nav_yaml_name,
                    nav_image_name,
                    grid_override=composed_for_nav,
                    map_info_override=map_info_for_nav,
                )
                reloaded, result_code = self._reload_navigation_map(nav_yaml_path)
                if reloaded:
                    rospy.loginfo("Navigation map refreshed before planning from composed_map: %s", nav_yaml_path)
                else:
                    rospy.logwarn(
                        "Navigation map refresh before planning failed (code=%s), continue planning with current map",
                        str(result_code),
                    )
            except Exception as exc:
                rospy.logwarn("Navigation map refresh before planning failed: %s", exc)
        selected_work_regions = self._resolve_plan_work_regions(force_use_all_regions=force_use_all_regions)
        has_task_info = bool(list(self.task_config.selected_work_region_ids or [])) or bool(
            dict(self.task_config.region_repeat_config or {})
        )
        rospy.loginfo(
            "Planning input regions: work_total=%d work_selected=%d obstacle=%d active_work_region_id=%s force_use_all=%s has_task_info=%s",
            len(self.task_config.work_regions),
            len(selected_work_regions),
            len(self.task_config.obstacle_regions),
            self.task_config.active_work_region_id or "<auto>",
            str(bool(force_use_all_regions)).lower(),
            str(bool(has_task_info)).lower(),
        )
        if not selected_work_regions:
            self._set_error("Planning failed: no valid work region")
            rospy.logwarn("Planning aborted: no valid work region in overlay")
            return False
        map_info = self.map_service.get_map_info()
        composed_map = self.map_service.compose_map()
        if map_info is None or composed_map is None:
            rospy.logwarn("Planning skipped: map_info or composed_map is empty")
            self._set_error("Cannot plan without a map")
            return False
        rospy.loginfo(
            "Planning started: task_id=%s map_version=%s map_size=%sx%s resolution=%.4f",
            self.task_config.task_id or "task",
            map_info.get("map_version", 0),
            map_info.get("width", 0),
            map_info.get("height", 0),
            float(map_info.get("resolution", 0.0)),
        )
        self.state = SchedulerState.PLANNING
        try:
            current_pose = self.aurora_bridge.get_pose()
            rospy.loginfo(
                "Plan request poses: current_pose=(%.3f, %.3f, %.1fdeg) request_start=(%s) request_end=(%s)",
                float(current_pose.get("x", 0.0)),
                float(current_pose.get("y", 0.0)),
                float(current_pose.get("heading_deg", 0.0)),
                (
                    "{:.3f}, {:.3f}, {:.1f}deg".format(
                        float((request_start_pose or {}).get("x", 0.0)),
                        float((request_start_pose or {}).get("y", 0.0)),
                        float((request_start_pose or {}).get("heading_deg", 0.0)),
                    )
                    if request_start_pose
                    else "<empty>"
                ),
                (
                    "{:.3f}, {:.3f}, {:.1f}deg".format(
                        float((request_end_pose or {}).get("x", 0.0)),
                        float((request_end_pose or {}).get("y", 0.0)),
                        float((request_end_pose or {}).get("heading_deg", 0.0)),
                    )
                    if request_end_pose
                    else "<empty>"
                ),
            )
            plan_task_config = TaskConfigModel(
                task_id=self.task_config.task_id,
                map_id=self.task_config.map_id,
                work_regions=selected_work_regions,
                obstacle_regions=self.task_config.obstacle_regions,
                erase_regions=self.task_config.erase_regions,
                crop_region=self.task_config.crop_region,
                active_work_region_id=self.task_config.active_work_region_id,
                selected_work_region_ids=self.task_config.selected_work_region_ids,
                region_repeat_config=self.task_config.region_repeat_config,
                vehicle_width=self.task_config.vehicle_width,
                vehicle_length=self.task_config.vehicle_length,
                default_path_spacing=self.task_config.default_path_spacing,
                global_direction=str(request_global_direction or "x").strip().lower() or "x",
                turn_radius=self.task_config.turn_radius,
                overlap_ratio=self.task_config.overlap_ratio,
                inflation_radius=self.task_config.inflation_radius,
                current_pose=current_pose,
                start_pose=request_start_pose or {},
                end_pose=request_end_pose or {},
            )
            self.current_path = self.planner.plan(self.task_config.task_id or "task", composed_map, map_info, plan_task_config)
            # Disable synthetic prepended start point:
            # if planner injected a first point marked as start_pose/current_pose,
            # drop it so navigation follows only planned region path points.
            try:
                if self.current_path is not None and isinstance(self.current_path.points, list) and len(self.current_path.points) > 1:
                    first = self.current_path.points[0] if isinstance(self.current_path.points[0], dict) else {}
                    first_point_type = str(first.get("point_type", "") or "").strip().lower()
                    first_source = str(first.get("source", "") or "").strip().lower()
                    if first_point_type in ("start_pose", "current_pose", "injected_start") or first_source in (
                        "start_pose",
                        "current_pose",
                        "injected_start",
                    ):
                        self.current_path.points = self.current_path.points[1:]
                        if self.current_path.nav_path is not None and hasattr(self.current_path.nav_path, "poses"):
                            if len(self.current_path.nav_path.poses) > 1:
                                self.current_path.nav_path.poses = self.current_path.nav_path.poses[1:]
                        rospy.loginfo("Removed prepended start point from planned path.")
            except Exception as _exc:
                rospy.logwarn("Failed to remove prepended start point safely: %s", _exc)
            self._current_plan_scope = "all" if len(selected_work_regions) > 1 else "single"
        except Exception as exc:
            rospy.logerr("Planning failed with exception: %s", exc)
            self._set_error("Planning failed: {}".format(exc))
            return False

        if self.current_path is None or not self.current_path.points:
            rospy.logwarn("Planning finished but returned empty path")
            self._set_error("Planning failed: empty path")
            return False

        # Only prepend current pose when task context exists.
        # For pure area preview planning (no task info), keep regions disconnected
        # from robot pose to avoid a fake line from current position.
        if has_task_info:
            self._prepend_current_pose_as_start_point(map_info)
        else:
            rospy.loginfo("Skip prepending current pose point because has_task_info=false")
        self._rebuild_goal_points()
        self.current_path.nav_path.header.stamp = rospy.Time.now()
        for pose in self.current_path.nav_path.poses:
            pose.header.stamp = self.current_path.nav_path.header.stamp
        self._publish_path_to_navigation(publish_goal=False, reason="plan_success")
        self.current_path_index = 0
        self.state = SchedulerState.READY
        self.last_error = ""
        self._publish_preview_metadata(map_info)
        self._save_planned_path_preview(map_info)
        self._save_planned_path_debug_json(map_info)
        self._save_local_state()
        rospy.loginfo(
            "Planning success: path_version=%s points=%s length_m=%.3f",
            self.current_path.path_version,
            len(self.current_path.points),
            float(self.current_path.length_m),
        )
        return True

    def _save_planned_path_preview(self, map_info):
        if self.current_path is None or not self.current_path.points:
            return
        try:
            payload = self._build_path_preview_payload(map_info)
            if payload is None:
                raise RuntimeError("Failed to build path preview payload")
            self._save_path_preview_bytes(payload[0], payload[1], map_info)
        except Exception as exc:
            rospy.logwarn("Failed to save planned path preview: %s", exc)

    def _save_path_preview_bytes(self, image_data, image_format, map_info):
        if self.current_path is None:
            return
        os.makedirs(self._planned_path_preview_dir, exist_ok=True)
        task_name = self._sanitize_name(self.current_path.task_id or "task")
        ext = str(image_format or "jpg")
        latest_files = [
            os.path.join(self._planned_path_preview_dir, "aurora_path_preview_latest.{}".format(ext)),
            os.path.join(self._planned_path_preview_dir, "aurora_path_preview_task{}_latest.{}".format(task_name, ext)),
        ]
        for full_path in latest_files:
            with open(full_path, "wb") as handle:
                handle.write(image_data)
        rospy.loginfo(
            "Saved planned path preview latest files: %s, %s",
            latest_files[0],
            latest_files[1],
        )

    def _save_planned_path_debug_json(self, map_info):
        if self.current_path is None or not self.current_path.points:
            return
        try:
            os.makedirs(self._planned_path_debug_dir, exist_ok=True)
            filename = "planned_path_task{}_mapv{}_pathv{}_{}.json".format(
                self._sanitize_name(self.current_path.task_id or "task"),
                int((map_info or {}).get("map_version", 0)),
                int(self.current_path.path_version),
                int(time.time()),
            )
            full_path = os.path.join(self._planned_path_debug_dir, filename)
            payload = {
                "saved_at": int(time.time()),
                "task_id": str(self.current_path.task_id or ""),
                "map_id": str(self.task_config.map_id or ""),
                "path_version": int(self.current_path.path_version),
                "path_length_m": float(self.current_path.length_m),
                "path_point_count": int(len(self.current_path.points)),
                "estimated_time_s": float(self._estimate_plan_time_s(self.current_path.length_m)),
                "frame_id": str((map_info or {}).get("frame_id", "")),
                "map_info": {
                    "map_version": int((map_info or {}).get("map_version", 0)),
                    "width": int((map_info or {}).get("width", 0)),
                    "height": int((map_info or {}).get("height", 0)),
                    "resolution": float((map_info or {}).get("resolution", 0.0)),
                    "origin_x": float((map_info or {}).get("origin_x", 0.0)),
                    "origin_y": float((map_info or {}).get("origin_y", 0.0)),
                },
                "points": list(self.current_path.points),
            }
            with open(full_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            rospy.loginfo("Saved planned path debug json to %s", full_path)
        except Exception as exc:
            rospy.logwarn("Failed to save planned path debug json: %s", exc)

    def _build_path_preview_payload(self, map_info):
        if self.current_path is None or not self.current_path.points:
            return None
        if self._current_plan_scope == "all":
            selected_work_regions = self._resolve_plan_work_regions(force_use_all_regions=True)
        else:
            selected_work_regions = self._resolve_plan_work_regions(force_use_all_regions=False)
        alignment_kwargs = self._map_preview_alignment_kwargs()
        alignment_yaw = alignment_kwargs.get("alignment_yaw", None)
        snapshot = self.map_service.create_preview(
            None,
            self._planned_path_preview_max_edge,
            self._planned_path_preview_format,
            False,
            **alignment_kwargs
        )
        image = cv2.imdecode(np.frombuffer(snapshot.preview_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return None
        render_map_info = {
            "width": int(snapshot.width),
            "height": int(snapshot.height),
            "origin_x": float(snapshot.origin_x),
            "origin_y": float(snapshot.origin_y),
            "resolution": float(snapshot.resolution),
            "map_version": int(snapshot.map_version),
            "frame_id": snapshot.frame_id,
            "alignment_yaw": alignment_yaw,
        }
        preview_h, preview_w = image.shape[:2]
        scale_x = float(preview_w) / float(max(1, render_map_info["width"]))
        scale_y = float(preview_h) / float(max(1, render_map_info["height"]))

        def _region_to_preview_polygon(region_points):
            polygon = []
            for point in region_points:
                pixel_x, pixel_y = self._map_point_to_preview_pixel(
                    point,
                    render_map_info,
                    scale_x,
                    scale_y,
                    preview_w,
                    preview_h,
                )
                polygon.append([pixel_x, pixel_y])
            return polygon

        self._paint_region_overrides_for_path_preview(image, render_map_info, scale_x, scale_y, _region_to_preview_polygon)

        polyline = []
        for point in self.current_path.points:
            pixel_x, pixel_y = self._map_point_to_preview_pixel(
                point,
                render_map_info,
                scale_x,
                scale_y,
                preview_w,
                preview_h,
            )
            polyline.append({
                "x": pixel_x,
                "y": pixel_y,
                "path_type": str(point.get("path_type", "") or ""),
            })
        # Display only selected work regions on path preview.
        for region in selected_work_regions:
            region_points = region.get("points", []) if isinstance(region, dict) else []
            if len(region_points) < 3:
                continue
            polygon = _region_to_preview_polygon(region_points)
            if len(polygon) >= 3:
                polygon_np = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(image, [polygon_np], isClosed=True, color=(0, 200, 0), thickness=1)
        if len(polyline) >= 2:
            region_segments = []
            def _draw_segments(type_filter, color):
                segment = []
                for item in polyline:
                    if type_filter(item["path_type"]):
                        segment.append([item["x"], item["y"]])
                    else:
                        if len(segment) >= 2:
                            seg_np = np.array(segment, dtype=np.int32).reshape((-1, 1, 2))
                            cv2.polylines(image, [seg_np], isClosed=False, color=color, thickness=1)
                        segment = []
                if len(segment) >= 2:
                    seg_np = np.array(segment, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(image, [seg_np], isClosed=False, color=color, thickness=1)

            def _draw_non_connection(color):
                segment = []
                last_type = ""
                last_start = None
                for item in polyline:
                    t = str(item.get("path_type", "") or "")
                    if t == "connection":
                        if len(segment) >= 2:
                            seg_np = np.array(segment, dtype=np.int32).reshape((-1, 1, 2))
                            cv2.polylines(image, [seg_np], isClosed=False, color=color, thickness=1)
                            if last_start is not None:
                                region_segments.append((last_type, tuple(last_start), tuple(segment[-1])))
                        segment = []
                        last_type = ""
                        last_start = None
                        continue
                    # Break line when switching between different region path types
                    # to avoid fake straight links across disconnected regions.
                    if last_type and t != last_type:
                        if len(segment) >= 2:
                            seg_np = np.array(segment, dtype=np.int32).reshape((-1, 1, 2))
                            cv2.polylines(image, [seg_np], isClosed=False, color=color, thickness=1)
                            if last_start is not None:
                                region_segments.append((last_type, tuple(last_start), tuple(segment[-1])))
                        segment = []
                        last_start = None
                    if not segment:
                        last_start = [item["x"], item["y"]]
                    segment.append([item["x"], item["y"]])
                    last_type = t
                if len(segment) >= 2:
                    seg_np = np.array(segment, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(image, [seg_np], isClosed=False, color=color, thickness=1)
                    if last_start is not None:
                        region_segments.append((last_type, tuple(last_start), tuple(segment[-1])))

            # 覆盖段：红色（按各区域分段）；区域间连接段：青色（更容易区分）
            _draw_non_connection((0, 0, 255))
            _draw_segments(lambda t: t == "connection", (255, 255, 0))
            if self._planned_path_preview_show_direction:
                arrow_step = self._planned_path_preview_arrow_step
                arrow_len_px = float(self._planned_path_preview_arrow_len_px)
                for idx in range(0, len(polyline) - 1, arrow_step):
                    p0 = polyline[idx]
                    p1 = polyline[min(idx + 1, len(polyline) - 1)]
                    dx = float(p1["x"] - p0["x"])
                    dy = float(p1["y"] - p0["y"])
                    norm = math.hypot(dx, dy)
                    if norm < 1.0:
                        continue
                    ux = dx / norm
                    uy = dy / norm
                    ex = int(round(float(p0["x"]) + ux * arrow_len_px))
                    ey = int(round(float(p0["y"]) + uy * arrow_len_px))
                    start_pt = (int(p0["x"]), int(p0["y"]))
                    end_pt = (max(0, min(preview_w - 1, ex)), max(0, min(preview_h - 1, ey)))
                    color = (255, 255, 0) if str(p0.get("path_type", "")) == "connection" else (0, 120, 255)
                    cv2.arrowedLine(
                        image,
                        start_pt,
                        end_pt,
                        color,
                        thickness=1,
                        line_type=cv2.LINE_AA,
                        tipLength=0.45,
                    )
            # Keep only start/end markers; index labels and direction arrows stay disabled by policy.
            cv2.circle(image, (polyline[0]["x"], polyline[0]["y"]), 5, (0, 220, 0), thickness=-1)
            cv2.circle(image, (polyline[-1]["x"], polyline[-1]["y"]), 5, (0, 140, 255), thickness=-1)
            # Mark start/end for each region segment to make region handoff explicit.
            for seg_type, seg_start, seg_end in region_segments:
                if not seg_type or seg_type == "connection":
                    continue
                cv2.circle(image, (int(seg_start[0]), int(seg_start[1])), 4, (0, 220, 0), thickness=-1)
                cv2.circle(image, (int(seg_end[0]), int(seg_end[1])), 4, (0, 140, 255), thickness=-1)
        image = self._crop_preview_image_by_region(image, render_map_info)
        ext = ".png" if snapshot.preview_format.lower() == "png" else ".jpg"
        ok, buffer = cv2.imencode(ext, image)
        if not ok:
            return None
        return buffer.tobytes(), snapshot.preview_format, render_map_info

    def _build_failed_plan_preview_payload(self, error_message):
        try:
            alignment_kwargs = self._map_preview_alignment_kwargs()
            alignment_yaw = alignment_kwargs.get("alignment_yaw", None)
            snapshot = self.map_service.create_preview(
                None,
                self._planned_path_preview_max_edge,
                self._planned_path_preview_format,
                self._planned_path_preview_include_overlay,
                **alignment_kwargs
            )
            image = cv2.imdecode(np.frombuffer(snapshot.preview_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                return snapshot.preview_data, snapshot.preview_format, None
            render_map_info = {
                "width": int(snapshot.width),
                "height": int(snapshot.height),
                "origin_x": float(snapshot.origin_x),
                "origin_y": float(snapshot.origin_y),
                "resolution": float(snapshot.resolution),
                "map_version": int(snapshot.map_version),
                "frame_id": snapshot.frame_id,
                "alignment_yaw": alignment_yaw,
            }
            if render_map_info is not None:
                preview_h, preview_w = image.shape[:2]
                scale_x = float(preview_w) / float(max(1, render_map_info["width"]))
                scale_y = float(preview_h) / float(max(1, render_map_info["height"]))

                def _region_to_preview_polygon(region_points):
                    polygon = []
                    for point in region_points:
                        pixel_x, pixel_y = self._map_point_to_preview_pixel(
                            point,
                            render_map_info,
                            scale_x,
                            scale_y,
                            preview_w,
                            preview_h,
                        )
                        polygon.append([pixel_x, pixel_y])
                    return polygon

                self._paint_region_overrides_for_path_preview(image, render_map_info, scale_x, scale_y, _region_to_preview_polygon)
                image = self._crop_preview_image_by_region(image, render_map_info)
            text = "Planning failed: {}".format(error_message or "unknown")
            text = text[:120]
            cv2.putText(
                image,
                text,
                (16, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            ext = ".png" if snapshot.preview_format.lower() == "png" else ".jpg"
            ok, buffer = cv2.imencode(ext, image)
            if not ok:
                return snapshot.preview_data, snapshot.preview_format, render_map_info
            return buffer.tobytes(), snapshot.preview_format, render_map_info
        except Exception:
            return None

    def _paint_region_overrides_for_path_preview(self, image, map_info, scale_x, scale_y, polygon_builder):
        try:
            overlay = self.map_service.get_overlay_regions() or {}
            obstacle_regions = overlay.get("obstacle_regions", []) or []
        except Exception:
            obstacle_regions = []
        obstacle_count = 0
        erase_count = 0
        obstacle_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        erase_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for region in obstacle_regions:
            if not isinstance(region, dict):
                continue
            if not bool(region.get("enabled", True)):
                continue
            points = region.get("points", []) or []
            if len(points) < 3:
                continue
            poly = polygon_builder(points)
            if len(poly) < 3:
                continue
            region_type = int(region.get("region_type", 2))
            if region_type == 3:
                cv2.fillPoly(erase_mask, [np.array(poly, dtype=np.int32)], color=255)
                erase_count += 1
            elif region_type == 2:
                # Obstacle-region visualization follows UNKNOWN tone on preview.
                cv2.fillPoly(obstacle_mask, [np.array(poly, dtype=np.int32)], color=255)
                obstacle_count += 1
        # Cover polygon edge quantization gaps after world->preview projection.
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        obstacle_mask = cv2.dilate(obstacle_mask, kernel, iterations=1)
        erase_mask = cv2.dilate(erase_mask, kernel, iterations=1)
        if int(np.count_nonzero(obstacle_mask)) > 0:
            image[obstacle_mask > 0] = (180, 180, 180)
        if int(np.count_nonzero(erase_mask)) > 0:
            image[erase_mask > 0] = (245, 245, 245)
        rospy.loginfo_throttle(
            2.0,
            "Path preview paint override: obstacle_regions=%d erase_regions=%d",
            obstacle_count,
            erase_count,
        )

    def _sanitize_name(self, text):
        safe = "".join(ch if (ch.isalnum() or ch in ("_", "-")) else "_" for ch in str(text))
        return safe[:64] if safe else "task"

    def _sanitize_map_filename_stem(self, text):
        # Keep Chinese/Unicode letters and digits; drop path-unfriendly symbols.
        # This allows Android-provided Chinese map names to be preserved on disk.
        raw = str(text or "").strip()
        if not raw:
            return "地图"
        # Remove extension if user already passed ".stcm".
        if raw.lower().endswith(".stcm"):
            raw = raw[:-5]
        # Keep most printable filename chars, replace reserved separators.
        safe_chars = []
        for ch in raw:
            if ch in ('\\', '/', ':', '*', '?', '"', '<', '>', '|'):
                safe_chars.append("_")
                continue
            # avoid control characters
            if ord(ch) < 32:
                continue
            safe_chars.append(ch)
        safe = "".join(safe_chars).strip().strip(".")
        if not safe:
            safe = "地图"
        return safe[:96]

    def _build_stcm_download_path(self, requested_path, forced_map_id=""):
        req = str(requested_path or "").strip()
        if req:
            req = os.path.expanduser(os.path.expandvars(req))
        if req:
            req_dir = os.path.dirname(req)
            if req_dir:
                save_dir = req_dir if os.path.isabs(req_dir) else os.path.join(self._stcm_local_dir, req_dir)
            else:
                save_dir = self._stcm_local_dir
            base_name = os.path.basename(req)
            stem = self._sanitize_map_filename_stem(base_name)
        else:
            save_dir = self._stcm_local_dir
            stem = "地图"
        map_id = str(forced_map_id or "").strip() or datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "{}_{}.stcm".format(stem, map_id)
        return os.path.normpath(os.path.join(save_dir, filename))

    def _split_map_name_and_id_from_path(self, stcm_path):
        base = os.path.splitext(os.path.basename(str(stcm_path or "")))[0]
        # Expected generated filename: <map_name>_<YYYYMMDD_HHMMSS>.stcm
        matched = re.match(r"^(.*)_(\d{8}_\d{6})$", base)
        if matched:
            raw_name = matched.group(1).strip("_").strip()
            map_id = matched.group(2)
            return (raw_name or "地图"), map_id
        fallback_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return (base or "地图"), fallback_id

    def _register_saved_map(
        self,
        stcm_path,
        display_name="",
        explicit_map_id="",
        total_work_area_m2=0.0,
        estimated_time_s=-1.0,
        region_metrics=None,
        thumb_format="",
        thumb_b64="",
        thumb_width=0,
        thumb_height=0,
    ):
        try:
            abs_path = os.path.abspath(str(stcm_path or "").strip())
            if not abs_path:
                return "", ""
            parsed_name, parsed_id = self._split_map_name_and_id_from_path(abs_path)
            name = str(display_name or "").strip() or parsed_name
            map_id = str(explicit_map_id or "").strip() or str(parsed_id)
            size_bytes = 0
            if os.path.isfile(abs_path):
                try:
                    size_bytes = int(os.path.getsize(abs_path))
                except Exception:
                    size_bytes = 0
            old_record = self._map_registry.get(abs_path, {})
            old_created_at = ""
            if isinstance(old_record, dict):
                old_created_at = str(old_record.get("created_at", "") or "").strip()
                if not old_created_at:
                    old_created_at = _format_ts_s(old_record.get("saved_at", 0))
            created_at = old_created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._map_registry[abs_path] = {
                "map_id": map_id,
                "name": name,
                "path": abs_path,
                "size_bytes": size_bytes,
                "created_at": str(created_at),
                "saved_at": int(time.time()),
                "total_work_area_m2": float(max(0.0, float(total_work_area_m2 or 0.0))),
                "estimated_time_s": float(estimated_time_s if estimated_time_s is not None else -1.0),
                "region_metrics": list(region_metrics or []),
                "thumb_format": str(thumb_format or "").strip(),
                "thumb_b64": str(thumb_b64 or ""),
                "thumb_width": int(max(0, int(thumb_width or 0))),
                "thumb_height": int(max(0, int(thumb_height or 0))),
            }
            return name, map_id
        except Exception as exc:
            rospy.logwarn("Failed to register saved map metadata: %s", exc)
            return "", ""

    def _unregister_saved_map(self, target_path):
        abs_path = os.path.abspath(str(target_path or "").strip())
        if abs_path:
            self._map_registry.pop(abs_path, None)

    def _find_recorded_map_by_id(self, map_id):
        target = str(map_id or "").strip()
        if not target:
            return None
        for record in (self._map_registry or {}).values():
            if not isinstance(record, dict):
                continue
            if str(record.get("map_id", "")).strip() == target:
                return record
        return None

    def _iter_recorded_maps(self, target_dir=""):
        target_dir = os.path.abspath(target_dir) if target_dir else ""
        exts = {".stcm"}
        entries = []
        for record in (self._map_registry or {}).values():
            if not isinstance(record, dict):
                continue
            path = os.path.abspath(str(record.get("path", "")).strip())
            if not path:
                continue
            ext = os.path.splitext(path)[1].lower()
            if ext not in exts:
                continue
            if target_dir:
                try:
                    if os.path.commonpath([path, target_dir]) != target_dir:
                        continue
                except Exception:
                    continue
            parsed_name, parsed_id = self._split_map_name_and_id_from_path(path)
            name = str(record.get("name", "")).strip() or parsed_name
            map_id = str(record.get("map_id", "")).strip() or parsed_id
            size_bytes = int(record.get("size_bytes", 0) or 0)
            if os.path.isfile(path):
                try:
                    size_bytes = int(os.path.getsize(path))
                except Exception:
                    pass
            total_work_area_m2 = float(record.get("total_work_area_m2", 0.0) or 0.0)
            estimated_time_s = float(record.get("estimated_time_s", -1.0) or -1.0)
            entries.append((name, map_id, path, size_bytes, total_work_area_m2, estimated_time_s))
        entries.sort(key=lambda item: item[0].lower())
        return entries

    def _publish_preview_metadata(self, map_info):
        message = MapPreviewMetadata()
        message.header.stamp = rospy.Time.now()
        message.map_version = map_info["map_version"]
        message.width = map_info["width"]
        message.height = map_info["height"]
        message.resolution = map_info["resolution"]
        message.origin.position.x = map_info["origin_x"]
        message.origin.position.y = map_info["origin_y"]
        message.origin.orientation.w = 1.0
        message.frame_id = map_info["frame_id"]
        self.preview_meta_pub.publish(message)

    def _start_execution(self):
        try:
            self._switch_to_localization_mode_after_map_save()
            rospy.loginfo("Task start pre-check: radar switched to localization mode")
        except Exception as exc:
            rospy.logwarn("Task start blocked: failed to switch radar to localization mode: %s", exc)
            return False, "Failed to switch radar to localization mode: {}".format(exc)
        if self.current_path is None and not self._plan_current_task():
            return False, "Failed to plan task"
        if self.current_path is None or not self.current_path.points:
            return False, "No planned path to execute"
        self._sync_task_regions_from_overlay()
        self._exec_region_order = self._sorted_work_region_ids()
        active_id = (self.task_config.active_work_region_id or "").strip()
        if active_id and active_id in self._exec_region_order:
            self._exec_region_index = self._exec_region_order.index(active_id)
        elif self._exec_region_order:
            self._exec_region_index = 0
            self.task_config.active_work_region_id = self._exec_region_order[0]
        else:
            self._exec_region_index = -1
        self._set_chassis_enabled(True)
        self.work_mode_pub.publish(UInt16(data=2))
        self.disc_lift_pub.publish(UInt16(data=1))
        self.disc_speed_pub.publish(Int16(data=1200))
        self.disc_enable_pub.publish(Bool(data=True))
        self.light_pub.publish(Bool(data=True))
        self._init_path_execution_cursor()
        self._exec_active = True
        self._exec_publish_start_pose_once = True
        self._exec_region_repeat_done = {}
        self._task_stop_reason = ""
        self._set_cmd_vel_forward_runtime_active(True, publish_zero=False, reason="task_start_nav_cmd_vel_forward")
        self._exec_last_send_time = 0.0
        self._exec_goal_start_time = time.time()
        self._publish_path_to_navigation(publish_goal=False, reason="task_start")
        self._dispatch_current_goal(force=True)
        self.state = SchedulerState.RUNNING
        rospy.loginfo(
            "Task execution started: regions=%s active=%s mode=%s",
            ",".join(self._exec_region_order) if self._exec_region_order else "<none>",
            self.task_config.active_work_region_id or "<none>",
            self._exec_mode,
        )
        return True, "Task started (mode={})".format(self._exec_mode)

    def _pause_execution(self):
        self._exec_active = False
        self._set_cmd_vel_forward_runtime_active(False, publish_zero=True, reason="task_pause")
        self._safe_stop_motion()
        self.disc_enable_pub.publish(Bool(data=False))
        self.state = SchedulerState.PAUSED
        return True, "Task paused"

    def _resume_execution(self):
        if self.current_path is None or not self.current_path.points:
            return False, "No path to resume"
        self._set_chassis_enabled(True)
        self._disc_last_mode = ""
        self.disc_enable_pub.publish(Bool(data=True))
        if self._exec_goal_index <= 0 or self._exec_goal_index >= len(self.current_path.points):
            self._init_path_execution_cursor()
        self._exec_active = True
        self._exec_publish_start_pose_once = True
        self._set_cmd_vel_forward_runtime_active(True, publish_zero=False, reason="task_resume_nav_cmd_vel_forward")
        self._exec_goal_start_time = time.time()
        self._publish_path_to_navigation(publish_goal=False, reason="task_resume")
        self._dispatch_current_goal(force=True)
        self.state = SchedulerState.RUNNING
        return True, "Task resumed"

    def _stop_execution(self):
        self._exec_active = False
        self._mark_current_region_repeat_done()
        self._set_cmd_vel_forward_runtime_active(False, publish_zero=True, reason="task_stop")
        self._safe_stop_motion()
        self.disc_enable_pub.publish(Bool(data=False))
        self.light_pub.publish(Bool(data=False))
        self.disc_lift_pub.publish(UInt16(data=2))
        self._set_chassis_enabled(False)
        self._exec_region_order = []
        self._exec_region_index = -1
        self.state = SchedulerState.STOPPED
        self._task_stop_reason = "stopped_by_command"
        self._finalize_task_result(stop_reason=self._task_stop_reason)
        return True, "Task stopped"

    def _safe_stop_motion(self):
        wheel = WheelSpeedCommand()
        wheel.left_wheel_speed = 0
        wheel.right_wheel_speed = 0
        self.wheel_cmd_pub.publish(wheel)
        self._set_chassis_enabled(False)

    def _normalize_angle(self, rad):
        return math.atan2(math.sin(rad), math.cos(rad))

    def _yaw_to_quaternion(self, yaw):
        half = 0.5 * float(yaw)
        return {
            "x": 0.0,
            "y": 0.0,
            "z": math.sin(half),
            "w": math.cos(half),
        }

    def _prepend_current_pose_as_start_point(self, map_info=None):
        if self.current_path is None or not self.current_path.points:
            return
        pose = self.aurora_bridge.get_pose() or {}
        start_x = float(pose.get("x", 0.0))
        start_y = float(pose.get("y", 0.0))
        heading_deg = float(pose.get("heading_deg", 0.0))
        orientation = pose.get("orientation") if isinstance(pose, dict) else None
        if isinstance(orientation, dict):
            try:
                quat = {
                    "x": float(orientation.get("x", 0.0)),
                    "y": float(orientation.get("y", 0.0)),
                    "z": float(orientation.get("z", 0.0)),
                    "w": float(orientation.get("w", 1.0)),
                }
            except Exception:
                quat = self._yaw_to_quaternion(math.radians(heading_deg))
        else:
            quat = self._yaw_to_quaternion(math.radians(heading_deg))

        if map_info is not None:
            resolution = max(1e-9, float(map_info.get("resolution", 0.05)))
            origin_x = float(map_info.get("origin_x", 0.0))
            origin_y = float(map_info.get("origin_y", 0.0))
            start_col = (start_x - origin_x) / resolution
            start_row = (start_y - origin_y) / resolution
        else:
            start_col = 0.0
            start_row = 0.0

        first = self.current_path.points[0]
        prepend_point = {
            "index": 0,
            "row": float(start_row),
            "col": float(start_col),
            "x": float(start_x),
            "y": float(start_y),
            "path_type": str(first.get("path_type", "start_pose") or "start_pose"),
            "point_type": "start",
            "timestamp": float(time.time()),
            "orientation": quat,
        }
        self.current_path.points.insert(0, prepend_point)
        for idx, item in enumerate(self.current_path.points):
            item["index"] = int(idx)

        first_x = float(first.get("x", start_x))
        first_y = float(first.get("y", start_y))
        self.current_path.length_m = float(self.current_path.length_m) + math.hypot(first_x - start_x, first_y - start_y)

        if self.current_path.nav_path is not None:
            nav_pose = PoseStamped()
            nav_pose.header.frame_id = self.current_path.nav_path.header.frame_id or (map_info or {}).get("frame_id", "map")
            nav_pose.pose.position.x = float(start_x)
            nav_pose.pose.position.y = float(start_y)
            nav_pose.pose.orientation.x = float(quat["x"])
            nav_pose.pose.orientation.y = float(quat["y"])
            nav_pose.pose.orientation.z = float(quat["z"])
            nav_pose.pose.orientation.w = float(quat["w"])
            self.current_path.nav_path.poses.insert(0, nav_pose)

        rospy.loginfo(
            "Prepended start pose point: x=%.3f y=%.3f heading=%.1fdeg path_points=%d",
            start_x,
            start_y,
            heading_deg,
            len(self.current_path.points),
        )

    def _resolve_point_orientation(self, point, index, cached_xy):
        ori = point.get("orientation") if isinstance(point, dict) else None
        if isinstance(ori, dict):
            try:
                return {
                    "x": float(ori.get("x", 0.0)),
                    "y": float(ori.get("y", 0.0)),
                    "z": float(ori.get("z", 0.0)),
                    "w": float(ori.get("w", 1.0)),
                }
            except Exception:
                pass

        # For straight-segment endpoints, keep heading aligned with the current segment
        # (previous point -> current point), not the next segment.
        try:
            if self._goal_points:
                for gp in self._goal_points:
                    if int(gp.get("path_index", -1)) == int(index):
                        if index > 0:
                            cx, cy = cached_xy[index]
                            px, py = cached_xy[index - 1]
                            yaw = math.atan2(cy - py, cx - px)
                            return self._yaw_to_quaternion(yaw)
                        break
        except Exception:
            pass

        if index + 1 < len(cached_xy):
            nx, ny = cached_xy[index + 1]
            cx, cy = cached_xy[index]
            yaw = math.atan2(ny - cy, nx - cx)
        elif index > 0:
            cx, cy = cached_xy[index]
            px, py = cached_xy[index - 1]
            yaw = math.atan2(cy - py, cx - px)
        else:
            yaw = 0.0
        return self._yaw_to_quaternion(yaw)

    def _resolve_straight_segment_end_index(self, start_index):
        if self.current_path is None or not self.current_path.points:
            return 0
        points = self.current_path.points
        n = len(points)
        if start_index >= n - 1:
            return n - 1

        threshold_rad = math.radians(float(self._goal_segment_yaw_threshold_deg))
        seg_type = str(points[start_index].get("path_type", "") or "")

        def _dir_angle(i0, i1):
            x0 = float(points[i0].get("x", 0.0))
            y0 = float(points[i0].get("y", 0.0))
            x1 = float(points[i1].get("x", 0.0))
            y1 = float(points[i1].get("y", 0.0))
            return math.atan2(y1 - y0, x1 - x0), math.hypot(x1 - x0, y1 - y0)

        base_angle = None
        end_index = start_index
        for idx in range(start_index, n - 1):
            cur_type = str(points[idx].get("path_type", "") or "")
            nxt_type = str(points[idx + 1].get("path_type", "") or "")
            if cur_type != seg_type or nxt_type != seg_type:
                break
            angle, seg_len = _dir_angle(idx, idx + 1)
            if seg_len < 1e-6:
                end_index = idx + 1
                continue
            if base_angle is None:
                base_angle = angle
                end_index = idx + 1
                continue
            diff = math.atan2(math.sin(angle - base_angle), math.cos(angle - base_angle))
            if abs(diff) > threshold_rad:
                break
            end_index = idx + 1
        return max(start_index, min(n - 1, end_index))

    def _rebuild_goal_points(self):
        self._goal_points = []
        if self.current_path is None or not self.current_path.points:
            return
        points = self.current_path.points
        n = len(points)
        cursor = 0
        cached_xy = [(float(p.get("x", 0.0)), float(p.get("y", 0.0))) for p in points]
        while cursor < n:
            end_idx = self._resolve_straight_segment_end_index(cursor)
            end_idx = max(cursor, min(n - 1, int(end_idx)))
            # Publish the penultimate point of each straight segment by default.
            # If the segment has only one point, fall back to the segment end.
            goal_idx = end_idx - 1 if end_idx > cursor else end_idx
            goal_idx = max(cursor, min(n - 1, int(goal_idx)))
            p = points[goal_idx]
            quat = self._resolve_point_orientation(p, goal_idx, cached_xy)
            self._goal_points.append(
                {
                    "path_index": int(goal_idx),
                    "x": float(p.get("x", 0.0)),
                    "y": float(p.get("y", 0.0)),
                    "path_type": str(p.get("path_type", "") or ""),
                    "orientation": quat,
                }
            )
            if end_idx >= n - 1:
                break
            cursor = end_idx + 1
        # Do not force append the final point here: goal points are intentionally
        # chosen as segment-penultimate points per current execution strategy.
        rospy.loginfo("Precomputed goal points: count=%d", len(self._goal_points))

    def _init_path_execution_cursor(self):
        if self.current_path is None or not self.current_path.points:
            self._exec_goal_index = 0
            return
        if not self._goal_points:
            self._rebuild_goal_points()
        pose = self.aurora_bridge.get_pose()
        nearest_index = 0
        nearest_distance = float("inf")
        for index, point in enumerate(self.current_path.points):
            distance = math.hypot(float(point["x"]) - pose["x"], float(point["y"]) - pose["y"])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_index = index
        self.current_path_index = nearest_index
        if not self._goal_points:
            self._exec_goal_index = min(nearest_index + 1, len(self.current_path.points) - 1)
            return

        # Do not publish the initial point as execution goal:
        # choose the first precomputed goal strictly ahead of current nearest index.
        target_goal_index = -1
        for i, item in enumerate(self._goal_points):
            if int(item.get("path_index", -1)) > int(nearest_index):
                target_goal_index = i
                break
        if target_goal_index < 0:
            # Fallback: if already near the final point, keep the last goal.
            target_goal_index = len(self._goal_points) - 1
        self._exec_goal_index = max(0, min(target_goal_index, len(self._goal_points) - 1))

    def _dispatch_current_goal(self, force=False):
        if not self._exec_active or self.current_path is None or not self.current_path.points:
            return
        if not self._goal_points:
            self._rebuild_goal_points()
        if not self._goal_points:
            return

        if force and bool(self._exec_publish_start_pose_once):
            self._publish_current_position_goal_once()
            self._exec_publish_start_pose_once = False

        # Before publishing, skip goals that are already reached.
        # This prevents publishing a near/initial point first.
        try:
            pose = self.aurora_bridge.get_pose()
            while 0 <= self._exec_goal_index < (len(self._goal_points) - 1):
                goal_probe = self._goal_points[self._exec_goal_index]
                dist_probe = math.hypot(
                    float(goal_probe.get("x", 0.0)) - float(pose.get("x", 0.0)),
                    float(goal_probe.get("y", 0.0)) - float(pose.get("y", 0.0)),
                )
                if dist_probe > float(self._exec_goal_reach_dist):
                    break
                self._exec_goal_index += 1
                self._exec_goal_start_time = time.time()
        except Exception:
            pass

        now = time.time()
        if (not force) and (now - self._exec_last_send_time < self._exec_goal_interval):
            return
        self._exec_last_send_time = now
        if force:
            self._publish_execution_goal_by_index(self._exec_goal_index, reason="exec_goal_step")
        goal = self._goal_points[self._exec_goal_index]
        rospy.loginfo_throttle(
            2.0,
            "Execution cursor update: idx=%d x=%.3f y=%.3f force=%s",
            int(goal.get("path_index", self._exec_goal_index)),
            float(goal.get("x", 0.0)),
            float(goal.get("y", 0.0)),
            str(bool(force)),
        )

    def _publish_execution_goal_by_index(self, target_index, reason=""):
        if self.current_path is None or not self.current_path.points:
            return
        if not self._goal_points:
            self._rebuild_goal_points()
        if not self._goal_points:
            return
        if target_index < 0 or target_index >= len(self._goal_points):
            return
        goal = self._goal_points[int(target_index)]
        path_index = int(goal.get("path_index", 0))
        if path_index < 0 or path_index >= len(self.current_path.points):
            return
        endpoint = self.current_path.points[path_index]
        self._apply_disc_state_for_path_point(endpoint)
        quat = goal.get("orientation") if isinstance(goal, dict) else None
        if not isinstance(quat, dict):
            cached_xy = [(float(p.get("x", 0.0)), float(p.get("y", 0.0))) for p in self.current_path.points]
            quat = self._resolve_point_orientation(endpoint, path_index, cached_xy)
        self.goal_pub.publish(self._build_navigation_goal_msg(endpoint, path_index, quat))

    def _apply_disc_state_for_path_point(self, path_point):
        if not bool(self._disc_follow_path_type):
            return
        if not isinstance(path_point, dict):
            return
        path_type = str(path_point.get("path_type", "") or "").strip().lower()
        # connection: transition path between regions -> disc up + disable
        # others: in-region coverage path -> disc down + enable
        target_mode = "transition" if path_type == "connection" else "cover"
        if target_mode == self._disc_last_mode:
            return
        if target_mode == "transition":
            self.disc_enable_pub.publish(Bool(data=False))
            self.disc_lift_pub.publish(UInt16(data=2))
        else:
            self.disc_lift_pub.publish(UInt16(data=1))
            self.disc_enable_pub.publish(Bool(data=True))
        self._disc_last_mode = target_mode
        rospy.loginfo(
            "Disc mode switched by path_type: mode=%s path_type=%s",
            target_mode,
            path_type or "<empty>",
        )

    def _publish_current_position_goal_once(self):
        if self.current_path is None or not self.current_path.points:
            return
        pose = self.aurora_bridge.get_pose()
        nearest_index = 0
        nearest_distance = float("inf")
        for index, point in enumerate(self.current_path.points):
            distance = math.hypot(float(point.get("x", 0.0)) - pose["x"], float(point.get("y", 0.0)) - pose["y"])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_index = index
        self.current_path_index = nearest_index
        endpoint = self.current_path.points[nearest_index]
        cached_xy = [(float(p.get("x", 0.0)), float(p.get("y", 0.0))) for p in self.current_path.points]
        quat = self._resolve_point_orientation(endpoint, int(nearest_index), cached_xy)
        self.goal_pub.publish(self._build_navigation_goal_msg(endpoint, int(nearest_index), quat))

    def _advance_goal_or_finish(self):
        if self.current_path is None or not self.current_path.points:
            return
        if not self._goal_points:
            self._rebuild_goal_points()
        if not self._goal_points:
            return
        if self._exec_goal_index >= len(self._goal_points) - 1:
            self._mark_current_region_repeat_done()
            if self._try_advance_to_next_region():
                return
            self._exec_active = False
            self._set_cmd_vel_forward_runtime_active(False, publish_zero=True, reason="task_complete")
            self.disc_enable_pub.publish(Bool(data=False))
            self.light_pub.publish(Bool(data=False))
            self.disc_lift_pub.publish(UInt16(data=2))
            self._safe_stop_motion()
            self._exec_region_order = []
            self._exec_region_index = -1
            self.state = SchedulerState.COMPLETED
            self._task_stop_reason = "completed"
            self._finalize_task_result(stop_reason="completed")
            rospy.loginfo("Path execution completed: task_id=%s path_version=%s", self.current_path.task_id, self.current_path.path_version)
            return
        self._exec_goal_index += 1
        self._exec_goal_start_time = time.time()
        prev_goal = self._goal_points[max(0, self._exec_goal_index - 1)]
        self.current_path_index = max(
            self.current_path_index,
            int(prev_goal.get("path_index", self.current_path_index)),
        )
        self._dispatch_current_goal(force=True)

    def _try_advance_to_next_region(self):
        if self._current_plan_scope == "all":
            return False
        self._sync_task_regions_from_overlay()
        region_order = self._sorted_work_region_ids()
        if not region_order or len(region_order) <= 1:
            return False
        current_id = (self.task_config.active_work_region_id or "").strip()
        if current_id in region_order:
            current_idx = region_order.index(current_id)
        else:
            current_idx = -1
        next_idx = current_idx + 1
        if next_idx >= len(region_order):
            return False
        next_region_id = region_order[next_idx]

        # Inter-region transfer: retract and stop disc before moving to next region.
        self.disc_enable_pub.publish(Bool(data=False))
        self.disc_lift_pub.publish(UInt16(data=2))
        self.task_config.active_work_region_id = next_region_id
        rospy.loginfo(
            "Switching to next work region: from=%s to=%s (%d/%d)",
            current_id or "<none>",
            next_region_id,
            next_idx + 1,
            len(region_order),
        )
        if not self._plan_current_task():
            rospy.logerr("Failed to plan next work region: %s", next_region_id)
            self._set_error("Planning failed for next work region: {}".format(next_region_id))
            return False
        if self.current_path is None or not self.current_path.points:
            rospy.logerr("Planned path is empty for next work region: %s", next_region_id)
            self._set_error("Empty path for next work region: {}".format(next_region_id))
            return False

        # Enter next region: enable working tool again.
        self._set_chassis_enabled(True)
        self.disc_lift_pub.publish(UInt16(data=1))
        self.disc_speed_pub.publish(Int16(data=1200))
        self.disc_enable_pub.publish(Bool(data=True))
        self.light_pub.publish(Bool(data=True))
        self._exec_region_order = region_order
        self._exec_region_index = next_idx
        self._init_path_execution_cursor()
        self._exec_active = True
        self._exec_last_send_time = 0.0
        self._exec_goal_start_time = time.time()
        self._dispatch_current_goal(force=True)
        return True

    def _tick_path_execution(self):
        if self.state != SchedulerState.RUNNING:
            return
        if not self._exec_active:
            return
        if self.current_path is None or not self.current_path.points:
            self._exec_active = False
            return
        if not self._goal_points:
            self._rebuild_goal_points()
        if not self._goal_points:
            self._exec_active = False
            return
        if self._exec_goal_index < 0 or self._exec_goal_index >= len(self._goal_points):
            self._exec_goal_index = max(0, min(self._exec_goal_index, len(self._goal_points) - 1))
        goal = self._goal_points[self._exec_goal_index]
        pose = self.aurora_bridge.get_pose()
        dist = math.hypot(float(goal.get("x", 0.0)) - pose["x"], float(goal.get("y", 0.0)) - pose["y"])
        if dist <= self._exec_goal_reach_dist:
            self.current_path_index = max(self.current_path_index, int(goal.get("path_index", 0)))
            self._advance_goal_or_finish()
            return
        if (time.time() - self._exec_goal_start_time) > self._exec_segment_timeout:
            rospy.logwarn(
                "Path execution timeout on segment-goal=%d dist=%.3f, republish current segment endpoint",
                int(goal.get("path_index", self._exec_goal_index)),
                dist,
            )
            # Do not advance on timeout; keep current segment goal and republish it.
            self._dispatch_current_goal(force=True)
            self._exec_goal_start_time = time.time()
            return
        self._dispatch_current_goal(force=False)

    def _set_chassis_enabled(self, enabled):
        # Requirement update:
        # chassis enable/disable is no longer controlled by task flow.
        # Keep this function as a no-op for backward compatibility.
        # If re-enabled in future, call with field name `enable` (not `enabled`):
        #   self.enable_service(enable=bool(enabled))
        rospy.loginfo_throttle(
            2.0,
            "Skip chassis enable control by scheduler (requested enabled=%s).",
            str(bool(enabled)),
        )

    def _update_progress(self):
        if self.current_path is None or not self.current_path.points:
            return
        if self.state == SchedulerState.READY:
            self.current_path_index = 0
            return
        pose = self.aurora_bridge.get_pose()
        nearest_index = 0
        nearest_distance = float("inf")
        for index, point in enumerate(self.current_path.points):
            distance = math.hypot(point["x"] - pose["x"], point["y"] - pose["y"])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_index = index
        self.current_path_index = nearest_index
        if self.state == SchedulerState.RUNNING and nearest_index >= len(self.current_path.points) - 1:
            # Task finished: always stop disc rotation and lift disc for safety.
            self._set_cmd_vel_forward_runtime_active(False, publish_zero=True, reason="task_complete_progress")
            self.disc_enable_pub.publish(Bool(data=False))
            self.disc_lift_pub.publish(UInt16(data=2))
            self.state = SchedulerState.COMPLETED
            self._task_stop_reason = "completed"
            self._finalize_task_result(stop_reason="completed")

    def _publish_status(self):
        pose = self.aurora_bridge.get_pose()
        message = SchedulerStatus()
        message.header.stamp = rospy.Time.now()
        message.task_id = self.task_config.task_id
        message.state = self.state.value
        message.progress = self._task_progress()
        map_info = self.map_service.get_map_info()
        message.map_version = map_info["map_version"] if map_info else 0
        message.map_available = map_info is not None
        message.stream_online = self.media_streamer.get_state().online
        message.replan_requested = self.replan_requested
        message.last_error = self.last_error
        message.pose.x = pose["x"]
        message.pose.y = pose["y"]
        message.pose.theta = math.radians(pose["heading_deg"])
        message.path_point_count = len(self.current_path.points) if self.current_path else 0
        self.status_pub.publish(message)

    def _publish_diagnostics(self):
        video_state = self.media_streamer.get_state()
        local_stream_state = self.local_stream_server.get_state()
        local_stream_urls = self.local_stream_server.get_stream_urls()
        status = DiagnosticStatus()
        status.name = "grinder_scheduler"
        status.hardware_id = "scheduler"
        rtsp_available = self.local_stream_server.ffmpeg_available()
        mediamtx_available = self.local_stream_server.mediamtx_available()
        if self.last_error == "" and rtsp_available and mediamtx_available:
            status.level = DiagnosticStatus.OK
            status.message = "ok"
        elif self.last_error == "" and (not rtsp_available or not mediamtx_available):
            status.level = DiagnosticStatus.WARN
            if not rtsp_available:
                status.message = "ffmpeg_not_installed"
            else:
                status.message = "mediamtx_not_installed"
        else:
            status.level = DiagnosticStatus.WARN
            status.message = self.last_error
        status.values = [
            KeyValue(key="state", value=self.state.value),
            KeyValue(key="task_id", value=self.task_config.task_id),
            KeyValue(key="map_available", value=str(self.map_service.has_map())),
            KeyValue(key="stream_online", value=str(video_state.online)),
            KeyValue(key="stream_url", value=video_state.stream_url),
            KeyValue(key="local_stream_online", value=str(local_stream_state.online)),
            KeyValue(key="local_stream_url", value=local_stream_state.stream_url),
            KeyValue(key="local_rtsp_left", value=local_stream_urls["left"]),
            KeyValue(key="local_rtsp_right", value=local_stream_urls["right"]),
            KeyValue(key="local_rtsp_ffmpeg_available", value=str(rtsp_available)),
            KeyValue(key="local_rtsp_mediamtx_available", value=str(mediamtx_available)),
            KeyValue(key="local_rtsp_server_running", value=str(self.local_stream_server.server_running())),
        ]
        array = DiagnosticArray()
        array.header.stamp = rospy.Time.now()
        array.status = [status]
        self.diagnostics_pub.publish(array)

    def _task_progress(self):
        if self.current_path is None or not self.current_path.points:
            return 0.0
        return float(self.current_path_index) / float(max(1, len(self.current_path.points) - 1))

    def _polygon_area_m2(self, points):
        if not points or len(points) < 3:
            return 0.0
        area2 = 0.0
        count = len(points)
        for i in range(count):
            p1 = points[i]
            p2 = points[(i + 1) % count]
            x1 = float(p1.get("x", 0.0))
            y1 = float(p1.get("y", 0.0))
            x2 = float(p2.get("x", 0.0))
            y2 = float(p2.get("y", 0.0))
            area2 += (x1 * y2 - x2 * y1)
        return abs(area2) * 0.5

    def _total_work_area_m2(self):
        total = 0.0
        for region in list(self.task_config.work_regions or []):
            if not isinstance(region, dict):
                continue
            points = region.get("points", []) or []
            if len(points) < 3:
                continue
            total += self._polygon_area_m2(points)
        return max(0.0, total)

    def _record_progress_sample(self, progress):
        now = time.time()
        p = max(0.0, min(1.0, float(progress)))
        self._progress_history.append((now, p))
        cutoff = now - 120.0
        while len(self._progress_history) >= 2 and self._progress_history[0][0] < cutoff:
            self._progress_history.popleft()

    def _estimate_remaining_time_s(self, progress):
        p = max(0.0, min(1.0, float(progress)))
        if p >= 0.999:
            return 0.0
        if len(self._progress_history) < 2:
            return -1.0
        t0, p0 = self._progress_history[0]
        t1, p1 = self._progress_history[-1]
        dt = max(0.0, float(t1 - t0))
        dp = float(p1 - p0)
        if dt < 3.0 or dp <= 1e-4:
            return -1.0
        rate = dp / dt
        if rate <= 1e-6:
            return -1.0
        remaining = max(0.0, 1.0 - p)
        return remaining / rate

    def _estimate_plan_time_s(self, path_length_m):
        try:
            length = max(0.0, float(path_length_m))
            # Rough ETA from path length and effective cruise speed.
            # Use ~70% of max linear speed to account for turns/slowdown.
            effective_speed = max(0.05, float(self._exec_max_linear) * 0.7)
            return length / effective_speed
        except Exception:
            return -1.0

    def _compute_saved_map_metrics(self):
        """Compute map-level task metadata persisted with saved map records."""
        total_area_m2 = float(self._total_work_area_m2())
        estimated_time_s = -1.0
        if self.current_path is not None:
            try:
                estimated_time_s = float(self._estimate_plan_time_s(self.current_path.length_m))
            except Exception:
                estimated_time_s = -1.0
        return total_area_m2, estimated_time_s

    def _compute_saved_region_metrics(self, total_estimated_time_s):
        metrics = []
        regions = list(self.task_config.work_regions or [])
        if not regions:
            return metrics
        per_region_area = []
        total_area_m2 = 0.0
        for region in regions:
            if not isinstance(region, dict):
                continue
            rid = str(region.get("region_id", "") or "").strip()
            name = str(region.get("name", "") or rid)
            points = list(region.get("points", []) or [])
            area = float(self._polygon_area_m2(points))
            repeat = 1
            if rid:
                try:
                    repeat = max(1, int((self.task_config.region_repeat_config or {}).get(rid, 1)))
                except Exception:
                    repeat = 1
            effective_area = max(0.0, area) * float(repeat)
            if effective_area <= 0.0:
                continue
            per_region_area.append((rid, name, repeat, effective_area))
            total_area_m2 += effective_area
        if total_area_m2 <= 0.0:
            return metrics

        for rid, name, repeat, area_m2 in per_region_area:
            if total_estimated_time_s is not None and float(total_estimated_time_s) >= 0.0:
                est_h = (float(total_estimated_time_s) * (area_m2 / total_area_m2)) / 3600.0
            else:
                est_h = -1.0
            metrics.append(
                {
                    "region_id": rid,
                    "region_name": name,
                    "repeat": int(repeat),
                    "area_m2": float(area_m2),
                    "estimated_time_h": float(est_h),
                }
            )
        return metrics

    def _build_saved_map_thumbnail(self):
        """Return (image_format, image_b64, width, height) for saved-map metadata."""
        try:
            snapshot = self.map_service.create_preview(
                self.aurora_bridge.get_pose(),
                int(self._saved_map_thumb_max_edge),
                "jpg",
                True,
                **self._map_preview_alignment_kwargs()
            )
            raw = bytes(snapshot.preview_data or b"")
            if not raw:
                return ("", "", 0, 0)
            arr = np.frombuffer(raw, dtype=np.uint8)
            image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if image is None:
                return ("", "", 0, 0)
            ok, enc = cv2.imencode(
                ".jpg",
                image,
                [int(cv2.IMWRITE_JPEG_QUALITY), int(self._saved_map_thumb_jpeg_quality)],
            )
            if not ok:
                return ("", "", 0, 0)
            encoded = bytes(enc.tobytes())
            return (
                "jpg",
                base64.b64encode(encoded).decode("ascii"),
                int(image.shape[1]),
                int(image.shape[0]),
            )
        except Exception as exc:
            rospy.logwarn("Failed to build saved-map thumbnail: %s", exc)
            return ("", "", 0, 0)

    def _set_error(self, message):
        self.last_error = message
        self._mark_current_region_repeat_done()
        self._set_cmd_vel_forward_runtime_active(False, publish_zero=True, reason="scheduler_error")
        self.state = SchedulerState.ERROR
        self._task_stop_reason = str(message or "error")
        self._finalize_task_result(stop_reason=self._task_stop_reason)
        rospy.logerr("Scheduler entered ERROR: %s", message)

    def _task_state_to_pb(self):
        pb = self.sl_link_server.pb
        mapping = {
            SchedulerState.IDLE: pb.TASK_STATE_IDLE,
            SchedulerState.READY: pb.TASK_STATE_READY,
            SchedulerState.PLANNING: pb.TASK_STATE_PLANNING,
            SchedulerState.RUNNING: pb.TASK_STATE_RUNNING,
            SchedulerState.PAUSED: pb.TASK_STATE_PAUSED,
            SchedulerState.COMPLETED: pb.TASK_STATE_COMPLETED,
            SchedulerState.STOPPED: pb.TASK_STATE_STOPPED,
            SchedulerState.ERROR: pb.TASK_STATE_ERROR,
        }
        return mapping[self.state]

    def build_device_status_report(self):
        pb = self.sl_link_server.pb
        report = pb.DeviceStatusReport()
        report.utc_time = int(time.time())
        report.system_status = pb.SYS_STATUS_ERROR if self.last_error else pb.SYS_STATUS_NORMAL
        report.wifi_status = pb.WIFI_SUCCESS
        report.work_mode = pb.WORK_MODE_AUTO if self.state in (SchedulerState.RUNNING, SchedulerState.READY) else pb.WORK_MODE_MANUAL
        if self.last_chassis_status is not None:
            report.disc_speed_rpm = max(0, int(self.last_chassis_status.disc_speed_feedback))
            report.disc_enabled = self.last_chassis_status.disc_enabled
            report.light_enabled = self.last_chassis_status.light_enabled
            report.chassis_enabled = self.last_chassis_status.enabled
        pose = self.aurora_bridge.get_pose()
        report.position.x = pose["x"]
        report.position.y = pose["y"]
        report.position.heading_deg = pose["heading_deg"]
        return report.SerializeToString(), pb.MSG_ID_DEVICE_STATUS_REPORT, pb.COMP_SYSTEM

    def build_task_status_report(self):
        pb = self.sl_link_server.pb
        report = pb.TaskStatusReport()
        report.task_id = self.task_config.task_id
        report.state = self._task_state_to_pb()
        progress = self._task_progress()
        self._record_progress_sample(progress)
        report.progress = progress
        map_info = self.map_service.get_map_info()
        report.map_version = map_info["map_version"] if map_info else 0
        report.message = self.last_error or self.state.value
        pose = self.aurora_bridge.get_pose()
        report.position.x = pose["x"]
        report.position.y = pose["y"]
        report.position.heading_deg = pose["heading_deg"]
        report.replan_requested = self.replan_requested
        report.path_point_count = len(self.current_path.points) if self.current_path else 0
        report.path_version = self.current_path.path_version if self.current_path else 0
        total_area = self._total_work_area_m2()
        remaining_area = max(0.0, total_area * (1.0 - progress))
        report.total_work_area_m2 = float(total_area)
        report.remaining_work_area_m2 = float(remaining_area)
        report.remaining_time_s = float(self._estimate_remaining_time_s(progress))
        region_id, repeat_index, repeat_total = self._current_region_repeat_progress()
        report.current_region_id = region_id
        report.current_region_repeat_index = int(repeat_index)
        report.current_region_repeat_total = int(repeat_total)
        return report.SerializeToString(), pb.MSG_ID_TASK_STATUS_REPORT, pb.COMP_SCHEDULER

    def _current_region_repeat_progress(self):
        active_id = str(self.task_config.active_work_region_id or "").strip()
        if not active_id:
            return "", 0, 0
        base_id = active_id
        repeat_index = 1
        if "__lap_" in active_id:
            prefix, _, suffix = active_id.rpartition("__lap_")
            if prefix:
                base_id = prefix
            try:
                repeat_index = max(1, int(suffix))
            except Exception:
                repeat_index = 1
        repeat_total = 1
        try:
            repeat_total = max(1, int((self.task_config.region_repeat_config or {}).get(base_id, 1)))
        except Exception:
            repeat_total = 1
        if repeat_index > repeat_total:
            repeat_index = repeat_total
        return base_id, repeat_index, repeat_total

    def _split_region_repeat(self, region_id_text):
        raw = str(region_id_text or "").strip()
        if not raw:
            return "", 1
        if "__lap_" not in raw:
            return raw, 1
        prefix, _, suffix = raw.rpartition("__lap_")
        base = prefix.strip() or raw
        try:
            lap = max(1, int(suffix))
        except Exception:
            lap = 1
        return base, lap

    def _mark_current_region_repeat_done(self):
        base_id, repeat_index, _ = self._current_region_repeat_progress()
        if not base_id:
            return
        old = int(self._exec_region_repeat_done.get(base_id, 0) or 0)
        if repeat_index > old:
            self._exec_region_repeat_done[base_id] = int(repeat_index)

    def _build_task_result_image(self):
        if self.current_path is None or not self.current_path.points:
            return "", b"", 0, 0
        try:
            alignment_kwargs = self._map_preview_alignment_kwargs()
            alignment_yaw = alignment_kwargs.get("alignment_yaw", None)
            snapshot = self.map_service.create_preview(
                None,
                self._planned_path_preview_max_edge,
                self._planned_path_preview_format,
                False,
                **alignment_kwargs
            )
            image = cv2.imdecode(np.frombuffer(snapshot.preview_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                return "", b"", 0, 0
            render_map_info = {
                "width": int(snapshot.width),
                "height": int(snapshot.height),
                "origin_x": float(snapshot.origin_x),
                "origin_y": float(snapshot.origin_y),
                "resolution": float(snapshot.resolution),
                "alignment_yaw": alignment_yaw,
            }
            preview_h, preview_w = image.shape[:2]
            scale_x = float(preview_w) / float(max(1, render_map_info["width"]))
            scale_y = float(preview_h) / float(max(1, render_map_info["height"]))

            def _to_px(path_point):
                return self._map_point_to_preview_pixel(
                    path_point,
                    render_map_info,
                    scale_x,
                    scale_y,
                    preview_w,
                    preview_h,
                )

            # Draw all work-region boundaries in task-result image for clearer context.
            for region in list(self.task_config.work_regions or []):
                if not isinstance(region, dict):
                    continue
                pts = list(region.get("points", []) or [])
                if len(pts) < 3:
                    continue
                poly = np.array([_to_px(p) for p in pts], dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(image, [poly], True, (0, 200, 0), thickness=2, lineType=cv2.LINE_AA)

            path_points = list(self.current_path.points or [])
            if len(path_points) < 2:
                return "", b"", 0, 0
            visited_end = int(max(1, min(len(path_points) - 1, int(self.current_path_index or 0))))
            for i in range(1, visited_end + 1):
                p0 = path_points[i - 1]
                p1 = path_points[i]
                seg_type = str(p1.get("path_type", "") or "")
                if seg_type == "connection":
                    # 区域间两点连接路径：固定青色
                    color = (255, 255, 0)
                else:
                    # 区域覆盖路径：按遍数配色
                    _, lap = self._split_region_repeat(seg_type)
                    color = self._task_result_palette_bgr[(max(1, lap) - 1) % len(self._task_result_palette_bgr)]
                cv2.line(image, _to_px(p0), _to_px(p1), color, thickness=2, lineType=cv2.LINE_AA)

            ext = ".png" if snapshot.preview_format.lower() == "png" else ".jpg"
            ok, buffer = cv2.imencode(ext, image)
            if not ok:
                return "", b"", 0, 0
            return str(snapshot.preview_format or "jpg"), bytes(buffer.tobytes()), int(preview_w), int(preview_h)
        except Exception as exc:
            rospy.logwarn("Failed to build task result image: %s", exc)
            return "", b"", 0, 0

    def _finalize_task_result(self, stop_reason=""):
        try:
            map_id = str(self._current_map_id() or self.task_config.map_id or "").strip()
            task_id = str(self.task_config.task_id or "task").strip() or "task"
            if not map_id:
                return
            self._mark_current_region_repeat_done()
            region_results = []
            all_completed = True
            selected = list(self._effective_selected_work_region_ids(list(self.task_config.work_regions or [])) or [])
            name_by_id = {}
            for region in list(self.task_config.work_regions or []):
                if not isinstance(region, dict):
                    continue
                rid = str(region.get("region_id", "")).strip()
                if rid:
                    name_by_id[rid] = str(region.get("name", "") or rid)
            for rid in selected:
                target_repeat = max(1, int((self.task_config.region_repeat_config or {}).get(rid, 1)))
                executed_repeat = max(0, min(target_repeat, int(self._exec_region_repeat_done.get(rid, 0) or 0)))
                completed = bool(executed_repeat >= target_repeat)
                if not completed:
                    all_completed = False
                region_results.append(
                    {
                        "region_id": rid,
                        "region_name": name_by_id.get(rid, rid),
                        "target_repeat": int(target_repeat),
                        "executed_repeat": int(executed_repeat),
                        "completed": bool(completed),
                        "unfinished_reason": "" if completed else str(stop_reason or self.last_error or "not_finished"),
                    }
                )
            image_format, image_data, image_width, image_height = self._build_task_result_image()
            key = "{}::{}".format(map_id, task_id)
            record = self._task_bindings.get(key, {}) if isinstance(self._task_bindings.get(key, {}), dict) else {}
            record.update(
                {
                    "task_id": task_id,
                    "map_id": map_id,
                    "selected_work_region_ids": list(self.task_config.selected_work_region_ids or selected),
                    "region_repeat_config": dict(self.task_config.region_repeat_config or {}),
                    "active_work_region_id": self.task_config.active_work_region_id or "",
                    "updated_at": int(time.time()),
                    "task_result": {
                        "map_id": map_id,
                        "task_id": task_id,
                        "final_state": str(self.state.value),
                        "all_completed": bool(all_completed),
                        "stop_reason": str(stop_reason or self.last_error or ""),
                        "path_version": int(self.current_path.path_version if self.current_path is not None else 0),
                        "finished_at": int(time.time()),
                        "selected_work_region_ids": list(self.task_config.selected_work_region_ids or selected),
                        "region_results": region_results,
                        "image_format": str(image_format or ""),
                        "image_b64": base64.b64encode(image_data).decode("ascii") if image_data else "",
                        "image_width": int(image_width),
                        "image_height": int(image_height),
                    },
                }
            )
            self._task_bindings[key] = record
            self._last_task_result = dict(record.get("task_result", {}) or {})
            self._save_local_state()
        except Exception as exc:
            rospy.logwarn("Failed to finalize task result: %s", exc)

    def handle_settings_read_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.SettingsReadRequest()
        request.ParseFromString(payload)
        response = pb.SettingsReadResponse()
        response.result = pb.RESULT_SUCCESS
        response.message = "Settings read success"
        if request.read_chassis:
            status = self.last_chassis_status
            response.chassis.run_speed = float(self._chassis_settings.get("run_speed", 0.4))
            response.chassis.disc_speed_rpm = max(0, int(self._chassis_settings.get("disc_speed_rpm", 1200)))
            saved_mode = int(self._chassis_settings.get("work_mode", 1))
            response.chassis.work_mode = pb.WORK_MODE_MANUAL if saved_mode == 2 else pb.WORK_MODE_AUTO
            response.chassis.disc_enabled = bool(status.disc_enabled) if status is not None else False
        if request.read_map:
            try:
                self._reload_robot_config_from_yaml()
            except Exception as exc:
                rospy.logwarn("Failed to realtime-load robot config from yaml %s: %s", self._robot_config_yaml_path, exc)
            response.map.vehicle_width = float(self.task_config.vehicle_width)
            response.map.vehicle_length = float(self.task_config.vehicle_length)
            response.map.default_path_spacing = self.task_config.default_path_spacing
            response.map.turn_radius = self.task_config.turn_radius
            response.map.overlap_ratio = self.task_config.overlap_ratio
            response.map.inflation_radius = self.task_config.inflation_radius
            for region in self.map_service.get_overlay_regions()["obstacle_regions"]:
                pb_region = response.map.obstacle_regions.add()
                pb_region.name = region["name"]
                pb_region.region_id = region.get("region_id", "")
                pb_region.priority = int(region.get("order_index", region.get("priority", 0)))
                pb_region.enabled = bool(region.get("enabled", True))
                pb_region.color_argb = int(region.get("color_argb", 0))
                pb_region.closed = bool(region.get("closed", True))
                pb_region.region_type = int(region.get("region_type", pb.REGION_TYPE_OBSTACLE))
                for point in region["points"]:
                    pb_point = pb_region.points.add()
                    pb_point.x = point["x"]
                    pb_point.y = point["y"]
            for region in self.map_service.get_overlay_regions()["work_regions"]:
                pb_region = response.map.work_regions.add()
                pb_region.name = region["name"]
                pb_region.region_id = region.get("region_id", "")
                pb_region.priority = int(region.get("order_index", region.get("priority", 0)))
                pb_region.enabled = bool(region.get("enabled", True))
                pb_region.color_argb = int(region.get("color_argb", 0))
                pb_region.closed = bool(region.get("closed", True))
                pb_region.region_type = int(region.get("region_type", pb.REGION_TYPE_WORK))
                for point in region["points"]:
                    pb_point = pb_region.points.add()
                    pb_point.x = point["x"]
                    pb_point.y = point["y"]
        return response.SerializeToString(), pb.MSG_ID_SETTINGS_READ_RESPONSE, pb.COMP_SETTINGS

    def handle_settings_write_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.SettingsWriteRequest()
        request.ParseFromString(payload)
        if request.HasField("chassis"):
            work_mode = int(request.chassis.work_mode)
            if work_mode == int(pb.WORK_MODE_AUTO):
                self.work_mode_pub.publish(UInt16(data=1))
                self._chassis_settings["work_mode"] = 1
            elif work_mode == int(pb.WORK_MODE_MANUAL):
                self.work_mode_pub.publish(UInt16(data=2))
                self._chassis_settings["work_mode"] = 2
            disc_speed = int(request.chassis.disc_speed_rpm)
            disc_speed = max(-32768, min(32767, disc_speed))
            self.disc_speed_pub.publish(Int16(data=disc_speed))
            self._chassis_settings["disc_speed_rpm"] = int(max(0, disc_speed))
            self.disc_enable_pub.publish(Bool(data=bool(request.chassis.disc_enabled)))
            if float(request.chassis.run_speed) > 0.0:
                self._chassis_settings["run_speed"] = float(request.chassis.run_speed)
            self._save_local_state()
        if request.HasField("map"):
            if request.map.vehicle_width > 0.0:
                self.task_config.vehicle_width = float(request.map.vehicle_width)
            if request.map.vehicle_length > 0.0:
                self.task_config.vehicle_length = float(request.map.vehicle_length)
            self.task_config.default_path_spacing = request.map.default_path_spacing or self.task_config.default_path_spacing
            self.task_config.turn_radius = request.map.turn_radius or self.task_config.turn_radius
            self.task_config.overlap_ratio = request.map.overlap_ratio
            self.task_config.inflation_radius = request.map.inflation_radius or self.task_config.inflation_radius
            for region in request.map.work_regions:
                self.map_service.apply_edit(
                    {
                        "operation": "UPSERT_WORK_REGION",
                        "region": {
                            "name": region.name,
                            "points": [{"x": p.x, "y": p.y} for p in region.points],
                            "region_id": region.region_id,
                            "priority": int(region.priority),
                            "enabled": bool(region.enabled),
                            "color_argb": int(region.color_argb),
                            "closed": bool(region.closed),
                            "region_type": int(region.region_type) if int(region.region_type) != 0 else int(pb.REGION_TYPE_WORK),
                        },
                    }
                )
            for region in request.map.obstacle_regions:
                self.map_service.apply_edit(
                    {
                        "operation": "UPSERT_OBSTACLE_REGION",
                        "region": {
                            "name": region.name,
                            "points": [{"x": p.x, "y": p.y} for p in region.points],
                            "region_id": region.region_id,
                            "priority": int(region.priority),
                            "enabled": bool(region.enabled),
                            "color_argb": int(region.color_argb),
                            "closed": bool(region.closed),
                            "region_type": int(region.region_type) if int(region.region_type) != 0 else int(pb.REGION_TYPE_OBSTACLE),
                        },
                    }
                )
            try:
                self._sync_robot_config_to_yaml()
            except Exception as exc:
                rospy.logwarn("Failed to sync robot config to yaml %s: %s", self._robot_config_yaml_path, exc)
            self._save_local_state()
        response = pb.SettingsWriteResponse()
        response.result = pb.RESULT_SUCCESS
        response.message = "Settings applied"
        if request.HasField("chassis"):
            response.chassis.CopyFrom(request.chassis)
        return response.SerializeToString(), pb.MSG_ID_SETTINGS_WRITE_RESPONSE, pb.COMP_SETTINGS

    def handle_control_command(self, payload):
        pb = self.sl_link_server.pb
        request = pb.ControlCommand()
        request.ParseFromString(payload)
        control_fields = set(getattr(request, "DESCRIPTOR").fields_by_name.keys())
        has_disc_control = "disc_control" in control_fields
        has_emergency_stop = "emergency_stop" in control_fields
        handled = False
        error_message = ""
        if request.HasField("disc_lift"):
            self.disc_lift_pub.publish(UInt16(data=2 if request.disc_lift.command == pb.DISC_LIFT_CMD_UP else 1))
            handled = True
        elif has_disc_control and request.HasField("disc_control"):
            if bool(request.disc_control.enabled):
                # Disc outputs are ignored by chassis driver when disabled.
                # Enable chassis first to make sure disc command reaches RS485 writes.
                self._set_chassis_enabled(True)
            disc_speed = int(request.disc_control.speed_rpm)
            disc_speed = max(-32768, min(32767, disc_speed))
            self.disc_speed_pub.publish(Int16(data=disc_speed))
            self.disc_enable_pub.publish(Bool(data=bool(request.disc_control.enabled)))
            handled = True
        elif request.HasField("lighting"):
            self.light_pub.publish(Bool(data=request.lighting.enabled))
            handled = True
        elif request.HasField("manual_drive"):
            self._handle_manual_drive(
                request.manual_drive.motion,
                request.manual_drive.speed_ratio,
                request.manual_drive.remote_x,
                request.manual_drive.remote_y,
            )
            handled = True
        elif has_emergency_stop and request.HasField("emergency_stop"):
            self._apply_emergency_stop(bool(request.emergency_stop.enabled))
            handled = True
        elif request.HasField("chassis_power"):
            self._set_chassis_enabled(request.chassis_power.enabled)
            handled = True
        else:
            error_message = "Unsupported or empty ControlCommand"
        response = pb.ControlCommandResponse()
        response.result = pb.RESULT_SUCCESS if handled else pb.RESULT_UNSUPPORTED
        response.message = "Control applied" if handled else error_message
        response.applied_command.CopyFrom(request)
        return response.SerializeToString(), pb.MSG_ID_CONTROL_COMMAND_RESPONSE, pb.COMP_CONTROL

    def _apply_emergency_stop(self, enabled):
        if not bool(enabled):
            rospy.loginfo("EmergencyStopControl received with enabled=false, ignored.")
            return
        # Emergency stop sequence:
        # 1) publish zero wheel speeds immediately
        # 2) disable disc output
        # 3) cut chassis enable
        wheel = WheelSpeedCommand()
        wheel.left_wheel_speed = 0
        wheel.right_wheel_speed = 0
        self.wheel_cmd_pub.publish(wheel)
        self.disc_enable_pub.publish(Bool(data=False))
        self._set_chassis_enabled(False)
        rospy.logwarn("Emergency stop applied: wheels=0, disc=off, chassis_disabled.")

    def _handle_manual_drive(self, motion, speed_ratio, remote_x=0.0, remote_y=0.0):
        base_max = int(self._manual_drive_base_speed)
        base = int(max(0.0, min(1.0, speed_ratio)) * base_max)
        wheel = WheelSpeedCommand()
        use_remote = abs(float(remote_x)) > 1e-3 or abs(float(remote_y)) > 1e-3
        if use_remote:
            x = max(-1.0, min(1.0, float(remote_x)))
            y = max(-1.0, min(1.0, float(remote_y)))
            if base <= 0:
                base = base_max
            # Use joystick Cartesian quadrant direction directly:
            # positive y means forward, negative y means backward.
            linear = y * float(base)
            angular = x * float(base)
            left = int(round(linear - angular))
            right = int(round(linear + angular))
            wheel.left_wheel_speed = int(max(-base_max, min(base_max, left)))
            wheel.right_wheel_speed = int(max(-base_max, min(base_max, right)))
        elif motion == self.sl_link_server.pb.MANUAL_MOTION_FORWARD:
            wheel.left_wheel_speed = base
            wheel.right_wheel_speed = base
        elif motion == self.sl_link_server.pb.MANUAL_MOTION_BACKWARD:
            wheel.left_wheel_speed = -base
            wheel.right_wheel_speed = -base
        elif motion == self.sl_link_server.pb.MANUAL_MOTION_FORWARD_LEFT:
            wheel.left_wheel_speed = int(base * 0.5)
            wheel.right_wheel_speed = base
        elif motion == self.sl_link_server.pb.MANUAL_MOTION_FORWARD_RIGHT:
            wheel.left_wheel_speed = base
            wheel.right_wheel_speed = int(base * 0.5)
        elif motion == self.sl_link_server.pb.MANUAL_MOTION_BACKWARD_LEFT:
            wheel.left_wheel_speed = int(-base * 0.5)
            wheel.right_wheel_speed = -base
        elif motion == self.sl_link_server.pb.MANUAL_MOTION_BACKWARD_RIGHT:
            wheel.left_wheel_speed = -base
            wheel.right_wheel_speed = int(-base * 0.5)
        else:
            wheel.left_wheel_speed = 0
            wheel.right_wheel_speed = 0
        now = time.time()
        next_left = int(wheel.left_wheel_speed)
        next_right = int(wheel.right_wheel_speed)
        reverse_switch = (
            (
                abs(self._manual_last_left_cmd) > 0
                and abs(next_left) > 0
                and ((self._manual_last_left_cmd > 0 and next_left < 0) or (self._manual_last_left_cmd < 0 and next_left > 0))
            )
            or (
                abs(self._manual_last_right_cmd) > 0
                and abs(next_right) > 0
                and (
                    (self._manual_last_right_cmd > 0 and next_right < 0)
                    or (self._manual_last_right_cmd < 0 and next_right > 0)
                )
            )
        )
        # Protect the motor driver from immediate direction reversal:
        # on sign flip, force one short zero-speed dwell before allowing reverse.
        if self._manual_reverse_guard_sec > 0.0:
            if reverse_switch:
                self._manual_reverse_until = now + self._manual_reverse_guard_sec
                wheel.left_wheel_speed = 0
                wheel.right_wheel_speed = 0
                rospy.logwarn_throttle(
                    1.0,
                    "Manual reverse switch detected, applying %.0fms stop guard."
                    % (self._manual_reverse_guard_sec * 1000.0),
                )
            elif now < self._manual_reverse_until and (abs(next_left) > 0 or abs(next_right) > 0):
                wheel.left_wheel_speed = 0
                wheel.right_wheel_speed = 0
        # If manual drive sends non-zero motion while chassis is disabled,
        # try to re-enable chassis automatically to avoid "no RS485 output" confusion.
        moving = abs(int(wheel.left_wheel_speed)) > 0 or abs(int(wheel.right_wheel_speed)) > 0
        chassis_enabled = bool(self.last_chassis_status.enabled) if self.last_chassis_status is not None else False
        if moving and not chassis_enabled:
            if now - self._last_manual_enable_try > 1.0:
                self._last_manual_enable_try = now
                self._set_chassis_enabled(True)
        self.wheel_cmd_pub.publish(wheel)
        self._manual_last_left_cmd = int(wheel.left_wheel_speed)
        self._manual_last_right_cmd = int(wheel.right_wheel_speed)

    def handle_task_config(self, payload):
        pb = self.sl_link_server.pb
        request = pb.TaskConfig()
        request.ParseFromString(payload)
        map_id_ok, current_map_id = self._validate_requested_map_id(getattr(request, "map_id", ""), "TaskConfig")
        if not map_id_ok:
            response = pb.TaskConfigResponse()
            response.result = pb.RESULT_INVALID_PARAM
            response.message = "map_id mismatch with current map"
            response.task_id = request.task_id or "task"
            return response.SerializeToString(), pb.MSG_ID_TASK_CONFIG_RESPONSE, pb.COMP_SCHEDULER
        self.task_config = TaskConfigModel(
            task_id=request.task_id or "task",
            map_id=current_map_id,
            work_regions=[
                {
                    "region_id": region.region_id,
                    "name": region.name,
                    "points": [{"x": p.x, "y": p.y} for p in region.points],
                }
                for region in request.work_regions
            ],
            obstacle_regions=[
                {
                    "region_id": region.region_id,
                    "name": region.name,
                    "points": [{"x": p.x, "y": p.y} for p in region.points],
                }
                for region in request.obstacle_regions
            ],
            erase_regions=[],
            active_work_region_id=(request.work_regions[0].region_id if len(request.work_regions) > 0 else ""),
            selected_work_region_ids=[
                str(rid).strip()
                for rid in list(getattr(request, "selected_work_region_ids", []) or [])
                if str(rid).strip()
            ]
            or [region.region_id for region in request.work_regions if str(region.region_id).strip()],
            region_repeat_config={
                str(item.region_id).strip(): max(1, int(item.repeat))
                for item in list(getattr(request, "region_repeats", []) or [])
                if str(getattr(item, "region_id", "")).strip()
            },
            vehicle_width=self.task_config.vehicle_width,
            vehicle_length=self.task_config.vehicle_length,
            default_path_spacing=request.default_path_spacing or self.task_config.default_path_spacing,
            global_direction=self.task_config.global_direction or "x",
            turn_radius=request.turn_radius or self.task_config.turn_radius,
            overlap_ratio=request.overlap_ratio or self.task_config.overlap_ratio,
            inflation_radius=request.inflation_radius or self.task_config.inflation_radius,
        )
        for region in self.task_config.work_regions:
            self.map_service.apply_edit({"operation": "UPSERT_WORK_REGION", "region": region})
        for region in self.task_config.obstacle_regions:
            self.map_service.apply_edit({"operation": "UPSERT_OBSTACLE_REGION", "region": region})
        self._sync_task_regions_from_overlay()
        self._sync_task_map_binding(update_binding=True)
        self._save_local_state()
        self._plan_current_task()
        response = pb.TaskConfigResponse()
        response.result = pb.RESULT_SUCCESS
        response.message = "Task config accepted"
        response.task_id = self.task_config.task_id
        return response.SerializeToString(), pb.MSG_ID_TASK_CONFIG_RESPONSE, pb.COMP_SCHEDULER

    def handle_task_command(self, payload):
        pb = self.sl_link_server.pb
        request = pb.TaskCommand()
        request.ParseFromString(payload)
        response = pb.TaskCommandResponse()
        response.task_id = request.task_id or self.task_config.task_id
        if request.command == pb.TASK_CMD_START:
            success, message = self._start_execution()
        elif request.command == pb.TASK_CMD_PAUSE:
            success, message = self._pause_execution()
        elif request.command == pb.TASK_CMD_RESUME:
            success, message = self._resume_execution()
        else:
            success, message = self._stop_execution()
        response.result = pb.RESULT_SUCCESS if success else pb.RESULT_FAILED
        response.message = message
        return response.SerializeToString(), pb.MSG_ID_TASK_COMMAND_RESPONSE, pb.COMP_SCHEDULER

    def build_task_path_chunks(self, payload):
        pb = self.sl_link_server.pb
        request = pb.TaskPathRequest()
        request.ParseFromString(payload)
        path_json = json.dumps(
            {
                "task_id": self.task_config.task_id,
                "path_version": self.current_path.path_version if self.current_path else 0,
                "points": self.current_path.points if self.current_path else [],
            },
            ensure_ascii=False,
        ).encode("utf-8")
        chunk_size = max(256, min(4096, request.max_chunk_size or 2048))
        total = max(1, int(math.ceil(len(path_json) / float(chunk_size))))
        chunks = []
        for index in range(total):
            chunk = pb.TaskPathChunk()
            chunk.task_id = self.task_config.task_id
            chunk.chunk_index = index
            chunk.total_chunks = total
            chunk.path_version = self.current_path.path_version if self.current_path else 0
            chunk.data = path_json[index * chunk_size : (index + 1) * chunk_size]
            chunks.append((chunk.SerializeToString(), pb.MSG_ID_TASK_PATH_CHUNK, pb.COMP_SCHEDULER))
        return chunks

    def build_camera_frame_chunks(self, payload):
        pb = self.sl_link_server.pb
        request = pb.CameraFrameRequest()
        request.ParseFromString(payload)
        chunk_size = max(256, min(4096, int(request.max_chunk_size or 1024)))
        left, right, _, _ = self.aurora_bridge.get_latest_frames()
        frames = [("left", left), ("right", right)]
        outputs = []
        now_utc = int(time.time())
        for side, frame in frames:
            if frame is None:
                continue
            ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if not ok:
                continue
            data = encoded.tobytes()
            total = max(1, int(math.ceil(len(data) / float(chunk_size))))
            side_frame_id = 1 if side == "left" else 2
            for index in range(total):
                chunk = pb.CameraFrameChunk()
                chunk.frame_id = side_frame_id
                chunk.utc_time = now_utc
                chunk.width = int(frame.shape[1])
                chunk.height = int(frame.shape[0])
                chunk.codec = pb.CAMERA_CODEC_JPEG
                chunk.chunk_index = index
                chunk.total_chunks = total
                chunk.data = data[index * chunk_size : (index + 1) * chunk_size]
                outputs.append((chunk.SerializeToString(), pb.MSG_ID_CAMERA_FRAME_CHUNK, pb.COMP_MEDIA))
        return outputs

    def build_map_chunks(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapRequest()
        request.ParseFromString(payload)
        raw_map = self.aurora_bridge.get_map()
        if raw_map is None:
            rospy.logwarn_throttle(2.0, "MapRequest received but raw map is unavailable")
            return []

        # Keep chunk size compatible with legacy protocol max payload.
        chunk_size = int(request.max_chunk_size) if request.max_chunk_size else 512
        chunk_size = max(64, min(512, chunk_size))

        info = raw_map.info
        width = int(info.width)
        height = int(info.height)
        resolution = float(info.resolution)
        origin_x = float(info.origin.position.x)
        origin_y = float(info.origin.position.y)
        frame_id = str(raw_map.header.frame_id)
        grid = np.array(raw_map.data, dtype=np.int16).reshape((height, width))
        yaw = self._lookup_live_map_alignment_yaw() if self._live_map_align_to_initial_yaw else None
        if yaw is not None:
            frame_id = self._live_map_aligned_frame
            if abs(float(yaw)) > 1e-6:
                grid, origin_x, origin_y = self._rotate_grid_to_aligned_frame(
                    grid, origin_x, origin_y, resolution, float(yaw)
                )
                height, width = grid.shape[:2]

        # Default to image payload for Android-friendly rendering.
        # Fallback: set ~map_request_encoding:=grid to output raw OccupancyGrid bytes.
        if self._map_request_encoding in ("grid", "occupancy", "occupancy_grid"):
            encoding = pb.MAP_ENCODING_OCCUPANCY_GRID
            data = grid.astype(np.int8).tobytes()
        else:
            encoding = pb.MAP_ENCODING_PNG
            image = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.uint8)
            image[:, :] = (180, 180, 180)
            image[grid == 0] = (245, 245, 245)
            image[grid >= 100] = (45, 45, 45)
            image = cv2.flip(image, 0)
            ok, buffer = cv2.imencode(".png", image)
            if not ok:
                rospy.logwarn("MapRequest PNG encode failed, fallback to OccupancyGrid bytes")
                encoding = pb.MAP_ENCODING_OCCUPANCY_GRID
                data = grid.astype(np.int8).tobytes()
            else:
                data = buffer.tobytes()
        total = max(1, int(math.ceil(len(data) / float(chunk_size))))
        map_info = self.map_service.get_map_info() or {}
        map_version = int(map_info.get("map_version", 0))
        if map_version > 0:
            base_map_id = map_version
        else:
            # map_version is often 0 when only raw map is used.
            # Fallback to a stable non-zero id generated from stamp or map data.
            stamp = raw_map.header.stamp
            stamp_ms = int(getattr(stamp, "secs", 0)) * 1000 + int(getattr(stamp, "nsecs", 0)) // 1000000
            if stamp_ms > 0:
                base_map_id = stamp_ms & 0xFFFFFFFF
            else:
                base_map_id = zlib.crc32(data) & 0xFFFFFFFF
        identity = "{}|{}|{}|{:.9f}|{:.9f}|{:.9f}|{:.9f}".format(
            frame_id,
            int(width),
            int(height),
            float(resolution),
            float(origin_x),
            float(origin_y),
            float(yaw) if yaw is not None else 0.0,
        )
        map_id = zlib.crc32("{}|{}".format(int(base_map_id), identity).encode("utf-8")) & 0xFFFFFFFF
        if map_id == 0:
            map_id = 1
        now_utc = int(time.time())

        outputs = []
        for index in range(total):
            chunk = pb.MapChunk()
            chunk.map_id = map_id
            chunk.utc_time = now_utc
            chunk.encoding = encoding
            chunk.width = int(width)
            chunk.height = int(height)
            chunk.resolution = float(resolution)
            chunk.origin.x = float(origin_x)
            chunk.origin.y = float(origin_y)
            chunk.origin.heading_deg = 0.0
            chunk.frame_id = frame_id
            chunk.preview_scale_x = 1.0
            chunk.preview_scale_y = 1.0
            chunk.chunk_index = index
            chunk.total_chunks = total
            chunk.data = data[index * chunk_size : (index + 1) * chunk_size]
            outputs.append((chunk.SerializeToString(), pb.MSG_ID_MAP_CHUNK, pb.COMP_MEDIA))
        return outputs

    def handle_map_sync_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapSyncRequest()
        request.ParseFromString(payload)
        response = pb.MapSyncResponse()
        op_download = int(getattr(pb, "MAP_SYNC_OP_DOWNLOAD_FROM_AURORA", 1))
        op_upload = int(getattr(pb, "MAP_SYNC_OP_UPLOAD_TO_AURORA", 2))
        req_op = int(request.operation)
        response.operation = req_op
        response.navigation_map_reloaded = False
        os.makedirs(self._stcm_local_dir, exist_ok=True)
        requested_map_id = str(getattr(request, "map_id", "")).strip()
        stcm_path = ""
        saved_name = ""
        saved_map_id = ""

        try:
            if req_op == op_download:
                # map_id-only mode: always create a fresh local file; request.map_id is optional hint.
                stcm_path = self._build_stcm_download_path("")
                self._ensure_sync_proxies()
                result = self._sync_get_proxy(mapfile=stcm_path)
                if not result.success:
                    raise RuntimeError(result.message or "sync_get_stcm failed")
                if (not os.path.exists(stcm_path)) or os.path.getsize(stcm_path) <= 0:
                    raise RuntimeError("sync_get_stcm finished but file is empty: {}".format(stcm_path))
                _saved_name, saved_map_id = self._register_saved_map(stcm_path, "")
                saved_name = _saved_name or ""
                if saved_map_id:
                    self._set_active_map_id(saved_map_id, reason="map_sync_download", migrate_bindings=True)
                response.message = "stcm_downloaded"
            elif req_op == op_upload:
                self._ensure_sync_proxies()
                if requested_map_id:
                    record = self._find_recorded_map_by_id(requested_map_id)
                    if record is None:
                        raise RuntimeError("map_id not found: {}".format(requested_map_id))
                    stcm_path = os.path.abspath(str(record.get("path", "")).strip())
                    if not stcm_path:
                        raise RuntimeError("map_id found but path is empty: {}".format(requested_map_id))
                    saved_name = str(record.get("name", "")).strip()
                    saved_map_id = requested_map_id
                else:
                    raise RuntimeError("map_id is required for upload")
                if not os.path.exists(stcm_path):
                    raise RuntimeError("stcm file not found: {}".format(stcm_path))
                result = self._sync_set_proxy(mapfile=stcm_path)
                if not result.success:
                    raise RuntimeError(result.message or "sync_set_stcm failed")
                if not saved_map_id:
                    _saved_name, saved_map_id = self._register_saved_map(stcm_path, "")
                    saved_name = saved_name or (_saved_name or "")
                if saved_map_id:
                    self._set_active_map_id(saved_map_id, reason="map_sync_upload", migrate_bindings=False)
                response.message = "stcm_uploaded"
            else:
                raise RuntimeError("unsupported map sync operation")

            self._attach_runtime_map_paths(response, False)
            self._save_local_state()
            response.result = pb.RESULT_SUCCESS
            if hasattr(response, "map_id"):
                response.map_id = str(saved_map_id or requested_map_id or "")
            if hasattr(response, "map_name"):
                response.map_name = str(saved_name or "")
            if not response.message:
                response.message = "ok"
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
            if hasattr(response, "map_id"):
                response.map_id = str(requested_map_id or "")

        return response.SerializeToString(), pb.MSG_ID_MAP_SYNC_RESPONSE, pb.COMP_SCHEDULER

    def _attach_runtime_map_paths(self, response, update_navigation_map):
        raw_map = self.aurora_bridge.get_map()
        if raw_map is None:
            return
        map_info = self.map_service.get_map_info()
        composed_map = self.map_service.compose_map()
        out_dir = self._live_map_dir
        yaml_name = self._live_map_yaml_name
        image_name = self._live_map_image_name
        if map_info is not None and composed_map is not None:
            yaml_path, image_path = self._export_runtime_map(
                raw_map,
                out_dir,
                yaml_name,
                image_name,
                grid_override=composed_map,
                map_info_override=map_info,
            )
        else:
            yaml_path, image_path = self._export_runtime_map(raw_map, out_dir, yaml_name, image_name)
        response.map_yaml_path = yaml_path
        response.map_image_path = image_path
        response.navigation_map_reloaded = False
        if not update_navigation_map:
            return
        nav_dir = os.path.dirname(self._nav_map_yaml_path)
        nav_yaml_name = os.path.basename(self._nav_map_yaml_path)
        nav_image_name = "map1.pgm"
        if map_info is not None and composed_map is not None:
            nav_yaml_path, nav_image_path = self._export_runtime_map(
                raw_map,
                nav_dir,
                nav_yaml_name,
                nav_image_name,
                grid_override=composed_map,
                map_info_override=map_info,
            )
        else:
            nav_yaml_path, nav_image_path = self._export_runtime_map(raw_map, nav_dir, nav_yaml_name, nav_image_name)
        reloaded, _ = self._reload_navigation_map(nav_yaml_path)
        response.map_yaml_path = nav_yaml_path
        response.map_image_path = nav_image_path
        response.navigation_map_reloaded = bool(reloaded)

    def handle_map_save_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapSaveRequest()
        request.ParseFromString(payload)
        response = pb.MapSaveResponse()
        response.navigation_map_reloaded = False
        os.makedirs(self._stcm_local_dir, exist_ok=True)

        requested_name = (request.map_name or "").strip()
        requested_map_id = str(getattr(request, "map_id", "") or "").strip()
        if requested_name:
            stcm_path = self._build_stcm_download_path(requested_name, forced_map_id=requested_map_id)
        else:
            stcm_path = self._build_stcm_download_path("", forced_map_id=requested_map_id)
        if hasattr(response, "stcm_path"):
            response.stcm_path = stcm_path

        try:
            self._ensure_sync_proxies()
            result = self._sync_get_proxy(mapfile=stcm_path)
            if not result.success:
                raise RuntimeError(result.message or "sync_get_stcm failed")
            if (not os.path.exists(stcm_path)) or os.path.getsize(stcm_path) <= 0:
                raise RuntimeError("save map finished but file is empty: {}".format(stcm_path))
            total_work_area_m2, estimated_time_s = self._compute_saved_map_metrics()
            region_metrics = self._compute_saved_region_metrics(estimated_time_s)
            thumb_format, thumb_b64, thumb_width, thumb_height = self._build_saved_map_thumbnail()
            _saved_name, saved_map_id = self._register_saved_map(
                stcm_path,
                requested_name,
                explicit_map_id=requested_map_id,
                total_work_area_m2=total_work_area_m2,
                estimated_time_s=estimated_time_s,
                region_metrics=region_metrics,
                thumb_format=thumb_format,
                thumb_b64=thumb_b64,
                thumb_width=thumb_width,
                thumb_height=thumb_height,
            )
            if saved_map_id:
                prev_map_id = self._current_map_id()
                # Carry current overlay regions into newly saved map state.
                self._save_map_overlay_state_for_map(prev_map_id)
                self._copy_map_overlay_state(prev_map_id, saved_map_id, overwrite=True)
                self._set_active_map_id(saved_map_id, reason="map_save", migrate_bindings=True)
                # After saving from LIVE_MAP, clear LIVE_MAP overlay regions.
                # This ensures next time LIVE_MAP is entered, it starts with empty regions.
                if prev_map_id == self._live_map_id:
                    self._remove_map_overlay_state_for_map(prev_map_id)
            localization_switched = False
            localization_err = ""
            try:
                self._switch_to_localization_mode_after_map_save()
                localization_switched = True
            except Exception as loc_exc:
                localization_err = str(loc_exc)
                rospy.logwarn("Map saved but failed to switch localization mode: %s", localization_err)
            self._attach_runtime_map_paths(response, False)
            self._save_local_state()
            response.result = pb.RESULT_SUCCESS
            response.message = "map_saved_and_localization_on" if localization_switched else "map_saved"
            if localization_err:
                response.message = "{} ({})".format(response.message, localization_err)
            if hasattr(response, "map_id"):
                response.map_id = str(saved_map_id or requested_map_id or "")
            if hasattr(response, "map_name"):
                response.map_name = str(_saved_name or requested_name or "")
            if hasattr(response, "total_work_area_m2"):
                response.total_work_area_m2 = float(max(0.0, total_work_area_m2))
            if hasattr(response, "estimated_time_s"):
                response.estimated_time_s = float(estimated_time_s)
            if hasattr(response, "created_at"):
                record = self._find_recorded_map_by_id(saved_map_id or requested_map_id or "")
                created_at = ""
                if isinstance(record, dict):
                    created_at = str(record.get("created_at", "") or "").strip()
                    if not created_at:
                        created_at = _format_ts_s(record.get("saved_at", 0))
                response.created_at = str(created_at or "")
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)

        return response.SerializeToString(), pb.MSG_ID_MAP_SAVE_RESPONSE, pb.COMP_SCHEDULER

    def handle_map_metrics_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapMetricsRequest()
        request.ParseFromString(payload)
        response = pb.MapMetricsResponse()
        requested_map_id = str(getattr(request, "map_id", "") or "").strip()
        response.map_id = requested_map_id
        try:
            if not requested_map_id:
                raise RuntimeError("map_id is empty")
            record = self._find_recorded_map_by_id(requested_map_id)
            if record is None:
                raise RuntimeError("map_id not found: {}".format(requested_map_id))
            map_name = str(record.get("name", "") or "").strip()

            response.result = pb.RESULT_SUCCESS
            response.message = "ok"
            response.map_id = requested_map_id
            response.map_name = map_name
            for item in list(record.get("region_metrics", []) or []):
                if not isinstance(item, dict):
                    continue
                region_item = response.region_metrics.add()
                region_item.region_id = str(item.get("region_id", "") or "")
                region_item.region_name = str(item.get("region_name", "") or "")
                region_item.repeat = int(max(1, int(item.get("repeat", 1) or 1)))
                region_item.area_m2 = float(max(0.0, float(item.get("area_m2", 0.0) or 0.0)))
                region_item.estimated_time_h = float(item.get("estimated_time_h", -1.0) or -1.0)
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
            response.map_name = ""

        return response.SerializeToString(), pb.MSG_ID_MAP_METRICS_RESPONSE, pb.COMP_SCHEDULER

    def handle_task_result_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.TaskResultRequest()
        request.ParseFromString(payload)
        response = pb.TaskResultResponse()
        requested_map_id = str(getattr(request, "map_id", "") or "").strip()
        requested_task_id = str(getattr(request, "task_id", "") or "").strip()
        try:
            record = None
            if requested_map_id and requested_task_id:
                key = "{}::{}".format(requested_map_id, requested_task_id)
                found = self._task_bindings.get(key)
                if isinstance(found, dict):
                    record = found
            elif requested_map_id:
                for _key, item in dict(self._task_bindings or {}).items():
                    if not isinstance(item, dict):
                        continue
                    if str(item.get("map_id", "")).strip() == requested_map_id:
                        record = item
                        break
            else:
                latest_ts = -1
                for _key, item in dict(self._task_bindings or {}).items():
                    if not isinstance(item, dict):
                        continue
                    task_result = item.get("task_result", {}) if isinstance(item.get("task_result", {}), dict) else {}
                    ts = int(task_result.get("finished_at", item.get("updated_at", 0)) or 0)
                    if ts >= latest_ts:
                        latest_ts = ts
                        record = item
            if not isinstance(record, dict):
                raise RuntimeError("task result not found")
            task_result = record.get("task_result", {}) if isinstance(record.get("task_result", {}), dict) else {}
            if not task_result:
                raise RuntimeError("task result is empty")

            response.result = pb.RESULT_SUCCESS
            response.message = "ok"
            response.map_id = str(task_result.get("map_id", record.get("map_id", "")) or "")
            response.task_id = str(task_result.get("task_id", record.get("task_id", "")) or "")
            final_state_text = str(task_result.get("final_state", "") or "").strip().upper()
            state_map = {
                "IDLE": pb.TASK_STATE_IDLE,
                "READY": pb.TASK_STATE_READY,
                "PLANNING": pb.TASK_STATE_PLANNING,
                "RUNNING": pb.TASK_STATE_RUNNING,
                "PAUSED": pb.TASK_STATE_PAUSED,
                "COMPLETED": pb.TASK_STATE_COMPLETED,
                "STOPPED": pb.TASK_STATE_STOPPED,
                "ERROR": pb.TASK_STATE_ERROR,
            }
            response.final_state = state_map.get(final_state_text, pb.TASK_STATE_UNKNOWN if hasattr(pb, "TASK_STATE_UNKNOWN") else pb.TASK_STATE_IDLE)
            response.all_completed = bool(task_result.get("all_completed", False))
            response.stop_reason = str(task_result.get("stop_reason", "") or "")
            response.path_version = int(task_result.get("path_version", 0) or 0)
            response.finished_at = int(task_result.get("finished_at", 0) or 0)
            response.selected_work_region_ids.extend(list(task_result.get("selected_work_region_ids", []) or []))
            response.image_format = str(task_result.get("image_format", "") or "")
            response.image_width = int(task_result.get("image_width", 0) or 0)
            response.image_height = int(task_result.get("image_height", 0) or 0)
            image_b64 = str(task_result.get("image_b64", "") or "")
            if image_b64:
                try:
                    response.image_data = base64.b64decode(image_b64.encode("ascii"), validate=False)
                except Exception:
                    response.image_data = b""
            for item in list(task_result.get("region_results", []) or []):
                if not isinstance(item, dict):
                    continue
                row = response.region_results.add()
                row.region_id = str(item.get("region_id", "") or "")
                row.region_name = str(item.get("region_name", "") or "")
                row.target_repeat = int(max(1, int(item.get("target_repeat", 1) or 1)))
                row.executed_repeat = int(max(0, int(item.get("executed_repeat", 0) or 0)))
                row.completed = bool(item.get("completed", False))
                row.unfinished_reason = str(item.get("unfinished_reason", "") or "")
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
            response.map_id = requested_map_id
            response.task_id = requested_task_id

        return response.SerializeToString(), pb.MSG_ID_TASK_RESULT_RESPONSE, pb.COMP_SCHEDULER

    def _switch_to_localization_mode_after_map_save(self):
        if self._set_map_localization_pub is None or SetMapLocalizationRequest is None:
            raise RuntimeError("set_map_localization publisher is unavailable")
        conn = int(self._set_map_localization_pub.get_num_connections())
        if conn <= 0:
            raise RuntimeError("set_map_localization has no subscribers; check slamware_ros_sdk node")
        msg = SetMapLocalizationRequest()
        msg.enabled = True
        for _ in range(12):
            self._set_map_localization_pub.publish(msg)
            rospy.sleep(0.15)

    def handle_map_mode_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapModeRequest()
        request.ParseFromString(payload)
        response = pb.MapModeResponse()
        response.mode = request.mode
        response.enabled = bool(request.enabled)
        response.map_kind = int(request.map_kind)

        try:
            if request.mode == pb.MAP_MODE_MAPPING:
                if bool(request.enabled):
                    if self._set_map_update_pub is None or SetMapUpdateRequest is None:
                        raise RuntimeError("set_map_update publisher is unavailable")
                    conn = int(self._set_map_update_pub.get_num_connections())
                    if conn <= 0:
                        raise RuntimeError("set_map_update has no subscribers; check slamware_ros_sdk node")
                    msg = SetMapUpdateRequest()
                    msg.enabled = True
                    # Default to EXPLORERMAP when request.map_kind is unset.
                    kind_value = int(request.map_kind) if request.map_kind != 0 else int(MapKind.EXPLORERMAP)
                    if MapKind is not None:
                        kind_value = max(int(MapKind.UNKNOWN), min(int(MapKind.LOCALSLAMMAP), kind_value))
                    msg.kind.kind = kind_value
                    for _ in range(12):
                        self._set_map_update_pub.publish(msg)
                        rospy.sleep(0.15)
                    self._set_active_map_id(self._live_map_id, reason="map_mode_mapping_on", migrate_bindings=False)
                    response.map_kind = kind_value
                    response.result = pb.RESULT_SUCCESS
                    response.message = "mapping_mode_command_published enabled=1 subscribers={}".format(conn)
                else:
                    # aurora_ros set_map_update callback ignores msg.enabled and always enters mapping mode.
                    # To support "mapping off" without modifying aurora_ros, switch to localization mode.
                    if self._set_map_localization_pub is None or SetMapLocalizationRequest is None:
                        raise RuntimeError(
                            "mapping_off fallback requires set_map_localization publisher, but it is unavailable"
                        )
                    conn = int(self._set_map_localization_pub.get_num_connections())
                    if conn <= 0:
                        raise RuntimeError(
                            "mapping_off fallback failed: set_map_localization has no subscribers; check slamware_ros_sdk node"
                        )
                    msg = SetMapLocalizationRequest()
                    msg.enabled = True
                    for _ in range(12):
                        self._set_map_localization_pub.publish(msg)
                        rospy.sleep(0.15)
                    response.result = pb.RESULT_SUCCESS
                    response.message = (
                        "mapping_off_fallback_to_localization enabled=1 subscribers={}".format(conn)
                    )
            elif request.mode == pb.MAP_MODE_LOCALIZATION:
                if self._set_map_localization_pub is None or SetMapLocalizationRequest is None:
                    raise RuntimeError("set_map_localization publisher is unavailable")
                conn = int(self._set_map_localization_pub.get_num_connections())
                if conn <= 0:
                    raise RuntimeError("set_map_localization has no subscribers; check slamware_ros_sdk node")
                msg = SetMapLocalizationRequest()
                msg.enabled = bool(request.enabled)
                for _ in range(12):
                    self._set_map_localization_pub.publish(msg)
                    rospy.sleep(0.15)
                response.result = pb.RESULT_SUCCESS
                response.message = "localization_mode_command_published enabled={} subscribers={}".format(
                    int(bool(request.enabled)), conn
                )
            else:
                response.result = pb.RESULT_INVALID_PARAM
                response.message = "unsupported map mode"
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)

        return response.SerializeToString(), pb.MSG_ID_MAP_MODE_RESPONSE, pb.COMP_SCHEDULER

    def _is_sub_path(self, child_path, parent_path):
        try:
            child = os.path.realpath(child_path)
            parent = os.path.realpath(parent_path)
            return os.path.commonpath([child, parent]) == parent
        except Exception:
            return False

    def handle_map_catalog_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapCatalogRequest()
        request.ParseFromString(payload)
        response = pb.MapCatalogResponse()
        target_dir = os.path.abspath(self._stcm_local_dir)
        try:
            # Query should return recorded map metadata, not raw folder filenames.
            entries = self._iter_recorded_maps(target_dir=target_dir)
            response.total_count = int(len(entries))
            bounded_count, thumbs_attached, thumbs_dropped = fill_map_catalog_response(
                response=response,
                entries=entries,
                find_record_by_id=self._find_recorded_map_by_id,
                include_thumbnails=self._map_catalog_include_thumbnails,
                max_items=self._map_catalog_max_items,
                max_thumb_b64_total=self._map_catalog_max_thumbnail_b64_total,
            )
            response.result = pb.RESULT_SUCCESS
            response.message = "ok"
            if bounded_count < len(entries):
                rospy.logwarn(
                    "MapCatalog trimmed: total=%d returned=%d (max_items=%d)",
                    len(entries),
                    bounded_count,
                    self._map_catalog_max_items,
                )
            if thumbs_dropped > 0:
                rospy.loginfo(
                    "MapCatalog thumbnail budget applied: attached=%d dropped=%d include=%s budget_b64=%d",
                    thumbs_attached,
                    thumbs_dropped,
                    str(self._map_catalog_include_thumbnails).lower(),
                    self._map_catalog_max_thumbnail_b64_total,
                )
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
            response.total_count = 0
        return response.SerializeToString(), pb.MSG_ID_MAP_CATALOG_RESPONSE, pb.COMP_SCHEDULER

    def handle_map_delete_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapDeleteRequest()
        request.ParseFromString(payload)
        response = pb.MapDeleteResponse()
        requested_map_id = str(getattr(request, "map_id", "")).strip()
        requested = requested_map_id
        if hasattr(response, "map_id"):
            response.map_id = requested_map_id
        response.deleted = False
        try:
            if not requested:
                raise RuntimeError("map_id is empty")
            record = self._find_recorded_map_by_id(requested_map_id)
            if record is None:
                raise RuntimeError("map_id not found: {}".format(requested_map_id))
            target_path = os.path.abspath(str(record.get("path", "")).strip())
            if not target_path:
                raise RuntimeError("map_id found but path is empty: {}".format(requested_map_id))
            if not os.path.exists(target_path):
                raise RuntimeError("map file not found: {}".format(target_path))
            if not os.path.isfile(target_path):
                raise RuntimeError("target is not a file: {}".format(target_path))
            record_name, record_id = self._split_map_name_and_id_from_path(target_path)
            for rec in (self._map_registry or {}).values():
                if isinstance(rec, dict) and os.path.abspath(str(rec.get("path", "")).strip()) == target_path:
                    if str(rec.get("map_id", "")).strip():
                        record_id = str(rec.get("map_id", "")).strip()
                    if str(rec.get("name", "")).strip():
                        record_name = str(rec.get("name", "")).strip()
                    break
            os.remove(target_path)
            self._unregister_saved_map(target_path)
            self._remove_map_overlay_state_for_map(record_id or requested_map_id)
            # Also remove task bindings associated with this map_id.
            removed_task_bindings = 0
            target_map_id = str(record_id or requested_map_id or "").strip()
            if target_map_id:
                prefix = "{}::".format(target_map_id)
                for key in list(self._task_bindings.keys()):
                    if str(key).startswith(prefix):
                        self._task_bindings.pop(key, None)
                        removed_task_bindings += 1
                if removed_task_bindings > 0:
                    rospy.loginfo(
                        "MapDelete removed task bindings: map_id=%s count=%d",
                        target_map_id,
                        removed_task_bindings,
                    )
            self._save_local_state()
            if hasattr(response, "map_id"):
                response.map_id = record_id
            if hasattr(response, "map_name"):
                response.map_name = record_name
            response.deleted = True
            response.result = pb.RESULT_SUCCESS
            response.message = "deleted"
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
        return response.SerializeToString(), pb.MSG_ID_MAP_DELETE_RESPONSE, pb.COMP_SCHEDULER

    def handle_live_map_cache_clear_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.LiveMapCacheClearRequest()
        request.ParseFromString(payload)
        response = pb.LiveMapCacheClearResponse()
        response.result = pb.RESULT_SUCCESS
        response.message = "cleared"
        try:
            # Request has no parameters by design.
            # Cleanup scope is decided by scheduler local policy.
            if self._live_map_cache_clear_mode == "memory_only":
                self.map_service.reset_overlay_regions()
                self._sync_task_regions_from_overlay()
                self._save_local_state()
            else:
                self._remove_map_overlay_state_for_map(self._live_map_id)
                # Also clear in-memory overlay immediately.
                self.map_service.reset_overlay_regions()
                self._sync_task_regions_from_overlay()
                self._save_local_state()
                self._clear_live_map_files()

            self._set_active_map_id(self._live_map_id, reason="live_map_cache_clear", migrate_bindings=False)
            response.message = "cleared(mode={})".format(self._live_map_cache_clear_mode)
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
        return response.SerializeToString(), pb.MSG_ID_LIVE_MAP_CACHE_CLEAR_RESPONSE, pb.COMP_SCHEDULER

    def handle_map_preview_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapPreviewRequest()
        request.ParseFromString(payload)
        response = pb.MapPreviewResponse()
        try:
            requested_map_id = str(getattr(request, "map_id", "") or "").strip()
            has_saved_maps = any(isinstance(item, dict) for item in (self._map_registry or {}).values())
            # If there is no saved map at all, always fallback to LIVE_MAP preview.
            # This avoids UI preview failure when APP still carries an old/non-live map_id.
            if has_saved_maps:
                map_id_ok, _ = self._validate_requested_map_id(requested_map_id, "MapPreviewRequest")
                if not map_id_ok:
                    raise RuntimeError("map_id mismatch with current map")
            else:
                if requested_map_id and requested_map_id not in (self._live_map_id, DEFAULT_LIVE_MAP_ID):
                    rospy.loginfo(
                        "MapPreviewRequest fallback to LIVE_MAP: no saved map available, requested_map_id=%s",
                        requested_map_id,
                    )
            requested_edge = request.max_edge if request.max_edge > 0 else PREVIEW_MAX_EDGE_CAP
            max_edge = self._sanitize_preview_edge(requested_edge, cap_edge=self._preview_max_edge_cap)
            snapshot = self.map_service.create_preview(
                self.aurora_bridge.get_pose(),
                max_edge,
                request.image_format or "jpg",
                request.include_overlay,
                **self._map_preview_alignment_kwargs()
            )
            response.result = pb.RESULT_SUCCESS
            response.message = "ok"
            response.map_version = snapshot.map_version
            response.width = snapshot.width
            response.height = snapshot.height
            response.resolution = snapshot.resolution
            response.origin.x = snapshot.origin_x
            response.origin.y = snapshot.origin_y
            response.frame_id = snapshot.frame_id
            response.image_data = snapshot.preview_data
            response.overlay_json = snapshot.overlay_json
            preview_w, preview_h, _ = self._preview_meta(snapshot.width, snapshot.height, max_edge)
            response.preview_scale_x = float(preview_w) / float(max(1, snapshot.width))
            response.preview_scale_y = float(preview_h) / float(max(1, snapshot.height))
        except Exception as exc:
            response.result = pb.RESULT_FAILED
            response.message = str(exc)
        return response.SerializeToString(), pb.MSG_ID_MAP_PREVIEW_RESPONSE, pb.COMP_SCHEDULER

    def handle_map_edit_command(self, payload):
        pb = self.sl_link_server.pb
        request = pb.MapEditCommand()
        request.ParseFromString(payload)
        map_id_ok, _ = self._validate_requested_map_id(getattr(request, "map_id", ""), "MapEditCommand")
        if not map_id_ok:
            response = pb.MapEditResponse()
            response.result = pb.RESULT_INVALID_PARAM
            response.message = "map_id mismatch with current map"
            map_info = self.map_service.get_map_info()
            response.map_version = int(map_info.get("map_version", 0)) if map_info else 0
            return response.SerializeToString(), pb.MSG_ID_MAP_EDIT_RESPONSE, pb.COMP_SCHEDULER
        region_points = [{"x": p.x, "y": p.y} for p in request.region.points]
        polygon_points = [{"x": p.x, "y": p.y} for p in request.polygon]
        operation_map = {
            pb.MAP_EDIT_OP_UPSERT_WORK_REGION: "UPSERT_WORK_REGION",
            pb.MAP_EDIT_OP_UPSERT_OBSTACLE_REGION: "UPSERT_OBSTACLE_REGION",
            pb.MAP_EDIT_OP_UPSERT_ERASE_REGION: "UPSERT_ERASE_REGION",
            pb.MAP_EDIT_OP_UPSERT_CROP_REGION: "UPSERT_CROP_REGION",
            pb.MAP_EDIT_OP_DELETE_REGION: "DELETE_REGION",
            pb.MAP_EDIT_OP_PAINT_FREE: "PAINT_FREE",
            pb.MAP_EDIT_OP_PAINT_OCCUPIED: "PAINT_OCCUPIED",
            pb.MAP_EDIT_OP_PAINT_UNKNOWN: "PAINT_UNKNOWN",
            pb.MAP_EDIT_OP_CLEAR_OVERLAY_PATCH: "CLEAR_OVERLAY_PATCH",
        }
        operation_name = operation_map.get(request.operation, "UNKNOWN")
        request_start_pose = {}
        request_end_pose = {}
        if request.HasField("start_pose"):
            request_start_pose = {
                "x": float(request.start_pose.x),
                "y": float(request.start_pose.y),
                "heading_deg": float(request.start_pose.heading_deg),
            }
        if request.HasField("end_pose"):
            request_end_pose = {
                "x": float(request.end_pose.x),
                "y": float(request.end_pose.y),
                "heading_deg": float(request.end_pose.heading_deg),
            }
        region_id_text = (request.region.region_id or "").strip()
        region_name_text = (request.region.name or request.region_name or "").strip().lower()
        target_region_id_text = (request.target_region_id or "").strip()
        region_type_value = int(request.region.region_type)
        target_region_type_value = int(request.target_region_type)
        crop_region_type = int(getattr(pb, "REGION_TYPE_CROP", 4))
        # Robust crop detection across proto/version mismatches:
        # if id/name clearly indicates crop, force type=4.
        if region_id_text == "crop_region_1" or region_name_text.startswith("crop"):
            region_type_value = crop_region_type
        if target_region_id_text == "crop_region_1":
            target_region_type_value = crop_region_type
        edit_alignment_yaw = self._lookup_live_map_alignment_yaw() if self._live_map_align_to_initial_yaw else None
        if edit_alignment_yaw is not None:
            region_points = self._points_from_aligned_to_source_map(region_points, edit_alignment_yaw)
            polygon_points = self._points_from_aligned_to_source_map(polygon_points, edit_alignment_yaw)
            request_start_pose = self._pose_from_aligned_to_source_map(request_start_pose, edit_alignment_yaw)
            request_end_pose = self._pose_from_aligned_to_source_map(request_end_pose, edit_alignment_yaw)
            rospy.loginfo(
                "MapEdit coordinates converted: input_frame=%s output_frame=%s alignment_yaw=%.6f",
                self._live_map_aligned_frame,
                self._live_map_source_frame,
                float(edit_alignment_yaw),
            )

        def _format_points(points, max_points=64):
            if not points:
                return "[]"
            shown = points[:max_points]
            body = ", ".join("({:.3f},{:.3f})".format(float(item["x"]), float(item["y"])) for item in shown)
            if len(points) > max_points:
                body += ", ... ({} more)".format(len(points) - max_points)
            return "[" + body + "]"

        rospy.loginfo(
            "MapEdit request: op=%s edit_id=%s map_id=%s region_id=%s region_name=%s region_type=%d region_points=%d polygon_points=%d target_region_id=%s target_region_type=%d brush_radius=%.3f",
            operation_name,
            (request.edit_id or "").strip(),
            str(getattr(request, "map_id", "")).strip() or "<empty>",
            region_id_text or "<empty>",
            (request.region.name or request.region_name or "").strip() or "<empty>",
            region_type_value,
            len(region_points),
            len(polygon_points),
            target_region_id_text or "<empty>",
            target_region_type_value,
            float(request.brush_radius),
        )
        if operation_name in ("UPSERT_WORK_REGION", "UPSERT_OBSTACLE_REGION", "UPSERT_ERASE_REGION", "UPSERT_CROP_REGION"):
            rospy.loginfo(
                "MapEdit region points: op=%s region_id=%s points=%s",
                operation_name,
                region_id_text or "<empty>",
                _format_points(region_points),
            )
        if request.operation == pb.MAP_EDIT_OP_UPSERT_WORK_REGION:
            if request_start_pose:
                rospy.loginfo(
                    "MapEdit work_region start_pose: x=%.3f y=%.3f heading=%.1f",
                    float(request_start_pose.get("x", 0.0)),
                    float(request_start_pose.get("y", 0.0)),
                    float(request_start_pose.get("heading_deg", 0.0)),
                )
            else:
                rospy.loginfo("MapEdit work_region start_pose: <empty>")
            if request_end_pose:
                rospy.loginfo(
                    "MapEdit work_region end_pose: x=%.3f y=%.3f heading=%.1f",
                    float(request_end_pose.get("x", 0.0)),
                    float(request_end_pose.get("y", 0.0)),
                    float(request_end_pose.get("heading_deg", 0.0)),
                )
            else:
                rospy.loginfo("MapEdit work_region end_pose: <empty>")
        if request.operation == pb.MAP_EDIT_OP_UPSERT_WORK_REGION and region_points:
            if (not request_start_pose) or (not request_end_pose):
                xs = [float(item.get("x", 0.0)) for item in region_points]
                ys = [float(item.get("y", 0.0)) for item in region_points]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                if not request_start_pose:
                    request_start_pose = {"x": min_x, "y": max_y, "heading_deg": 0.0}
                if not request_end_pose:
                    request_end_pose = {"x": max_x, "y": min_y, "heading_deg": 0.0}
                rospy.loginfo(
                    "MapEdit UPSERT_WORK auto-fill start/end: start=(%.3f,%.3f) end=(%.3f,%.3f)",
                    float(request_start_pose.get("x", 0.0)),
                    float(request_start_pose.get("y", 0.0)),
                    float(request_end_pose.get("x", 0.0)),
                    float(request_end_pose.get("y", 0.0)),
                )
        # Region-level planning direction:
        # do not auto-infer; consume direction from request if protocol provides it.
        # If absent, keep existing region direction (MapService upsert fallback), or default x for new region.
        region_global_direction = ""
        try:
            candidate = str(getattr(request.region, "global_direction", "") or "").strip().lower()
            if candidate in ("x", "y"):
                region_global_direction = candidate
        except Exception:
            region_global_direction = ""

        region_payload = {
            "name": request.region.name or request.region_name,
            "points": region_points,
            "region_id": request.region.region_id,
            "priority": int(request.region.priority),
            "enabled": bool(request.region.enabled),
            "color_argb": int(request.region.color_argb),
            "closed": bool(request.region.closed),
            "region_type": region_type_value,
            "start_pose": request_start_pose,
            "end_pose": request_end_pose,
        }
        if region_global_direction:
            region_payload["global_direction"] = region_global_direction

        success, message, map_version = self.map_service.apply_edit(
            {
                "operation": operation_name,
                "region_name": request.region_name,
                "region": region_payload,
                "polygon": polygon_points,
                "brush_radius": request.brush_radius,
                "paint_value": request.paint_value,
                "target_region_id": request.target_region_id,
                "target_region_type": target_region_type_value,
            }
        )
        if success:
            if request.operation == pb.MAP_EDIT_OP_UPSERT_WORK_REGION:
                selected_id = (request.region.region_id or "").strip()
                if selected_id:
                    self.task_config.active_work_region_id = selected_id
            elif request.operation == pb.MAP_EDIT_OP_DELETE_REGION:
                target_type = int(request.target_region_type)
                target_id = (request.target_region_id or "").strip()
                if target_id and target_type in (0, int(pb.REGION_TYPE_WORK)):
                    if self.task_config.active_work_region_id == target_id:
                        self.task_config.active_work_region_id = ""
            # Keep task_config cache consistent with overlay source-of-truth immediately.
            self._sync_task_regions_from_overlay()
        if success and self.state in (SchedulerState.READY, SchedulerState.PLANNING):
            self._plan_current_task()
        elif success and self.state == SchedulerState.RUNNING:
            self.replan_requested = True
        if success:
            self._save_local_state()
            rospy.loginfo(
                "MapEdit applied: op=%s success=true map_version=%d replan_requested=%s active_work_region_id=%s",
                operation_name,
                int(map_version),
                str(self.replan_requested).lower(),
                self.task_config.active_work_region_id or "<empty>",
            )
        else:
            rospy.logwarn(
                "MapEdit applied: op=%s success=false map_version=%d reason=%s",
                operation_name,
                int(map_version),
                message,
            )

        response = pb.MapEditResponse()
        response.result = pb.RESULT_SUCCESS if success else pb.RESULT_FAILED
        response.message = message
        response.map_version = map_version

        status = pb.MapEditStatusReport()
        status.map_version = map_version
        status.applied_to_planner = success
        status.message = "planner_refresh_requested" if self.replan_requested else message

        return [
            (response.SerializeToString(), pb.MSG_ID_MAP_EDIT_RESPONSE, pb.COMP_SCHEDULER),
            (status.SerializeToString(), pb.MSG_ID_MAP_EDIT_STATUS_REPORT, pb.COMP_SCHEDULER),
        ]

    def handle_video_stream_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.VideoStreamInfoRequest()
        request.ParseFromString(payload)
        state = self.media_streamer.get_state()
        local_state = self.local_stream_server.get_state()
        response = pb.VideoStreamInfoResponse()
        response.result = pb.RESULT_SUCCESS
        if not self.local_stream_server.ffmpeg_available():
            response.message = "ffmpeg_not_installed"
        elif not self.local_stream_server.mediamtx_available():
            response.message = "mediamtx_not_installed"
        else:
            response.message = "ok"
        if local_state.online:
            response.stream_url = local_state.stream_url
            response.codec = local_state.codec
            response.width = local_state.width
            response.height = local_state.height
            response.online = local_state.online
            response.utc_time = local_state.last_update_utc
        else:
            response.stream_url = state.stream_url
            response.codec = state.codec
            response.width = state.width
            response.height = state.height
            response.online = state.online
            response.utc_time = state.last_update_utc
        return response.SerializeToString(), pb.MSG_ID_VIDEO_STREAM_INFO_RESPONSE, pb.COMP_SCHEDULER

    def handle_path_plan_request(self, payload):
        pb = self.sl_link_server.pb
        request = pb.PathPlanRequest()
        request.ParseFromString(payload)

        map_id_ok, current_map_id = self._validate_requested_map_id(
            getattr(request, "map_id", ""),
            "PathPlanRequest",
            keep_current_on_empty=True,
        )
        if not map_id_ok:
            response = pb.PathPlanResponse()
            response.request_id = request.request_id
            response.task_id = self.task_config.task_id
            response.result = pb.RESULT_FAILED
            response.message = "map_id mismatch with current map"
            response.planned = False
            return response.SerializeToString(), pb.MSG_ID_PATH_PLAN_RESPONSE, pb.COMP_SCHEDULER

        if request.task_id:
            self.task_config.task_id = request.task_id
        self.task_config.map_id = current_map_id

        # PathPlanRequest planning scope:
        # True  -> plan all configured/selected regions in order
        # False -> plan by current selected/active policy
        self._sync_task_regions_from_overlay()
        self._sync_task_map_binding(update_binding=False)
        total_regions = len(self.task_config.work_regions or [])
        selected_ids = self._effective_selected_work_region_ids(
            sorted(
                list(self.task_config.work_regions or []),
                key=lambda region: int(region.get("order_index", 0)),
            ),
        )
        use_all = bool(self._path_plan_request_use_all_regions)
        request_start_pose = {}
        request_end_pose = {}
        request_global_direction = str(getattr(request, "global_direction", "") or "").strip().lower()
        if request_global_direction not in ("x", "y"):
            request_global_direction = "x"
        self.task_config.global_direction = request_global_direction
        if request.HasField("start_pose"):
            request_start_pose = {
                "x": float(request.start_pose.x),
                "y": float(request.start_pose.y),
                "heading_deg": float(request.start_pose.heading_deg),
            }
        if request.HasField("end_pose"):
            request_end_pose = {
                "x": float(request.end_pose.x),
                "y": float(request.end_pose.y),
                "heading_deg": float(request.end_pose.heading_deg),
            }
        plan_alignment_yaw = self._lookup_live_map_alignment_yaw() if self._live_map_align_to_initial_yaw else None
        if plan_alignment_yaw is not None:
            request_start_pose = self._pose_from_aligned_to_source_map(request_start_pose, plan_alignment_yaw)
            request_end_pose = self._pose_from_aligned_to_source_map(request_end_pose, plan_alignment_yaw)
            rospy.loginfo(
                "PathPlanRequest poses converted: input_frame=%s output_frame=%s alignment_yaw=%.6f",
                self._live_map_aligned_frame,
                self._live_map_source_frame,
                float(plan_alignment_yaw),
            )
        rospy.loginfo(
            "PathPlanRequest: request_id=%s active_work_region_id=%s force_replan=%s use_all_regions=%s work_region_count=%d has_start=%s has_end=%s global_direction=%s",
            request.request_id or "<empty>",
            self.task_config.active_work_region_id or "<empty>",
            str(bool(request.force_replan)).lower(),
            str(bool(use_all)).lower(),
            int(total_regions),
            str(bool(request_start_pose)).lower(),
            str(bool(request_end_pose)).lower(),
            request_global_direction,
        )
        rospy.loginfo(
            "PathPlanRequest selection: requested_map_id=%s map_id=%s task_id=%s selected_regions=%s region_repeat_config=%s",
            str(getattr(request, "map_id", "")).strip() or "<empty>",
            self.task_config.map_id or "<empty>",
            self.task_config.task_id or "<empty>",
            ",".join(selected_ids) if selected_ids else "<all_valid_regions>",
            json.dumps(self.task_config.region_repeat_config or {}, ensure_ascii=False, sort_keys=True),
        )
        if request_start_pose:
            rospy.loginfo(
                "PathPlanRequest start_pose: x=%.3f y=%.3f heading=%.1f",
                float(request_start_pose.get("x", 0.0)),
                float(request_start_pose.get("y", 0.0)),
                float(request_start_pose.get("heading_deg", 0.0)),
            )
        if request_end_pose:
            rospy.loginfo(
                "PathPlanRequest end_pose: x=%.3f y=%.3f heading=%.1f",
                float(request_end_pose.get("x", 0.0)),
                float(request_end_pose.get("y", 0.0)),
                float(request_end_pose.get("heading_deg", 0.0)),
            )
        planned = self._plan_current_task(
            force_use_all_regions=use_all,
            request_start_pose=request_start_pose,
            request_end_pose=request_end_pose,
            request_global_direction=request_global_direction,
        )

        response = pb.PathPlanResponse()
        response.request_id = request.request_id
        response.task_id = self.task_config.task_id
        map_info = self.map_service.get_map_info()
        response.map_version = map_info["map_version"] if map_info else 0
        if map_info:
            self._apply_response_map_info(response, map_info)
        else:
            response.width = 0
            response.height = 0
            response.resolution = 0.0
            response.origin.x = 0.0
            response.origin.y = 0.0
            response.origin.heading_deg = 0.0
            response.frame_id = ""
        response.preview_scale_x = 0.0
        response.preview_scale_y = 0.0
        total_area = self._total_work_area_m2()
        response.total_work_area_m2 = float(total_area)
        response.estimated_time_s = -1.0
        response.planned = planned

        if planned and self.current_path is not None:
            response.result = pb.RESULT_SUCCESS
            response.message = "planning_ok"
            response.path_version = self.current_path.path_version
            response.path_point_count = len(self.current_path.points)
            response.path_length_m = float(self.current_path.length_m)
            response.estimated_time_s = float(self._estimate_plan_time_s(self.current_path.length_m))
            try:
                preview_payload = self._build_path_preview_payload(map_info)
                if preview_payload is not None:
                    response.preview_image = preview_payload[0]
                    response.preview_format = preview_payload[1]
                    if len(preview_payload) > 2:
                        self._apply_response_map_info(response, preview_payload[2])
                    if response.width > 0 and response.height > 0 and response.preview_image:
                        try:
                            decoded = cv2.imdecode(np.frombuffer(response.preview_image, dtype=np.uint8), cv2.IMREAD_COLOR)
                            if decoded is not None:
                                ph, pw = decoded.shape[:2]
                                response.preview_scale_x = float(pw) / float(max(1, response.width))
                                response.preview_scale_y = float(ph) / float(max(1, response.height))
                        except Exception:
                            pass
                    # Ensure each successful PathPlanRequest leaves a local preview file.
                    self._save_path_preview_bytes(preview_payload[0], preview_payload[1], map_info)
            except Exception as exc:
                rospy.logwarn("Failed to build/save path preview in PathPlanResponse: %s", exc)
        else:
            response.result = pb.RESULT_FAILED
            response.message = self.last_error or "planning_failed"
            response.path_version = 0
            response.path_point_count = 0
            response.path_length_m = 0.0
            response.estimated_time_s = -1.0
            response.preview_image = b""
            response.preview_format = ""
            # Even if planning fails, return current map preview for UI continuity.
            try:
                failed_preview = self._build_failed_plan_preview_payload(response.message)
                if failed_preview is not None:
                    response.preview_image = failed_preview[0]
                    response.preview_format = failed_preview[1]
                    if len(failed_preview) > 2:
                        self._apply_response_map_info(response, failed_preview[2])
                    if response.width > 0 and response.height > 0 and response.preview_image:
                        try:
                            decoded = cv2.imdecode(np.frombuffer(response.preview_image, dtype=np.uint8), cv2.IMREAD_COLOR)
                            if decoded is not None:
                                ph, pw = decoded.shape[:2]
                                response.preview_scale_x = float(pw) / float(max(1, response.width))
                                response.preview_scale_y = float(ph) / float(max(1, response.height))
                        except Exception:
                            pass
            except Exception as exc:
                rospy.logwarn("Failed to build fallback preview for failed PathPlanResponse: %s", exc)

        response_payload = response.SerializeToString()
        # SL-Link frame payload_len is uint16, keep a safety margin for robustness.
        max_payload_safe = 65000
        if len(response_payload) > max_payload_safe:
            rospy.logwarn(
                "PathPlanResponse payload too large (%d bytes), strip preview image for transport safety",
                len(response_payload),
            )
            response.preview_image = b""
            response.preview_format = ""
            response.preview_scale_x = 0.0
            response.preview_scale_y = 0.0
            if response.message:
                response.message = "{};preview_omitted_oversize".format(response.message)
            else:
                response.message = "preview_omitted_oversize"
            response_payload = response.SerializeToString()

        outputs = [
            (response_payload, pb.MSG_ID_PATH_PLAN_RESPONSE, pb.COMP_SCHEDULER),
        ]

        if planned and request.return_path_chunks and self.current_path is not None:
            path_request = pb.TaskPathRequest()
            path_request.task_id = self.task_config.task_id
            path_request.max_chunk_size = request.max_chunk_size
            chunks = self.build_task_path_chunks(path_request.SerializeToString())
            outputs.extend(chunks)
            response.path_chunked = True
            response_payload = response.SerializeToString()
            if len(response_payload) > max_payload_safe:
                rospy.logwarn(
                    "PathPlanResponse payload too large after chunk-flag update (%d bytes), strip preview image",
                    len(response_payload),
                )
                response.preview_image = b""
                response.preview_format = ""
                response.preview_scale_x = 0.0
                response.preview_scale_y = 0.0
                if response.message:
                    response.message = "{};preview_omitted_oversize".format(response.message)
                else:
                    response.message = "preview_omitted_oversize"
                response_payload = response.SerializeToString()
            outputs[0] = (response_payload, pb.MSG_ID_PATH_PLAN_RESPONSE, pb.COMP_SCHEDULER)

        return outputs


def main():
    rospy.init_node("grinder_scheduler")
    node = SchedulerNode()
    rospy.on_shutdown(node.shutdown)
    rospy.spin()
