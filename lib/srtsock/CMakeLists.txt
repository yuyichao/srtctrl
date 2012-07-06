check_all_modules(SRTSOCK
  GLIB2 REQUIRED glib-2.0
  GOBJECT2 REQUIRED gobject-2.0
  GIO2 REQUIRED gio-2.0
  )
include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${SRTSOCK_INCLUDE_DIRS})
link_directories(${SRTSOCK_LINK_DIRS})
add_definitions(${SRTSOCK_FLAGS})

include(AddRun)

if(NOT DEFINED SRTSOCK_HEADER_INSTALL_DIR)
  set(SRTSOCK_HEADER_INSTALL_DIR "${HEADER_INSTALL_DIR}/srtsock")
endif(NOT DEFINED SRTSOCK_HEADER_INSTALL_DIR)

set(SRTSOCK_SOURCES
  srtsock_sock.c
  srtsock_buff.c
  )

set(SRTSOCK_HEADERS
  srtsock_sock.h
  srtsock_buff.h
  )

add_library(srtsock SHARED ${SRTSOCK_SOURCES})
target_link_libraries(srtsock ${SRTSOCK_LINK})
install(TARGETS srtsock LIBRARY DESTINATION ${LIB_INSTALL_DIR})

gobject_introspection(
  FILENAME SrtSock-0.1.gir
  NSVERSION 0.1
  INCLUDE GObject-2.0 GLib-2.0 Gio-2.0
  PACKAGE_EXPORT srtsock
  LIBRARY srtsock
  SCANNER_ARGS --warn-all --add-include-path=${CMAKE_CURRENT_SOURCE_DIR}
  COMPILER_ARGS "--includedir=${CMAKE_CURRENT_SOURCE_DIR}"
  SYMBOL_PREFIXES srtsock
  SOURCES ${SRTSOCK_SOURCES} ${SRTSOCK_HEADERS}
  QUIET
  )

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/SrtSock-0.1.gir
  DESTINATION ${GOBJECT_INTROSPECTION_GIRDIR})
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/SrtSock-0.1.typelib
  DESTINATION ${GOBJECT_INTROSPECTION_TYPELIBDIR})
install(FILES ${SRTSOCK_HEADERS}
  DESTINATION ${SRTSOCK_HEADER_INSTALL_DIR})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
