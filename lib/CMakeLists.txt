if(ENABLE_SRTCOMM)
  add_subdirectory(srt_comm)
  add_subdirectory(modules)
endif()

if(ENABLE_SRTSOCK)
  add_subdirectory(srtsock)
endif()

# if(ENABLE_GWEBKITJS)
#   add_subdirectory(gwebkitjs)
#   add_subdirectory(pywkjs)
# endif()
