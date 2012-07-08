cmake_minimum_required(VERSION 2.6)
cmake_policy(SET CMP0017 OLD)
project(srtctrl)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake
  ${CMAKE_MODULE_PATH})

include(PythonMacros)
include(CheckAll)
include(GObjectIntrospection)
include(AddRun)

option(ENABLE_TEST "Test build" OFF)

if(ENABLE_TEST)
  enable_testing()
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

if(NOT DEFINED SRT_INITIALIZER)
  set(SRT_INITIALIZER "default")
endif()
set(CMAKE_C_FLAGS "-g -pipe -Wall -Wextra -Wno-sign-compare -Wno-unused-parameter -Wl,--as-needed ${CMAKE_C_FLAGS}")
set(CMAKE_CXX_FLAGS "-g -pipe -Wall -Wextra -Wno-sign-compare -Wno-unused-parameter -Wl,--as-needed ${CMAKE_CXX_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS "-Wl,--as-needed ${CMAKE_SHARED_LINKER_FLAGS}")
set(CMAKE_MODULE_LINKER_FLAGS "-Wl,--as-needed ${CMAKE_MODULE_LINKER_FLAGS}")
add_subdirectory(client)
add_subdirectory(lib)
add_subdirectory(front)
