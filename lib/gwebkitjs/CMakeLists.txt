include(CheckAll)
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
  gwebkitjs_context.c)

add_library(gwebkitjs SHARED ${GWEBKITJS_SOURCE})
target_link_libraries(gwebkitjs ${GWEBKITJS_LINK})
install(TARGETS gwebkitjs LIBRARY DESTINATION ${LIB_INSTALL_DIR})
