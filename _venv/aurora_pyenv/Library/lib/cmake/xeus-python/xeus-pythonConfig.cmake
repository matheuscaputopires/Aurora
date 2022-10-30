############################################################################
# Copyright (c) 2018, Martin Renou, Johan Mabille, Sylvain Corlay and      #
# Wolf Vollprecht                                                          #
#                                                                          #
# Distributed under the terms of the BSD 3-Clause License.                 #
#                                                                          #
# The full license is in the file LICENSE, distributed with this software. #
############################################################################

# xeus-python cmake module
# This module sets the following variables in your project::
#
#   xeus-python_FOUND - true if xeus-python found on the system
#   xeus-python_INCLUDE_DIRS - the directory containing xeus-python headers
#   xeus-python_LIBRARY - the library for dynamic linking
#   xeus-python_STATIC_LIBRARY - the library for static linking


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was xeus-pythonConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR};${CMAKE_MODULE_PATH}")



include(CMakeFindDependencyMacro)
find_dependency(xeus 0.24.0)
find_dependency(cppzmq )
find_dependency(pybind11 2.2.4)

if (NOT TARGET xeus-python)
    include("${CMAKE_CURRENT_LIST_DIR}/xeus-pythonTargets.cmake")

    get_target_property(xeus-python_INCLUDE_DIR xeus-python INTERFACE_INCLUDE_DIRECTORIES)
    get_target_property(xeus-python_LIBRARY xeus-python LOCATION)

    if (TARGET xeus-python-static)
        get_target_property(xeus-python_STATIC_LIBRARY xeus-python-static LOCATION)
    endif ()
endif ()
