add_subdirectory(srt_client)
install(PROGRAMS main.py DESTINATION ${BIN_INSTALL_DIR} RENAME srt_client)
