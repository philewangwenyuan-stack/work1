cmake_minimum_required(VERSION 3.0.2)
project(grinder_chassis_driver)

find_package(catkin REQUIRED COMPONENTS
  actionlib_msgs
  diagnostic_msgs
  geometry_msgs
  message_generation
  rospy
  sensor_msgs
  slamware_ros_sdk
  std_msgs
  std_srvs
)

catkin_python_setup()

add_message_files(
  FILES
  WheelSpeedCommand.msg
  WheelSpeedState.msg
  ChassisStatus.msg
  LocalizationWatchdogStatus.msg
)

add_service_files(
  FILES
  EnableChassis.srv
  ClearFault.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS actionlib_msgs diagnostic_msgs geometry_msgs message_runtime rospy sensor_msgs slamware_ros_sdk std_msgs std_srvs
)

catkin_install_python(PROGRAMS
  scripts/chassis_driver_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY
  launch
  config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
