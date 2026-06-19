# 2-dnavigation-package

本目录收纳 Aurora ROS1 驱动、本地导航栈和 Slamtec Aurora Remote SDK 依赖，是研磨机器人导航链路的基础目录。

## 目录说明

- `slamware_ros_sdk`：本项目使用的 Aurora ROS1 server/client 包，已经加入位姿增强、协方差质量和纯定位模式修正。
- `aurora_remote_public`：Slamtec Aurora Remote SDK 头文件和平台库。
- `2dnavigation`：基于 ROS1 `move_base` 的导航栈源码，包括 `move_base`、`costmap_2d`、`teb_local_planner`、`map_server`、`amcl` 等第三方包。

## 当前导航接法

- Aurora driver 发布 `/slamware_ros_sdk_server_node/robot_pose`、`/slamware_ros_sdk_server_node/odom`、`/slamware_ros_sdk_server_node/scan` 和 `/slamware_ros_sdk_server_node/pose_quality`。
- `move_base` 仍使用现有 TF 链和 `/odom`。
- 项目自有 shadow AMCL 已删除；第三方 `2dnavigation/amcl` 仅作为 vendor 源码保留，不由系统 launch 启动。
- 定位质量由 Aurora 协方差和系统状态判断，底盘看门狗负责阻断错误定位下的速度输出。

## 编译

在 ROS Noetic 环境中：

```bash
cd Grinder/catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make
source devel/setup.bash
```

如果只编译 Aurora driver：

```bash
catkin_make -DCATKIN_WHITELIST_PACKAGES="slamware_ros_sdk"
```

如果只编译底盘和调度包：

```bash
catkin_make -DCATKIN_WHITELIST_PACKAGES="slamware_ros_sdk;grinder_chassis_driver;grinder_scheduler"
```

## 运行入口

整机推荐入口：

```bash
roslaunch grinder_scheduler grinder_system.launch
```

导航栈单独入口：

```bash
roslaunch teb_local_planner_tutorials robot_diff_drive.launch
```
