# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "grinder_scheduler: 2 messages, 0 services")

set(MSG_I_FLAGS "-Igrinder_scheduler:/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg;-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(grinder_scheduler_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" NAME_WE)
add_custom_target(_grinder_scheduler_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_scheduler" "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" "geometry_msgs/Pose2D:std_msgs/Header"
)

get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" NAME_WE)
add_custom_target(_grinder_scheduler_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_scheduler" "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" "geometry_msgs/Pose:geometry_msgs/Quaternion:geometry_msgs/Point:std_msgs/Header"
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose2D.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_scheduler
)
_generate_msg_cpp(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_scheduler
)

### Generating Services

### Generating Module File
_generate_module_cpp(grinder_scheduler
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_scheduler
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(grinder_scheduler_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(grinder_scheduler_generate_messages grinder_scheduler_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_cpp _grinder_scheduler_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_cpp _grinder_scheduler_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_scheduler_gencpp)
add_dependencies(grinder_scheduler_gencpp grinder_scheduler_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_scheduler_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose2D.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_scheduler
)
_generate_msg_eus(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_scheduler
)

### Generating Services

### Generating Module File
_generate_module_eus(grinder_scheduler
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_scheduler
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(grinder_scheduler_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(grinder_scheduler_generate_messages grinder_scheduler_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_eus _grinder_scheduler_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_eus _grinder_scheduler_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_scheduler_geneus)
add_dependencies(grinder_scheduler_geneus grinder_scheduler_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_scheduler_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose2D.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_scheduler
)
_generate_msg_lisp(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_scheduler
)

### Generating Services

### Generating Module File
_generate_module_lisp(grinder_scheduler
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_scheduler
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(grinder_scheduler_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(grinder_scheduler_generate_messages grinder_scheduler_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_lisp _grinder_scheduler_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_lisp _grinder_scheduler_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_scheduler_genlisp)
add_dependencies(grinder_scheduler_genlisp grinder_scheduler_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_scheduler_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose2D.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_scheduler
)
_generate_msg_nodejs(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_scheduler
)

### Generating Services

### Generating Module File
_generate_module_nodejs(grinder_scheduler
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_scheduler
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(grinder_scheduler_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(grinder_scheduler_generate_messages grinder_scheduler_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_nodejs _grinder_scheduler_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_nodejs _grinder_scheduler_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_scheduler_gennodejs)
add_dependencies(grinder_scheduler_gennodejs grinder_scheduler_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_scheduler_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose2D.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler
)
_generate_msg_py(grinder_scheduler
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler
)

### Generating Services

### Generating Module File
_generate_module_py(grinder_scheduler
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(grinder_scheduler_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(grinder_scheduler_generate_messages grinder_scheduler_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/SchedulerStatus.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_py _grinder_scheduler_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_scheduler/msg/MapPreviewMetadata.msg" NAME_WE)
add_dependencies(grinder_scheduler_generate_messages_py _grinder_scheduler_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_scheduler_genpy)
add_dependencies(grinder_scheduler_genpy grinder_scheduler_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_scheduler_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_scheduler)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_scheduler
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(grinder_scheduler_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()
if(TARGET std_msgs_generate_messages_cpp)
  add_dependencies(grinder_scheduler_generate_messages_cpp std_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_scheduler)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_scheduler
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(grinder_scheduler_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()
if(TARGET std_msgs_generate_messages_eus)
  add_dependencies(grinder_scheduler_generate_messages_eus std_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_scheduler)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_scheduler
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(grinder_scheduler_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()
if(TARGET std_msgs_generate_messages_lisp)
  add_dependencies(grinder_scheduler_generate_messages_lisp std_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_scheduler)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_scheduler
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(grinder_scheduler_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()
if(TARGET std_msgs_generate_messages_nodejs)
  add_dependencies(grinder_scheduler_generate_messages_nodejs std_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler
    DESTINATION ${genpy_INSTALL_DIR}
    # skip all init files
    PATTERN "__init__.py" EXCLUDE
    PATTERN "__init__.pyc" EXCLUDE
  )
  # install init files which are not in the root folder of the generated code
  string(REGEX REPLACE "([][+.*()^])" "\\\\\\1" ESCAPED_PATH "${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler")
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_scheduler
    DESTINATION ${genpy_INSTALL_DIR}
    FILES_MATCHING
    REGEX "${ESCAPED_PATH}/.+/__init__.pyc?$"
  )
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(grinder_scheduler_generate_messages_py geometry_msgs_generate_messages_py)
endif()
if(TARGET std_msgs_generate_messages_py)
  add_dependencies(grinder_scheduler_generate_messages_py std_msgs_generate_messages_py)
endif()
