set(FRONT_DIR "${CMAKE_CURRENT_BINARY_DIR}/..")
add_run(test_frontend
  COMMAND GI_TYPELIB_PATH=${FRONT_DIR}/../lib/gwebkitjs
  "PYTHONPATH=${FRONT_DIR}:${FRONT_DIR}/../lib"
  "LD_LIBRARY_PATH=${FRONT_DIR}/../lib/gwebkitjs"
  "${PYTHON_EXECUTABLE}" ${CMAKE_CURRENT_SOURCE_DIR}/test_front.py
  ${CMAKE_CURRENT_SOURCE_DIR}/../data/index.html)
