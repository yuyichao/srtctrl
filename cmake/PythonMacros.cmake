# Python macros
# ~~~~~~~~~~~~~
# This file defines the following macros:
#
# PYTHON_COMPILE(LIST_OF_SOURCE_FILES)
#     Byte compile the py force files listed in the LIST_OF_SOURCE_FILES.
#     Compiled pyc files are stored in PYTHON_COMPILED_FILES, corresponding py
#     files are stored in PYTHON_COMPILE_PY_FILES
#
# PYTHON_INSTALL_ALL(DESINATION_DIR LIST_OF_SOURCE_FILES)
#     Install the LIST_OF_SOURCE_FILES, which is a list of Python .py file,
#     into the destination directory during install. The file will be byte
#     compiled and both the .py file and .pyc file will be installed.
#
# PYTHON_INSTALL_MODULE(MODULE_NAME LIST_OF_SOURCE_FILES)
#     Similiar to PYTHON_INSTALL_ALL(), but the files are automatically
#     installed to the site-package directory of python as module MODULE_NAME.
#
# PYTHON_INSTALL(SOURCE_FILE DESINATION_DIR)
#     Similiar to PYTHON_INSTALL_ALL(), but the order of source file and
#     destination directory is reversed.
#     This macro is provided only for backward compatibility. (And this is
#     the reason of the extra "_ALL" in PYTHON_INSTALL_ALL)
#     use PYTHON_INSTALL_ALL() or PYTHON_INSTALL_MODULE() instead.

#   Copyright (C) 2012~2012 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# This file incorporates work covered by the following copyright and
# permission notice:
#
#     Copyright (c) 2007, Simon Edwards <simon@simonzone.com>
#     Redistribution and use is allowed according to the terms of the BSD
#     license. For details see the accompanying COPYING-CMAKE-SCRIPTS file.
#

function(__PY_GET_UNIQUE_TARGET_NAME _name _unique_name)
  set(propertyName "_PYTHON_UNIQUE_COUNTER_${_name}")
  get_property(currentCounter GLOBAL PROPERTY "${propertyName}")
  if(NOT currentCounter)
    set(currentCounter 1)
  endif()
  set(${_unique_name} "${_name}_${currentCounter}" PARENT_SCOPE)
  math(EXPR currentCounter "${currentCounter} + 1")
  set_property(GLOBAL PROPERTY ${propertyName} ${currentCounter} )
endfunction()

get_filename_component(PYTHON_MACROS_MODULE_PATH
  ${CMAKE_CURRENT_LIST_FILE} PATH)

# Hopefully this will not break anything
find_package(PythonLibrary REQUIRED)

function(_PYTHON_COMPILE SOURCE_FILE)
  find_file(_python_compile_py PythonCompile.py PATHS ${CMAKE_MODULE_PATH})

  # Byte compile and install the .pyc file.
  get_filename_component(_absfilename "${SOURCE_FILE}" ABSOLUTE)
  get_filename_component(_filename "${_absfilename}" NAME)
  get_filename_component(_filenamebase "${_absfilename}" NAME_WE)
  get_filename_component(_basepath "${_absfilename}" PATH)
  get_filename_component(_pro_bin_abs "${PROJECT_BINARY_DIR}" ABSOLUTE)
  get_filename_component(_pro_src_abs "${PROJECT_SOURCE_DIR}" ABSOLUTE)

  string(LENGTH "${_basepath}" __base_path_length)
  string(LENGTH "${_pro_bin_abs}" __bin_length)
  string(LENGTH "${_pro_src_abs}" __src_length)

  if(__base_path_length GREATER __bin_length)
    math(EXPR __tmp_length "${__bin_length} + 1")
    string(SUBSTRING "${_basepath}/" 0 ${__tmp_length} __bin_found)
  endif()
  if(__base_path_length GREATER __src_length)
    math(EXPR __tmp_length "${__src_length} + 1")
    string(SUBSTRING "${_basepath}/" 0 ${__tmp_length} __src_found)
  endif()

  if("${__bin_found}" STREQUAL "${_pro_bin_abs}/")
    math(EXPR __tmp_length "${__base_path_length} - ${__bin_length}")
    string(SUBSTRING "${_basepath}" ${__bin_length} ${__tmp_length}
      __tmp_base_path)
  elseif("${__src_found}" STREQUAL "${_pro_src_abs}/")
    math(EXPR __tmp_length "${__base_path_length} - ${__src_length}")
    string(SUBSTRING "${_basepath}" ${__src_length} ${__tmp_length}
      __tmp_base_path)
  endif()

  set(_basepath "./${__tmp_base_path}")
  # if(WIN32)
  #   string(REGEX REPLACE ".:/" "/" _basepath "${_basepath}")
  # endif()

  get_filename_component(_full_base_path
    "${PROJECT_BINARY_DIR}/${_basepath}" ABSOLUTE)

  get_filename_component(_bin_py "${_full_base_path}/${_filename}" ABSOLUTE)
  file(MAKE_DIRECTORY "${_full_base_path}")
  if(PYTHON_MAGIC_TAG)
    # PEP 3147
    set(_bin_pyc
      "${_full_base_path}/__pycache__/${_filenamebase}.${PYTHON_MAGIC_TAG}.pyc")
    # should be fine, just in case
    file(MAKE_DIRECTORY "${_full_base_path}/__pycache__")
  else()
    # python2
    set(_bin_pyc "${_full_base_path}/${_filenamebase}.pyc")
  endif()

  get_filename_component(_abs_bin_py ${_bin_py} ABSOLUTE)
  # Don't copy the file onto itself.
  if(NOT "${_abs_bin_py}" STREQUAL "${_absfilename}")
    add_custom_command(
      OUTPUT ${_bin_py}
      COMMAND ${CMAKE_COMMAND} -E copy ${_absfilename} ${_bin_py}
      DEPENDS ${_absfilename})
  endif()
  add_custom_command(
    OUTPUT ${_bin_pyc}
    COMMAND ${PYTHON_EXECUTABLE} ${_python_compile_py} ${_bin_py}
    DEPENDS ${_bin_py})
  set(PYTHON_COMPILED_FILE ${_bin_pyc} PARENT_SCOPE)
  set(PYTHON_COMPILE_PY_FILE ${_bin_py} PARENT_SCOPE)
endfunction()

function(PYTHON_COMPILE)
  unset(PYTHON_COMPILED_FILES)
  unset(PYTHON_COMPILE_TARGET_FILES)
  foreach(pyfile ${ARGN})
    _python_compile(${pyfile})
    set(PYTHON_COMPILED_FILES ${PYTHON_COMPILED_FILES} ${PYTHON_COMPILED_FILE})
    set(PYTHON_COMPILE_PY_FILES ${PYTHON_COMPILE_PY_FILES}
      ${PYTHON_COMPILE_PY_FILE})
  endforeach()
  set(PYTHON_COMPILED_FILES ${PYTHON_COMPILED_FILES} PARENT_SCOPE)
  set(PYTHON_COMPILE_PY_FILES ${PYTHON_COMPILE_PY_FILES} PARENT_SCOPE)
endfunction()

function(PYTHON_INSTALL_ALL DEST_DIR)
  python_compile(${ARGN})

  # PLEASE tell me if there is better solutions
  __py_get_unique_target_name(python_compile_target _py_compile_target)

  add_custom_target("${_py_compile_target}" ALL
    DEPENDS ${PYTHON_COMPILED_FILES})
  install(FILES ${PYTHON_COMPILE_PY_FILES} DESTINATION ${DEST_DIR})
  if(PYTHON_MAGIC_TAG)
    # PEP 3147
    set(PYC_DEST_DIR ${DEST_DIR}/__pycache__)
  else()
    # python2
    set(PYC_DEST_DIR ${DEST_DIR})
  endif()
  install(FILES ${PYTHON_COMPILED_FILES} DESTINATION ${PYC_DEST_DIR})
endfunction()

# backward compatibility
function(PYTHON_INSTALL SOURCE_FILE DESINATION_DIR)
  python_install_all(${DESINATION_DIR} ${SOURCE_FILE})
endfunction()

function(PYTHON_INSTALL_AS_MODULE)
  python_install_all(${PYTHON_SITE_PACKAGES_INSTALL_DIR} ${ARGN})
endfunction()

function(PYTHON_INSTALL_MODULE MODULE_NAME)
  python_install_all(${PYTHON_SITE_PACKAGES_INSTALL_DIR}/${MODULE_NAME} ${ARGN})
endfunction()
