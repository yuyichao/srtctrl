#   Copyright (C) 2012~2012 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
