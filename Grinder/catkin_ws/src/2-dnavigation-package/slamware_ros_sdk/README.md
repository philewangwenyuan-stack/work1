# slamware_ros_sdk

本包是项目内使用的 Slamtec Aurora ROS1 driver。它基于官方 ROS server 扩展了位姿增强、协方差质量评估和更明确的建图/定位模式控制。

## 位姿增强

启动后默认调用 Aurora Remote SDK：

```text
startPoseAugmentation(IMU_VISION_MIXED, 50Hz)
```

默认参数：

- `pose_augmentation_enabled: true`
- `pose_augmentation_frequency_hz: 50`
- `pose_augmentation_mode: imu_vision_mixed`
- `pose_augmentation_smoothing_enabled: false`
- `pose_augmentation_smoothing_factor: 0.3`
- `pose_augmentation_timeout_sec: 0.25`

本包不新增 `/augmented_pose` 话题。增强位姿只作为 server 内部 pose source，优先进入现有 `/robot_pose`、`/odom` 和当前 TF 发布链路。

如果 IMU 不可用、固件不支持、启动失败或增强位姿超时，server 自动回退到 SDK 原始 pose。`/pose_quality.pose_source` 会显示 `raw_fallback`。

## 位姿质量

新增话题：

```text
/slamware_ros_sdk_server_node/pose_quality
```

类型：`slamware_ros_sdk/PoseQuality`

质量判定顺序：

1. `system_status` 和 `relocalization_status` 优先。
2. tracking lost、初始化失败、重定位运行/失败直接进入 `FAULT`。
3. 再看协方差 `xy95_m` 和 yaw sigma。
4. 协方差超过 `pose_quality_covariance_timeout_sec` 未刷新进入 `FAULT`。

默认阈值：

- WARN：`xy95 >= 0.10 m` 或 `yaw >= 3 deg`
- FAULT：`xy95 >= 0.30 m` 或 `yaw >= 5 deg`
- 协方差超时：`1.0 s`

协方差来自 Aurora SDK 的 `onPoseCovariance` 回调，并转换为 readable 指标。

## 模式控制

保留官方 topic：

- `~/set_map_update`
- `~/set_map_localization`

修正后的行为：

- `set_map_update.enabled=true`：请求建图模式。
- `set_map_update.enabled=false`：请求纯定位模式。
- `set_map_localization.enabled=true`：请求纯定位模式。
- `set_map_localization.enabled=false`：请求建图模式。

这些接口仍然是 topic，没有 ack。上层只应把它们当作请求和重试。

## 重定位

保留 stock server 能力：

- `~/relocalization`
- `~/relocalization/cancel`
- `/slamware_ros_sdk_server_node/relocalization_status`

本项目没有新增第二套重定位服务。

## 常用调试

```bash
rostopic hz /slamware_ros_sdk_server_node/robot_pose
rostopic hz /slamware_ros_sdk_server_node/odom
rostopic echo /slamware_ros_sdk_server_node/pose_quality
rostopic echo /slamware_ros_sdk_server_node/system_status
rostopic echo /slamware_ros_sdk_server_node/relocalization_status
```

## map_aligned exact-front alignment

`map_aligned` is the project-facing map frame. The raw Aurora map remains in
`map`; the aligned map is rotated into `map_aligned` so the robot heading at the
first valid pose points to the configured screen/front direction.

Defaults:

- `align_map_to_initial_yaw: true`
- `map_alignment_mode: exact_front`
- `aligned_front_yaw_deg: 90.0`

The alignment formula is:

```text
alignment_yaw = radians(aligned_front_yaw_deg) - initial_yaw
```

The node keeps the existing compatibility TF chain and `/odom` source. `/odom`
is still provided by Aurora, not by chassis wheel feedback.

The service `~/set_map_alignment` (`slamware_ros_sdk/SetMapAlignment`) lets the
scheduler restore a saved `alignment_yaw_rad` from its map registry, so a saved
map keeps the same `map_aligned` direction after reboot.
