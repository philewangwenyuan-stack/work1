# grinder_scheduler

`grinder_scheduler` 是研磨机器人上层调度包，负责接收 SL-LinkA 任务请求、管理地图、规划覆盖路径，并把当前任务段交给 `move_base` 执行。

## 核心职责

- 任务控制：处理任务配置、开始、暂停、恢复、停止和任务结果上报。
- 地图管理：保存/上传/下载 STCM，维护本地地图索引和预览图。
- 路径规划：调用 `third_party/path_planner/mst25.py` 生成覆盖路径，并发布全局路径和当前活动段路径。
- 导航对接：向 `/move_base_simple/goal` 发布当前段目标，通过 `/chassis/task_enable` 控制底盘是否消费 `/cmd_vel`。
- 模式切换：开始任务前请求 Aurora 进入纯定位模式。

## 关键节点与话题

- 节点：`grinder_scheduler`
- 发布：
  - `/scheduler/status`：调度状态。
  - `/scheduler/map_preview_metadata`：地图预览元数据。
  - `/grinder/GlobalPlanner/plan`：完整规划路径。
  - `/grinder/navigation/active_segment_plan`：当前导航段路径。
  - `/move_base_simple/goal`：当前导航段终点。
  - `/chassis/task_enable`：任务导航使能。
- 订阅：
  - `/cmd_vel`：用于磨盘运动保护判断。
  - `/chassis/status`：底盘在线与执行状态。

## 纯定位模式

任务开始前会连续发布两类请求：

- `/slamware_ros_sdk_server_node/set_map_update`：`enabled=false`
- `/slamware_ros_sdk_server_node/set_map_localization`：`enabled=true`

这两个接口是 topic，没有 ack。日志里的语义是“已请求/已重试”，不是“设备已确认成功”。如果现场需要强确认，需要后续接入 Aurora 可回读的模式状态。

## AMCL 清理说明

本包已经移除 shadow AMCL/ACML 链路，包括 `localization_shadow.launch`、AMCL 配置和 `localization_monitor_node.py`。定位质量现在来自 `slamware_ros_sdk` 发布的 `/pose_quality`，底盘看门狗直接消费该质量状态。

第三方 `2dnavigation/amcl` 包未删除，只是不再由本项目调度链路启动。

## 运行

推荐从系统 launch 启动：

```bash
roslaunch grinder_scheduler grinder_system.launch start_chassis_driver:=true start_navigation:=true
```

单独启动调度器：

```bash
roslaunch grinder_scheduler scheduler.launch
```

## 调试入口

- 查看任务状态：`rostopic echo /scheduler/status`
- 查看当前活动段：`rostopic echo /grinder/navigation/active_segment_plan`
- 查看底盘使能：`rostopic echo /chassis/task_enable`
- 查看定位质量：`rostopic echo /slamware_ros_sdk_server_node/pose_quality`
- 查看看门狗状态：`rostopic echo /chassis/localization_watchdog_status`
## map_aligned and saved-map alignment

`map_aligned` is the external/business map frame used by the tablet, RViz,
task regions, path points, and navigation costmaps. The scheduler keeps tablet
status and preview poses on the same `map_aligned` adapter; APP-only heading
conversion is limited to `sl_status_heading_clockwise` and
`sl_status_heading_offset_deg`.

Saved map records store:

- `alignment_yaw_rad`
- `aligned_front_yaw_deg`
- `alignment_mode`
- `aligned_frame`
- `source_frame`

On map save/download the current alignment is written into the registry. On
upload, map switch, or restart, the scheduler calls
`/slamware_ros_sdk_server_node/set_map_alignment` to restore that value. Legacy
records without alignment metadata are migrated once using the current live
alignment.

## Tablet Planning Contract

The tablet should treat `PathPlanRequest` as the only default command that
generates or refreshes the executable task path. The executable path is a
composition of stable per-work-region bow coverage segments plus connector
segments between regions/laps. Obstacle/avoidance regions default to affecting
only connector planning; they do not change the internal bow coverage pattern.

`TaskConfig` updates and saves task/region settings. `MapEdit` updates map
overlays and marks any existing path stale. `TaskCommand START` reuses the
already planned `current_path`; it only falls back to planning when no path
exists or the saved path was explicitly marked stale.

Compatibility switches are available but default to `false`:

- `task_config_auto_plan`
- `map_edit_auto_plan_when_idle`
- `obstacle_regions_affect_coverage`
- `current_pose_seeds_task_coverage`



终端1
source /opt/ros/noetic/setup.bash
source /home/neardi/work/Grinder/catkin_ws/devel/setup.bash
roscore
终端2
sudo pkill -9 -f scheduler_node.py
sudo pkill -f roslaunch
sudo pkill -f rosmaster
sleep 2
source /opt/ros/noetic/setup.bash
source /home/neardi/work/Grinder/catkin_ws/devel/setup.bash
cd /home/neardi/work/Grinder/catkin_ws
sudo AURORA_IP=192.168.11.1 ./start_grinder_stack.sh


端口监听
cd /home/neardi/work/Grinder/third_party/sl_linka/sdk/python/tools
sudo python3 sl_link_trace.py \
  --iface eth1 \
  --sdk /home/neardi/work/Grinder/third_party/sl_linka/sdk/python
终端4
source /opt/ros/noetic/setup.bash
source /home/neardi/work/Grinder/catkin_ws/devel/setup.bash
cd /home/neardi/work/Grinder/third_party/sl_linka/sdk/python/tools
sudo python3 ./sl_linka_pyqt_debugger.py

rviz
source /opt/ros/noetic/setup.bash
source devel/setup.bash
rviz

chmod +x ~/bin/rviz-fixed
~/bin/rviz-fixed

v w
rostopic echo /cmd_vel
v w频率
rostopic hz /cmd_vel
rostopic hz /move_base/TebLocalPlannerROS/local_plan
top -H -p $(pgrep -n -f 'move_base/move_base')

日志

mkdir -p ~/bags

rosbag record -O ~/bags/track_debug_$(date +%Y%m%d_%H%M%S).bag \
  /tf /tf_static \
  /slamware_ros_sdk_server_node/robot_pose \
  /odom \
  /slamware_ros_sdk_server_node/odom \
  /slamware_ros_sdk_server_node/robot_pose \
  /scan \
  /cmd_vel \
  /chassis/cmd_vel \
  /chassis/wheel_speed_state \
  /chassis/status \
  /move_base_simple/goal \
  /move_base/status \
  /move_base/result \
  /move_base/TebLocalPlannerROS/local_plan \
  /move_base/TebLocalPlannerROS/global_plan \
  /grinder/GlobalPlanner/plan \
  /scheduler/status \
  /diagnostics \
  /rosout

配置查询
rosparam get /move_base/TebLocalPlannerROS/costmap_converter_plugin
重载配置
source /opt/ros/noetic/setup.bash
source /home/neardi/work/Grinder/catkin_ws/devel/setup.bash
rosparam load /home/neardi/work/Grinder/catkin_ws/src/2-dnavigation-package/2dnavigation/teb_local_planner_tutorials/cfg/diff_drive/teb_local_planner_params.yaml /move_base

rosparam load /home/neardi/work/Grinder/catkin_ws/src/2-dnavigation-package/2dnavigation/teb_local_planner_tutorials/cfg/diff_drive/costmap_converter_params.yaml /move_base
重启进程
rosnode kill /move_base

重新编译teb_local_planner
cd /home/neardi/work/Grinder/catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make --pkg teb_local_planner -DCMAKE_BUILD_TYPE=Release
source devel/setup.bash

source /opt/ros/noetic/setup.bash
catkin_make --pkg slamware_ros_sdk
source devel/setup.bash
BYOJRC4UVOBUX1HPZS

sudo python3 sl_link_trace.py \
  --iface ETH1 \
  --sdk /home/neardi/work/Grinder/third_party/sl_linka/sdk/python