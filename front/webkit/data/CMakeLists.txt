set(frontend_src
  index.html
  )

install(FILES ${frontend_src}
  DESTINATION "${SRT_WEBKIT_DATA_DIR}")

install(DIRECTORY css/ js/
  DESTINATION "${SRT_WEBKIT_DATA_DIR}")
