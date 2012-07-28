add_subdirectory(srt_client)
add_subdirectory(config)

install(PROGRAMS srt_helper.py DESTINATION ${SRT_HELPER_PATH})

if(ENABLE_TEST)
#  add_subdirectory(test)
endif()
