set(srt_comm_py
  __init__.py
  jsonstm.py
  srtconn.py
  srtaddr.py
  util.py
  )

python_install_module(srt_comm ${srt_comm_py})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
