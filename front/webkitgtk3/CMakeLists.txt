if(NOT DEFINED SRT_WKGTK_FRONT)
  set(SRT_WKGTK_FRONT "srt_wkgtk")
endif()

if(NOT DEFINED SRT_WKGTK_DATA_DIR)
  set(SRT_WKGTK_DATA_DIR "${DATA_INSTALL_DIR}/webkitgtk3")
endif()

configure_file(main.py.in
  "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  IMMEDIATE @ONLY)
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/main.py"
  DESTINATION ${BIN_INSTALL_DIR}
  RENAME ${SRT_WKGTK_FRONT})

add_subdirectory(srt_wkgtk)
add_subdirectory(data)

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
