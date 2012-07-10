set(srt_client_py
  __init__.py
  srtconf.py
  srtremote.py
  srtcenter.py
  )

python_install_module(srt_client ${srt_client_py})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
