set(srt_client_py
  __init__.py
  srtantn.py
  srtbase.py
  srtconf.py
  srtconn.py
  srtpara.py
  srtsrc.py
  )

python_install_module(srt_client ${srt_client_py})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
