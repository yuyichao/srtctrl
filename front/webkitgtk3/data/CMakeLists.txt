set(frontend_src
  index.html
  srt.js
  jquery.min.js
  )

install(FILES ${frontend_src}
  DESTINATION ${DATA_INSTALL_DIR})
