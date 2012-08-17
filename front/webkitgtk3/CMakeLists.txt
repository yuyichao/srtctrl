if(NOT DEFINED SRT_WKGTK_FRONT)
  set(SRT_WKGTK_FRONT "srt_wkgtk")
endif()

if(NOT DEFINED SRT_WKGTK_DATA_DIR)
  set(SRT_WKGTK_DATA_DIR "${DATA_INSTALL_DIR}/webkitgtk3")
endif()

set(SRT_WEBKITGTK3_PATH "${SRT_WKGTK_DATA_DIR}/index.html")

configure_file(main.py.in
  "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  IMMEDIATE @ONLY)
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  DESTINATION ${BIN_INSTALL_DIR}
  RENAME ${SRT_WKGTK_FRONT})

add_subdirectory(srt_wkgtk)
add_subdirectory(data)

if(ENABLE_TEST)
  set(BINARY_LIB_DIR "${PROJECT_BINARY_DIR}/lib")
  set(FRONT_DIR "${PROJECT_BINARY_DIR}/front/webkitgtk3")
  add_run(test_webkitgtk_main
    COMMAND env
    "GI_TYPELIB_PATH=${BINARY_LIB_DIR}/srtsock:${BINARY_LIB_DIR}/gwebkitjs"
    "PYTHONPATH=${FRONT_DIR}:${BINARY_LIB_DIR}:${PROJECT_BINARY_DIR}/client"
    "LD_LIBRARY_PATH=${BINARY_LIB_DIR}/srtsock:${BINARY_LIB_DIR}/gwebkitjs"
    "SRT_CONFIG_PATH=${PROJECT_SOURCE_DIR}/client/config"
    "SRT_HELPER_PATH=${PROJECT_SOURCE_DIR}/client"
    "SRT_MODULES_PATH=${PROJECT_SOURCE_DIR}/lib/modules"
    "SRT_WEBKITGTK3_PATH=${CMAKE_CURRENT_SOURCE_DIR}/data/index.html"
    "${PYTHON_EXECUTABLE}" "${CMAKE_CURRENT_BINARY_DIR}/main.py"
    -f "${PROJECT_SOURCE_DIR}/client/test/test_slave.cmd"
    )
endif()
