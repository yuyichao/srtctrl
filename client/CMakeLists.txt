set(srt_client_py
  srt_client/__init__.py
  srt_client/srtantn.py
  srt_client/srtbase.py
  srt_client/srtconf.py
  srt_client/srtconn.py
  srt_client/srtpara.py
  srt_client/srtsrc.py
  )

python_install_module(srt_client ${srt_client_py})
install(PROGRAMS main.py DESTINATION ${BIN_INSTALL_DIR} RENAME srt_client)
