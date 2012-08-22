set(srt_modules_py
  0dispatch_basic.py
  0init_default.py
  purcell_helper.py
  purcell.py
  python_slave.py
  timer.py
  track_ephem.py
  tracker.py
  track_simple.py
  webkit.py
  # webkitgtk3.py
  zwicky_cmd_slave.py
  zwicky_cmds.py
  zwicky_helper.py
  zwicky_logger.py
  zwicky_motor.py
  zwicky_properties.py
  zwicky.py
  zwicky_radio.py
  zwicky_tracker.py
  )

install(FILES ${srt_modules_py}
  DESTINATION ${SRT_MODULES_PATH})
