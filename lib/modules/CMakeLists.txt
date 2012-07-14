set(srt_modules_py
  0init_default.py
  0dispatch_basic.py
  purcell.py
  purcell_helper.py
  zwicky.py
  zwicky_helper.py
  zwicky_motor.py
  zwicky_radio.py
  zwicky_tracker.py
  track_simple.py
  tracker.py
  )

install(FILES ${srt_modules_py}
  DESTINATION ${SRT_MODULES_PATH})
