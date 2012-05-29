check_all_modules(GWEBKITJS
  GLIB2 REQUIRED glib-2.0
  GOBJECT2 REQUIRED gobject-2.0
  WEBKIT REQUIRED webkitgtk-3.0
  )
include_directories(${CURRENT_SOURCE_DIR}
  ${GWEBKITJS_INCLUDE_DIRS})
link_directories(${GWEBKITJS_LINK_DIRS})
add_definitions(${GWEBKITJS_FLAGS})

set(GWEBKITJS_SOURCE
  gwebkitjs_context.c
  gwebkitjs_base.c
  )

set(GWEBKITJS_HEADER
  gwebkitjs_context.h
  gwebkitjs_base.h
  )

add_library(gwebkitjs SHARED ${GWEBKITJS_SOURCE})
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
    SOURCES ${GWEBKITJS_SOURCE} ${GWEBKITJS_HEADER}
    QUIET
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/GWebKitJS-0.1.gir
  DESTINATION ${GOBJECT_INTROSPECTION_GIRDIR})
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/GWebKitJS-0.1.typelib
  DESTINATION ${GOBJECT_INTROSPECTION_TYPELIBDIR})
