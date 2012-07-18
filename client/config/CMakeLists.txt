set(config_files
  generic.py
  zwicky.py
  )

install(FILES ${config_files}
  DESTINATION ${SRT_CONFIG_PATH})
