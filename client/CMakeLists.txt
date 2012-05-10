set(srt_client_py
  srt_client/srtconn.py
  )

python_install_module(srt_client ${srt_client_py})
install(PROGRAMS main.py DESTINATION ${BIN_INSTALL_DIR} RENAME srt_client)
