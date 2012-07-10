set(srt_modules_py
  0init_default.py
  0dispatch_basic.py
  purcell.py
  zwicky.py
  )

install(FILES ${srt_modules_py}
  DESTINATION ${SRT_MODULES_PATH})
