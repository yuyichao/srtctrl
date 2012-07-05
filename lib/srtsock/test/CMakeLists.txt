# add_test(NAME testsock
#   COMMAND env GI_TYPELIB_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
#   LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
#   ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_sock.py)

set(TEST_BUFF_SOURCE
  test_buff.c
  )

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/.. ${SRTSOCK_INCLUDE_DIRS})
add_executable(test_srtbuff ${TEST_BUFF_SOURCE})
target_link_libraries(test_srtbuff srtsock)

add_run(run_srtbuff
  COMMAND env LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  ${CMAKE_CURRENT_BINARY_DIR}/test_srtbuff)

add_run(test_srtsock
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMAND env GI_TYPELIB_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}/..
  ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_srtsock.py)
