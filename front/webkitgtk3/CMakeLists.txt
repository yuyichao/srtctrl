add_subdirectory(srt_wkgtk)
add_subdirectory(data)

if(NOT DEFINED SRT_WKGTK_FRONT)
  set(SRT_WKGTK_FRONT "srt_wkgtk")
endif()

configure_file(main.py.in
  "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  IMMEDIATE @ONLY)
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  DESTINATION ${BIN_INSTALL_DIR}
  RENAME ${SRT_WKGTK_FRONT})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
