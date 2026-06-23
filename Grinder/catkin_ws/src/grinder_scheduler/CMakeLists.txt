cmake_minimum_required(VERSION 3.0.2)
project(grinder_scheduler)

find_package(OpenCV REQUIRED)

find_package(catkin REQUIRED COMPONENTS
  diagnostic_msgs
  geometry_msgs
  grinder_chassis_driver
  message_generation
  nav_msgs
  rospy
  sensor_msgs
  slamware_ros_sdk
  std_msgs
  std_srvs
)

catkin_python_setup()

add_message_files(
  FILES
  SchedulerStatus.msg
  MapPreviewMetadata.msg
)

generate_messages(
  DEPENDENCIES
  geometry_msgs
  std_msgs
)

add_library(grinder_map_render_core SHARED
  src/map_render_core.cpp
)
target_include_directories(grinder_map_render_core PRIVATE
  ${OpenCV_INCLUDE_DIRS}
)
target_link_libraries(grinder_map_render_core
  ${OpenCV_LIBRARIES}
)
set_property(TARGET grinder_map_render_core PROPERTY CXX_STANDARD 11)
set_property(TARGET grinder_map_render_core PROPERTY CXX_STANDARD_REQUIRED ON)

catkin_package(
  LIBRARIES grinder_map_render_core
  CATKIN_DEPENDS diagnostic_msgs geometry_msgs grinder_chassis_driver message_runtime nav_msgs rospy sensor_msgs slamware_ros_sdk std_msgs std_srvs
)

catkin_install_python(PROGRAMS
  scripts/scheduler_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(TARGETS grinder_map_render_core
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY
  launch
  config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

if(CATKIN_ENABLE_TESTING)
  catkin_add_nosetests(test)
endif()
