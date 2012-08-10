set(frontend_src
  index.html
  )

install(FILES ${frontend_src}
  DESTINATION ${DATA_INSTALL_DIR})

# add_subdirectory(css)
# add_subdirectory(js)
