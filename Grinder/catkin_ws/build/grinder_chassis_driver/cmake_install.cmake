# Install script for directory: /home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/neardi/work/Grinder/catkin_ws/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  include("/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/safe_execute_install.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver/msg" TYPE FILE FILES
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedCommand.msg"
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/WheelSpeedState.msg"
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/msg/ChassisStatus.msg"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver/srv" TYPE FILE FILES
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/EnableChassis.srv"
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/srv/ClearFault.srv"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver/cmake" TYPE FILE FILES "/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/installspace/grinder_chassis_driver-msg-paths.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/home/neardi/work/Grinder/catkin_ws/devel/include/grinder_chassis_driver")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roseus/ros" TYPE DIRECTORY FILES "/home/neardi/work/Grinder/catkin_ws/devel/share/roseus/ros/grinder_chassis_driver")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/common-lisp/ros" TYPE DIRECTORY FILES "/home/neardi/work/Grinder/catkin_ws/devel/share/common-lisp/ros/grinder_chassis_driver")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gennodejs/ros" TYPE DIRECTORY FILES "/home/neardi/work/Grinder/catkin_ws/devel/share/gennodejs/ros/grinder_chassis_driver")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  execute_process(COMMAND "/usr/bin/python3" -m compileall "/home/neardi/work/Grinder/catkin_ws/devel/lib/python3/dist-packages/grinder_chassis_driver")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python3/dist-packages" TYPE DIRECTORY FILES "/home/neardi/work/Grinder/catkin_ws/devel/lib/python3/dist-packages/grinder_chassis_driver" REGEX "/\\_\\_init\\_\\_\\.py$" EXCLUDE REGEX "/\\_\\_init\\_\\_\\.pyc$" EXCLUDE)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python3/dist-packages" TYPE DIRECTORY FILES "/home/neardi/work/Grinder/catkin_ws/devel/lib/python3/dist-packages/grinder_chassis_driver" FILES_MATCHING REGEX "/home/neardi/work/Grinder/catkin_ws/devel/lib/python3/dist-packages/grinder_chassis_driver/.+/__init__.pyc?$")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/installspace/grinder_chassis_driver.pc")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver/cmake" TYPE FILE FILES "/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/installspace/grinder_chassis_driver-msg-extras.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver/cmake" TYPE FILE FILES
    "/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/installspace/grinder_chassis_driverConfig.cmake"
    "/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/installspace/grinder_chassis_driverConfig-version.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver" TYPE FILE FILES "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/package.xml")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/grinder_chassis_driver" TYPE PROGRAM FILES "/home/neardi/work/Grinder/catkin_ws/build/grinder_chassis_driver/catkin_generated/installspace/chassis_driver_node.py")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/grinder_chassis_driver" TYPE DIRECTORY FILES
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/launch"
    "/home/neardi/work/Grinder/catkin_ws/src/grinder_chassis_driver/config"
    )
endif()

