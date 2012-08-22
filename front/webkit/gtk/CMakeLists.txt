if(NOT DEFINED SRT_WEBKITGTK_FRONT)
  set(SRT_WEBKITGTK_FRONT "srt_gtk")
endif()

configure_file(main.py.in
  "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  IMMEDIATE @ONLY)
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  DESTINATION ${BIN_INSTALL_DIR}
  RENAME ${SRT_WEBKITGTK_FRONT})

add_subdirectory(srt_webkit)

if(ENABLE_TEST)
  set(BINARY_LIB_DIR "${PROJECT_BINARY_DIR}/lib")
  set(FRONT_DIR "${PROJECT_BINARY_DIR}/front/webkit/gtk")
  add_run(test_webkitgtk
    COMMAND env
    "GI_TYPELIB_PATH=${BINARY_LIB_DIR}/srtsock"
    "PYTHONPATH=${FRONT_DIR}:${BINARY_LIB_DIR}:${PROJECT_BINARY_DIR}/client"
    "LD_LIBRARY_PATH=${BINARY_LIB_DIR}/srtsock"
    "SRT_CONFIG_PATH=${PROJECT_SOURCE_DIR}/client/config"
    "SRT_HELPER_PATH=${PROJECT_SOURCE_DIR}/client"
    "SRT_MODULES_PATH=${PROJECT_SOURCE_DIR}/lib/modules"
    "SRT_WEBKIT_PATH=${CMAKE_CURRENT_SOURCE_DIR}/../data/index.html"
    "${PYTHON_EXECUTABLE}" "${CMAKE_CURRENT_BINARY_DIR}/main.py"
    -f "${PROJECT_SOURCE_DIR}/client/test/test_slave.cmd"
    )
endif()
