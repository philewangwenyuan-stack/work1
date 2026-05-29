# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "grinder_chassis_driver: 3 messages, 2 services")

set(MSG_I_FLAGS "-Igrinder_chassis_driver:/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(grinder_chassis_driver_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" NAME_WE)
add_custom_target(_grinder_chassis_driver_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_chassis_driver" "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" ""
)

get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" NAME_WE)
add_custom_target(_grinder_chassis_driver_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_chassis_driver" "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" "std_msgs/Header"
)

get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" NAME_WE)
add_custom_target(_grinder_chassis_driver_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_chassis_driver" "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" "std_msgs/Header"
)

get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" NAME_WE)
add_custom_target(_grinder_chassis_driver_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_chassis_driver" "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" ""
)

get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" NAME_WE)
add_custom_target(_grinder_chassis_driver_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "grinder_chassis_driver" "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" ""
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_cpp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_cpp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Services
_generate_srv_cpp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
)
_generate_srv_cpp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Module File
_generate_module_cpp(grinder_chassis_driver
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(grinder_chassis_driver_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(grinder_chassis_driver_generate_messages grinder_chassis_driver_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_cpp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_cpp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_cpp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_cpp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_cpp _grinder_chassis_driver_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_chassis_driver_gencpp)
add_dependencies(grinder_chassis_driver_gencpp grinder_chassis_driver_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_chassis_driver_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_eus(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_eus(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Services
_generate_srv_eus(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
)
_generate_srv_eus(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Module File
_generate_module_eus(grinder_chassis_driver
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(grinder_chassis_driver_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(grinder_chassis_driver_generate_messages grinder_chassis_driver_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_eus _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_eus _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_eus _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_eus _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_eus _grinder_chassis_driver_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_chassis_driver_geneus)
add_dependencies(grinder_chassis_driver_geneus grinder_chassis_driver_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_chassis_driver_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_lisp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_lisp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Services
_generate_srv_lisp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
)
_generate_srv_lisp(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Module File
_generate_module_lisp(grinder_chassis_driver
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(grinder_chassis_driver_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(grinder_chassis_driver_generate_messages grinder_chassis_driver_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_lisp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_lisp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_lisp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_lisp _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_lisp _grinder_chassis_driver_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_chassis_driver_genlisp)
add_dependencies(grinder_chassis_driver_genlisp grinder_chassis_driver_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_chassis_driver_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_nodejs(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_nodejs(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Services
_generate_srv_nodejs(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
)
_generate_srv_nodejs(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Module File
_generate_module_nodejs(grinder_chassis_driver
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(grinder_chassis_driver_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(grinder_chassis_driver_generate_messages grinder_chassis_driver_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_nodejs _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_nodejs _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_nodejs _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_nodejs _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_nodejs _grinder_chassis_driver_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_chassis_driver_gennodejs)
add_dependencies(grinder_chassis_driver_gennodejs grinder_chassis_driver_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_chassis_driver_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_py(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
)
_generate_msg_py(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Services
_generate_srv_py(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
)
_generate_srv_py(grinder_chassis_driver
  "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
)

### Generating Module File
_generate_module_py(grinder_chassis_driver
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(grinder_chassis_driver_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(grinder_chassis_driver_generate_messages grinder_chassis_driver_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_py _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_py _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_py _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_py _grinder_chassis_driver_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv" NAME_WE)
add_dependencies(grinder_chassis_driver_generate_messages_py _grinder_chassis_driver_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(grinder_chassis_driver_genpy)
add_dependencies(grinder_chassis_driver_genpy grinder_chassis_driver_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS grinder_chassis_driver_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/grinder_chassis_driver
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_cpp)
  add_dependencies(grinder_chassis_driver_generate_messages_cpp std_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/grinder_chassis_driver
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_eus)
  add_dependencies(grinder_chassis_driver_generate_messages_eus std_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/grinder_chassis_driver
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_lisp)
  add_dependencies(grinder_chassis_driver_generate_messages_lisp std_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/grinder_chassis_driver
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_nodejs)
  add_dependencies(grinder_chassis_driver_generate_messages_nodejs std_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
    DESTINATION ${genpy_INSTALL_DIR}
    # skip all init files
    PATTERN "__init__.py" EXCLUDE
    PATTERN "__init__.pyc" EXCLUDE
  )
  # install init files which are not in the root folder of the generated code
  string(REGEX REPLACE "([][+.*()^])" "\\\\\\1" ESCAPED_PATH "${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver")
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/grinder_chassis_driver
    DESTINATION ${genpy_INSTALL_DIR}
    FILES_MATCHING
    REGEX "${ESCAPED_PATH}/.+/__init__.pyc?$"
  )
endif()
if(TARGET std_msgs_generate_messages_py)
  add_dependencies(grinder_chassis_driver_generate_messages_py std_msgs_generate_messages_py)
endif()
