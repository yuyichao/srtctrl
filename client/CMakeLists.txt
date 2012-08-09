add_subdirectory(srt_client)
add_subdirectory(config)

install(PROGRAMS srt_helper.py DESTINATION ${SRT_HELPER_PATH})
python_install_as_module(srt_slave.py)

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
