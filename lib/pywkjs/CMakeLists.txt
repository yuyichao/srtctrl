set(pywkjs_py
  __init__.py
  general.py
  jswrap.py
  pywrap.py
  helper.py
  )

python_install_module(pywkjs ${pywkjs_py})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
