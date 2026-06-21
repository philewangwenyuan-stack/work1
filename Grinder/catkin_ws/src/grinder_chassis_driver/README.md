# grinder_chassis_driver

`grinder_chassis_driver` 是研磨机器人底盘驱动包，使用 ROS1 Python 节点通过 RS485/Modbus RTU 控制底盘、磨盘、升降和照明，并把 `/cmd_vel` 转换为左右轮速度。

## 核心职责

- 底盘输出：左右轮速度、磨盘转速、磨盘启停、工作模式、升降和照明。
- 状态回读：周期读取寄存器并发布 `/chassis/status`、`/chassis/wheel_speed_state` 和 `/diagnostics`。
- `/cmd_vel` 转换：根据轮距、轮半径、减速比和方向修正参数生成左右轮转速。
- 手动接管：支持 `/chassis/manual_override`，接管时忽略 `/cmd_vel`；默认不取消 move_base 目标，退出手动后继续接收 `/cmd_vel`。
- 定位看门狗：默认只根据 `/pose_quality` 锁定底盘，system/relocalization 状态保留为可观测字段。

## 定位看门狗

订阅：

- `/slamware_ros_sdk_server_node/system_status`
- `/slamware_ros_sdk_server_node/relocalization_status`
- `/slamware_ros_sdk_server_node/pose_quality`
- `/slamware_ros_sdk_server_node/scan`

发布：

- `/chassis/localization_watchdog_status`

触发 WARN/FAULT/UNKNOWN 或 pose_quality 超时后：

- 周期发布 `/move_base/cancel`，阻止 move_base 持续按错误位姿输出。
- 屏蔽 `/cmd_vel` 和普通底盘命令。
- `pose_quality=WARN/FAULT/UNKNOWN/超时` 时都尝试低速蠕动，磨盘按 `localization_watchdog_disc_speed_scale` 降到锁定前速度的 0.5。
- 蠕动命令为本体系直行，左右轮等幅，不叠加角速度。
- 只有不能安全蠕动时才停车并默认停磨盘，例如 scan 超时、前方障碍、超过距离/时间上限、任务未使能或底盘未 enable；如现场硬件要求锁定即停磨盘，可将 `localization_watchdog_stop_disc_on_lock` 设为 `true`。
- 磨盘速度写入带斜坡限幅，默认每周期最多变化 `disc_speed_max_step=200`，避免恢复时电流冲击。
- 仅在任务使能且底盘 enabled 时允许本体系 `+x` 低速蠕动。

默认滑行策略：

- 速度：`0.05 m/s`
- 最大距离：`0.30 m`
- 最大时长：`10 s`
- 前方检测扇区：`45 deg`
- 前方停止距离：`0.40 m`
- `/scan` 超时：`0.5 s`

滑行只用于短暂定位恢复窗口，不按 map 方向纠偏。一旦达到距离/时间上限、前方有障碍或 scan 超时，会保持停车，直到定位质量恢复并由调度器重新发布当前任务段目标。

## 主要话题

- 订阅：
  - `/cmd_vel`
  - `/chassis/task_enable`
  - `/chassis/wheel_speed_cmd`
  - `/chassis/disc_speed_cmd`
  - `/chassis/disc_enable_cmd`
  - `/chassis/work_mode_cmd`
  - `/chassis/disc_lift_cmd`
  - `/chassis/light_cmd`
- 发布：
  - `/chassis/status`
  - `/chassis/wheel_speed_state`
  - `/chassis/localization_watchdog_status`
  - `/diagnostics`

## 服务

- `/chassis/enable`：启用/停用底盘输出。
- `/chassis/clear_fault`：故障清除占位服务。
- `/chassis/localization_watchdog_release`：当关闭自动释放时手动释放定位看门狗。
- `/chassis/set_manual_override`：手动接管开关。

## 运行

```bash
roslaunch grinder_chassis_driver chassis_driver.launch
```

关键参数在 `config/chassis_driver.yaml`，现场重点调这些值：

- `cmd_vel_wheel_track_m`
- `cmd_vel_wheel_radius_m`
- `cmd_vel_gear_ratio`
- `cmd_vel_max_input_v`
- `cmd_vel_max_input_w`
- `localization_recovery_glide_speed_mps`
- `localization_recovery_max_distance_m`
- `localization_recovery_obstacle_stop_m`
- `localization_watchdog_stop_disc_on_lock`
- `localization_watchdog_stop_disc_when_not_gliding`
- `localization_watchdog_disc_speed_scale`
- `disc_speed_max_step`
- `manual_override_cancel_navigation`

## 运行 看门狗配置
[Grinder/catkin_ws/src/grinder_chassis_driver/config/chassis_driver.yaml (line 74)](/E:/work1/Grinder/catkin_ws/src/grinder_chassis_driver/config/chassis_driver.yaml:74)
[Grinder/catkin_ws/src/2-dnavigation-package/slamware_ros_sdk/launch/slamware_ros_sdk_server_node.launch (line 53)](/E:/work1/Grinder/catkin_ws/src/2-dnavigation-package/slamware_ros_sdk/launch/slamware_ros_sdk_server_node.launch:53)