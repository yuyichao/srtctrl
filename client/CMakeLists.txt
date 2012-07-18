add_subdirectory(srt_client)
add_subdirectory(config)

configure_file(main.py.in
  "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  IMMEDIATE @ONLY)
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  DESTINATION ${BIN_INSTALL_DIR}
  RENAME ${SRT_CLIENT_BIN_NAME})
install(PROGRAMS srt_helper.py DESTINATION ${SRT_HELPER_PATH})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
