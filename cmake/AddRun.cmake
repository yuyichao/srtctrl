include(CMakeParseArguments)

function(add_run run_name)
  set(options)
  set(oneValueArgs "WORKING_DIRECTORY")
  set(multiValueArgs "COMMAND")
  cmake_parse_arguments(ADD_RUN "${options}"
    "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
  set(args COMMAND ${ADD_RUN_COMMAND})
  if(ADD_RUN_WORKING_DIRECTORY)
    set(args ${args} WORKING_DIRECTORY ${ADD_RUN_WORKING_DIRECTORY})
  endif()
  add_custom_target(${run_name} ${args})
endfunction()