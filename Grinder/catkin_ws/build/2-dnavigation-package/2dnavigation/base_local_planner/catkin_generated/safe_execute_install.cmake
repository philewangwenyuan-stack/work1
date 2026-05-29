execute_process(COMMAND "/home/neardi/work/Grinder/catkin_ws/build/2-dnavigation-package/2dnavigation/base_local_planner/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/neardi/work/Grinder/catkin_ws/build/2-dnavigation-package/2dnavigation/base_local_planner/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
