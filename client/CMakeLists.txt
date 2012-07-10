add_subdirectory(srt_client)
add_subdirectory(config)
install(PROGRAMS main.py DESTINATION ${BIN_INSTALL_DIR} RENAME srt_client)
install(PROGRAMS srt_helper.py DESTINATION ${SRT_HELPER_PATH})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
