cmake_minimum_required(VERSION 2.8)
if(CMAKE_VERSION VERSION_LESS 2.8.4)
  set(FALLBACK_CMAKE283 1)
else()
  set(FALLBACK_CMAKE283 0)
  cmake_policy(SET CMP0017 OLD)
endif()
project(srtctrl C)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake
  ${CMAKE_MODULE_PATH})

include(PythonMacros)
include(CheckAll)
include(AddRun)

option(ENABLE_TEST "Test build" Off)

option(ENABLE_FRONT "Frontends" On)
option(ENABLE_BACK "Beckend" On)

# option(ENABLE_FRONT_WEBKITGTK3 "GWebKitJS library for webkitgtk-3 frontend" On)

# This two options will automatically be enabled if needed
# option(ENABLE_GWEBKITJS "GWebKitJS library for webkitgtk-3 frontend" Off)
option(ENABLE_SRTSOCK "Srtsock library for communication in backend" Off)
option(ENABLE_SRTCOMM "General python modules for backend" Off)

if(ENABLE_TEST)
  enable_testing()
endif()

if(NOT ENABLE_FRONT)
  # set(ENABLE_FRONT_WEBKITGTK3 Off)
endif()

# if(ENABLE_FRONT_WEBKITGTK3)
#   set(ENABLE_GWEBKITJS On)
# endif()

if(ENABLE_BACK)
  set(ENABLE_SRTSOCK On)
  set(ENABLE_SRTCOMM On)
endif()

if(NOT DEFINED BIN_INSTALL_DIR)
  set(BIN_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/bin")
endif()

if(NOT DEFINED LIB_INSTALL_DIR)
  set(LIB_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/lib")
endif()

if(NOT DEFINED PKGCONF_DIR)
  set(PKGCONF_DIR "${LIB_INSTALL_DIR}/pkgconfig")
endif()

if(NOT DEFINED DATA_INSTALL_DIR)
  set(DATA_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/share/srtctl")
endif()

if(NOT DEFINED HEADER_INSTALL_DIR)
  set(HEADER_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/include")
endif()

if(NOT DEFINED CONF_INSTALL_DIR)
  set(CONF_INSTALL_DIR "/etc")
endif()

if(NOT DEFINED SRT_LIB_PATH)
  set(SRT_LIB_PATH "${LIB_INSTALL_DIR}/srtctrl")
endif()

if(NOT DEFINED SRT_MODULES_PATH)
  set(SRT_MODULES_PATH "${SRT_LIB_PATH}/modules")
endif()

if(NOT DEFINED SRT_HELPER_PATH)
  set(SRT_HELPER_PATH "${SRT_LIB_PATH}")
endif()

if(NOT DEFINED SRT_CONFIG_PATH)
  set(SRT_CONFIG_PATH "${DATA_INSTALL_DIR}/config")
endif()

if(NOT DEFINED SRT_INITIALIZER)
  set(SRT_INITIALIZER "default")
endif()

set(CMAKE_C_FLAGS "-g -pipe -Wall -Wextra -Wno-sign-compare -Wno-unused-parameter ${CMAKE_C_FLAGS}")
set(CMAKE_CXX_FLAGS "-g -pipe -Wall -Wextra -Wno-sign-compare -Wno-unused-parameter ${CMAKE_CXX_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS}")
set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS}")

if(ENABLE_BACK)
  add_subdirectory(client)
endif()

add_subdirectory(lib)

if(ENABLE_FRONT)
  add_subdirectory(front)
endif()

add_subdirectory(tools)
