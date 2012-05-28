#ifndef __GWEBKITJS_CONTEXT_H__
#define __GWEBKITJS_CONTEXT_H__
#include <glib-object.h>
#include <JavaScriptCore/JSContextRef.h>
#include <webkit/webkitwebview.h>

#define GWEBKITJS_TYPE_CONTEXT (gwebkitjs_context_get_type())
#define GWEBKITJS_CONTEXT(obj)                                          \
    (G_TYPE_CHECK_INSTANCE_CAST((obj), GWEBKITJS_TYPE_CONTEXT, GWebKitJSContext))
#define GWEBKITJS_IS_CONTEXT(obj)                                       \
    (G_TYPE_CHECK_INSTANCE_TYPE((obj), GWEBKITJS_TYPE_CONTEXT))
#define GWEBKITJS_CONTEXT_CLASS(klass)                                  \
    (G_TYPE_CHECK_CLASS_CAST((klass), GWEBKITJS_TYPE_CONTEXT,           \
                             GWebKitJSContextClass))
#define GWEBKITJS_IS_CONTEXT_CLASS(klass)                       \
    (G_TYPE_CHECK_CLASS_TYPE((klass), GWEBKITJS_TYPE_CONTEXT))
#define GWEBKITJS_CONTEXT_GET_CLASS(obj)                                \
    (G_TYPE_INSTANCE_GET_CLASS((obj), GWEBKITJS_TYPE_CONTEXT,           \
                               GWebKitJSContextClass))

typedef struct _GWebKitJSContext GWebKitJSContext;
typedef struct _GWebKitJSContextClass GWebKitJSContextClass;

struct _GWebKitJSContext {
    GObject parent;
    JSGlobalContextRef ctx;
    WebKitWebView *webview;
    gulong webview_id;
};

struct _GWebKitJSContextClass {
    GObjectClass parent_class;
};

#ifdef __cplusplus
extern "C" {
#endif
    GType gwebkitjs_context_get_type();
    GWebKitJSContext *gwebkitjs_context_new(JSGlobalContextRef ctx);
    GWebKitJSContext *gwebkitjs_context_new_from_frame(
        WebKitWebFrame *webframe);
    GWebKitJSContext *gwebkitjs_context_new_from_view(WebKitWebView *webview);
    void gwebkitjs_context_set_context(GWebKitJSContext *gctx,
                                       JSGlobalContextRef ctx);
    void gwebkitjs_context_set_frame(GWebKitJSContext *gctx,
                                     WebKitWebFrame *webframe);
    void gwebkitjs_context_set_view(GWebKitJSContext *gctx,
                                    WebKitWebView *webview);
#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_CONTEXT_H__ */
