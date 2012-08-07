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

function(check_all_modules TARGET)
  set(ARG_LIST ${ARGN})
  list(LENGTH ARG_LIST LEN)
  while(LEN GREATER 0)
    list(GET ARG_LIST 0 VAR)
    list(REMOVE_AT ARG_LIST 0)
    list(LENGTH ARG_LIST LEN)
    if(LEN EQUAL 0)
      break()
    endif()
    list(GET ARG_LIST 0 NEXT_ARG)
    list(REMOVE_AT ARG_LIST 0)
    list(LENGTH ARG_LIST LEN)
    if(NEXT_ARG STREQUAL "REQUIRED")
      if(LEN EQUAL 0)
        break()
      endif()
      list(GET ARG_LIST 0 NEXT_ARG)
      list(REMOVE_AT ARG_LIST 0)
      list(LENGTH ARG_LIST LEN)
      pkg_check_modules(${VAR} REQUIRED ${NEXT_ARG})
    else()
      pkg_check_modules(${VAR} ${NEXT_ARG})
    endif()
    set(${VAR}_INCLUDE_DIRS ${${VAR}_INCLUDE_DIRS} PARENT_SCOPE)
    set(TARGET_INCLUDE_DIRS ${TARGET_INCLUDE_DIRS} ${${VAR}_INCLUDE_DIRS})

    set(${VAR}_LIBRARIES ${${VAR}_LIBRARIES} PARENT_SCOPE)
    set(TARGET_LINK ${TARGET_LINK} ${${VAR}_LIBRARIES})

    set(${VAR}_LIBRARIES_DIRS ${${VAR}_LIBRARIES_DIRS} PARENT_SCOPE)
    set(TARGET_LINK_DIRS ${TARGET_LINK_DIRS} ${${VAR}_LIBRARIES_DIRS})

    set(${VAR}_LDFLAGS ${${VAR}_LDFLAGS} PARENT_SCOPE)
    set(${VAR}_LDFLAGS_OTHER ${${VAR}_LDFLAGS_OTHER} PARENT_SCOPE)
    set(TARGET_LDFLAGS ${TARGET_LDFLAGS} ${${VAR}_LDFLAGS}
      ${${VAR}_LDFLAGS_OTHER})

    set(${VAR}_CFLAGS ${${VAR}_CFLAGS} PARENT_SCOPE)
    set(${VAR}_CFLAGS_OTHER ${${VAR}_CFLAGS_OTHER} PARENT_SCOPE)
    set(TARGET_CFLAGS ${TARGET_CFLAGS} ${${VAR}_CFLAGS} ${${VAR}_CFLAGS_OTHER})
  endwhile()
  set(${TARGET}_INCLUDE_DIRS ${TARGET_INCLUDE_DIRS} PARENT_SCOPE)
  set(${TARGET}_LINK ${TARGET_LINK} PARENT_SCOPE)
  set(${TARGET}_LINK_DIRS ${TARGET_LINK_DIRS} PARENT_SCOPE)
  set(${TARGET}_LDFLAGS ${TARGET_LDFLAGS} PARENT_SCOPE)
  set(${TARGET}_CFLAGS ${TARGET_CFLAGS} PARENT_SCOPE)
  set(${TARGET}_FLAGS ${TARGET_CFLAGS} ${TARGET_LDFLAGS} PARENT_SCOPE)
endfunction()
