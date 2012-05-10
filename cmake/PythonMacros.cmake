# Python macros
# ~~~~~~~~~~~~~
# Copyright 2012 Yu Yichao
# yyc1992@gmail.com
#
# This file is part of SrtCtrl.
#
# SrtCtrl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SrtCtrl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SrtCtrl.  If not, see <http://www.gnu.org/licenses/>.

# This file incorporates work covered by the following copyright and
# permission notice:
#
#     Copyright (c) 2007, Simon Edwards <simon@simonzone.com>
#
#     Redistribution and use is allowed according to the terms of the BSD
#     license. For details see the accompanying COPYING-CMAKE-SCRIPTS file.
#
# This file defines the following macros:
#
# python_compile(LIST_OF_SOURCE_FILES)
#     Byte compile the py force files listed in the LIST_OF_SOURCE_FILES.
#     Compiled pyc files are stored in PYTHON_COMPILED_FILES, corresponding py
#     files are stored in PYTHON_COMPILE_PY_FILES
#
# python_install(DESINATION_DIR LIST_OF_SOURCE_FILES)
#     Install the LIST_OF_SOURCE_FILES, which is a list of Python .py file,
#     into the destination directory during install. The file will be byte
#     compiled and both the .py file and .pyc file will be installed.
#
# python_install_module(MODULE_NAME LIST_OF_SOURCE_FILES)
#     Similiar to python_install(), but the files are automatically installed
#     to the site-package directory of python.

get_filename_component(PYTHON_MACROS_MODULE_PATH
  ${CMAKE_CURRENT_LIST_FILE} PATH)

find_package(PythonLibrary REQUIRED)

macro(_python_compile SOURCE_FILE)
  find_file(_python_compile_py PythonCompile.py PATHS ${CMAKE_MODULE_PATH})

  # Byte compile and install the .pyc file.
  get_filename_component(_absfilename ${SOURCE_FILE} ABSOLUTE)
  get_filename_component(_filename ${SOURCE_FILE} NAME)
  get_filename_component(_filenamebase ${SOURCE_FILE} NAME_WE)
  get_filename_component(_basepath ${SOURCE_FILE} PATH)

  if(WIN32)
    string(REGEX REPLACE ".:/" "/" _basepath "${_basepath}")
  endif(WIN32)

  set(_bin_py ${CMAKE_CURRENT_BINARY_DIR}/${_basepath}/${_filename})
  file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${_basepath})
  if(PYTHON_MAGIC_TAG)
    # PEP 3147
    set(_bin_pyc ${CMAKE_CURRENT_BINARY_DIR}/${_basepath}/__pycache__/${_filenamebase}.${PYTHON_MAGIC_TAG}.pyc)
    # show be fine, just in case
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${_basepath}/__pycache__)
  else(PYTHON_MAGIC_TAG)
    # python2
    set(_bin_pyc ${CMAKE_CURRENT_BINARY_DIR}/${_basepath}/${_filenamebase}.pyc)
  endif(PYTHON_MAGIC_TAG)

  set(_message "Byte-compiling ${_bin_py}")

  get_filename_component(_abs_bin_py ${_bin_py} ABSOLUTE)
  # Don't copy the file onto itself.
  if(NOT _abs_bin_py STREQUAL ${_absfilename})
    add_custom_command(
      OUTPUT ${_bin_py}
      COMMAND ${CMAKE_COMMAND} -E echo "Copying ${_absfilename} to ${_bin_py}"
      COMMAND ${CMAKE_COMMAND} -E copy ${_absfilename} ${_bin_py}
      DEPENDS ${_absfilename}
    )
  endif(NOT _abs_bin_py STREQUAL ${_absfilename})
  add_custom_command(
    OUTPUT ${_bin_pyc}
    COMMAND ${CMAKE_COMMAND} -E echo ${_message}
    COMMAND ${PYTHON_EXECUTABLE} ${_python_compile_py} ${_bin_py}
    DEPENDS ${_bin_py}
    )
  set(PYTHON_COMPILED_FILE ${_bin_pyc})
  set(PYTHON_COMPILE_PY_FILE ${_bin_py})
endmacro(_python_compile)

macro(python_compile)
  unset(PYTHON_COMPILED_FILES)
  unset(PYTHON_COMPILE_TARGET_FILES)
  foreach(pyfile ${ARGN})
    _python_compile(${pyfile})
    set(PYTHON_COMPILED_FILES ${PYTHON_COMPILED_FILES} ${PYTHON_COMPILED_FILE})
    set(PYTHON_COMPILE_PY_FILES ${PYTHON_COMPILE_PY_FILES}
      ${PYTHON_COMPILE_PY_FILE})
  endforeach(pyfile ${ARGN})
endmacro(python_compile)

macro(python_install DEST_DIR)
  python_compile(${ARGN})
  set(_PYTHON_COMPILE_DEFAULT_TARGETS ${_PYTHON_COMPILE_DEFAULT_TARGETS}
    ${PYTHON_COMPILED_FILES})
  add_custom_target(compile_pyc_target ALL
    DEPENDS ${_PYTHON_COMPILE_DEFAULT_TARGETS})
  install(FILES ${PYTHON_COMPILE_PY_FILES} DESTINATION ${DEST_DIR})
  if(PYTHON_MAGIC_TAG)
    # PEP 3147
    set(PYC_DEST_DIR ${DEST_DIR}/__pycache__)
  else(PYTHON_MAGIC_TAG)
    # python2
    set(PYC_DEST_DIR ${DEST_DIR})
  endif(PYTHON_MAGIC_TAG)
  install(FILES ${PYTHON_COMPILED_FILES} DESTINATION ${PYC_DEST_DIR})
endmacro(python_install DEST_DIR)

macro(python_install_module MODULE_NAME)
  python_install(${PYTHON_SITE_PACKAGES_INSTALL_DIR}/${MODULE_NAME} ${ARGN})
endmacro(python_install_module MODULE_NAME)
