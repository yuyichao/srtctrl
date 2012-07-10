include(GObjectIntrospection)

check_all_modules(GWEBKITJS
  GLIB2 REQUIRED glib-2.0
  GOBJECT2 REQUIRED gobject-2.0
  WEBKIT REQUIRED webkitgtk-3.0
  LIBFFI REQUIRED libffi
  )
include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${GWEBKITJS_INCLUDE_DIRS})
link_directories(${GWEBKITJS_LINK_DIRS})
add_definitions(${GWEBKITJS_FLAGS})

if(NOT DEFINED GWEBKITJS_HEADER_INSTALL_DIR)
  set(GWEBKITJS_HEADER_INSTALL_DIR "${HEADER_INSTALL_DIR}/gwebkitjs")
endif(NOT DEFINED GWEBKITJS_HEADER_INSTALL_DIR)

set(GWEBKITJS_SOURCES
  gwebkitjs_context.c
  gwebkitjs_closure.c
  gwebkitjs_value.c
  gwebkitjs_base.c
  gwebkitjs_util.c
  gwebkitjs_helper.c
  )

set(GWEBKITJS_HEADERS
  gwebkitjs_context.h
  gwebkitjs_closure.h
  gwebkitjs_value.h
  gwebkitjs_base.h
  gwebkitjs_util.h
  gwebkitjs_helper.h
  )

add_library(gwebkitjs SHARED ${GWEBKITJS_SOURCES})
target_link_libraries(gwebkitjs ${GWEBKITJS_LINK})
install(TARGETS gwebkitjs LIBRARY DESTINATION ${LIB_INSTALL_DIR})

gobject_introspection(
    FILENAME GWebKitJS-0.1.gir
    NSVERSION 0.1
    INCLUDE GObject-2.0 GLib-2.0 WebKit-3.0
    PACKAGE_EXPORT gwebkitjs
    LIBRARY gwebkitjs
    SCANNER_ARGS --warn-all --add-include-path=${CMAKE_CURRENT_SOURCE_DIR}
    COMPILER_ARGS "--includedir=${CMAKE_CURRENT_SOURCE_DIR}"
    SYMBOL_PREFIXES gwebkitjs
    SOURCES ${GWEBKITJS_SOURCES} ${GWEBKITJS_HEADERS}
    QUIET
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/GWebKitJS-0.1.gir
  DESTINATION ${GOBJECT_INTROSPECTION_GIRDIR})
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/GWebKitJS-0.1.typelib
  DESTINATION ${GOBJECT_INTROSPECTION_TYPELIBDIR})
install(FILES ${GWEBKITJS_HEADERS}
  DESTINATION ${GWEBKITJS_HEADER_INSTALL_DIR})

if(ENABLE_TEST)
  add_subdirectory(test)
endif()
