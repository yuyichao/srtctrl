if(NOT DEFINED SRT_WEBKIT_DATA_DIR)
  set(SRT_WEBKIT_DATA_DIR "${DATA_INSTALL_DIR}/webkit")
endif()

set(SRT_WEBKIT_PATH "${SRT_WEBKIT_DATA_DIR}/index.html")

add_subdirectory(gtk)
add_subdirectory(data)
