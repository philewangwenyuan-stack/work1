# grinder_chassis_driver

`grinder_chassis_driver` 是研磨机器人底盘驱动包，使用 ROS1 Python 节点通过 RS485/Modbus RTU 控制底盘、磨盘、升降和照明，并把 `/cmd_vel` 转换为左右轮速度。

## 核心职责

- 底盘输出：左右轮速度、磨盘转速、磨盘启停、工作模式、升降和照明。
- 状态回读：周期读取寄存器并发布 `/chassis/status`、`/chassis/wheel_speed_state` 和 `/diagnostics`。
- `/cmd_vel` 转换：根据轮距、轮半径、减速比和方向修正参数生成左右轮转速。
- 手动接管：支持 `/chassis/manual_override`，接管时忽略 `/cmd_vel` 并可取消导航目标。
- 定位看门狗：根据 Aurora system/relocalization 状态和 `/pose_quality` 锁定底盘，阻断错误位姿下的导航速度。

## 定位看门狗

订阅：

- `/slamware_ros_sdk_server_node/system_status`
- `/slamware_ros_sdk_server_node/relocalization_status`
- `/slamware_ros_sdk_server_node/pose_quality`
- `/slamware_ros_sdk_server_node/scan`

发布：

- `/chassis/localization_watchdog_status`

触发 FAULT 或状态超时后：

- 周期发布 `/move_base/cancel`，阻止 move_base 持续按错误位姿输出。
- 屏蔽 `/cmd_vel` 和普通底盘命令。
- 关闭磨盘。
- 仅在任务使能且底盘 enabled 时允许本体系 `+x` 低速滑行。

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
