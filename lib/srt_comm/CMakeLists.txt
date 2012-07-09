configure_file(_config.py.in
  "${CMAKE_CURRENT_BINARY_DIR}/_config.py"
  IMMEDIATE @ONLY)

set(srt_comm_py
  __init__.py
  jsonstm.py
  srtconn.py
  srtaddr.py
  util.py
  "${CMAKE_CURRENT_BINARY_DIR}/_config.py"
  config.py
  ps.py
  module.py
  error.py
  )

python_install_module(srt_comm ${srt_comm_py})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
