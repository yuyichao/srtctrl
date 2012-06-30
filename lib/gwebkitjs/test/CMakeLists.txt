add_test(NAME makevalue
  COMMAND env GI_TYPELIB_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_makevalue.py)

set(TEST_CLOSURE_SOURCE
  test_closure.c
  )

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/.. ${GWEBKITJS_INCLUDE_DIRS})
add_executable(test_closure ${TEST_CLOSURE_SOURCE})
target_link_libraries(test_closure gwebkitjs)

add_test(NAME closure
  COMMAND env LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  ${CMAKE_CURRENT_BINARY_DIR}/test_closure)

add_test(NAME jsbase
  COMMAND env GI_TYPELIB_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_jsbase.py)
