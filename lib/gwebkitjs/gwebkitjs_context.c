#include "gwebkitjs_context.h"

static void gwebkitjs_context_init(GWebKitJSContext *ctx,
                                   GWebKitJSContextClass *klass);

static void gwebkitjs_context_class_init(GWebKitJSContextClass *klass,
                                         gpointer data);
static void gwebkitjs_context_dispose(GObject *obj);
static void gwebkitjs_context_finalize(GObject *obj);

GType
gwebkitjs_context_get_type()
{
    static GType context_type = 0;
    if (G_UNLIKELY(context_type == 0)) {
      const GTypeInfo context_info = {
          .class_size = sizeof(GWebKitJSContextClass),
          .base_init = NULL,
          .base_finalize = NULL,
          .class_init = (GClassInitFunc)gwebkitjs_context_class_init,
          .class_finalize = NULL,
          .class_data = NULL,
          .instance_size = sizeof(GWebKitJSContext),
          .n_preallocs = 0,
          .instance_init = (GInstanceInitFunc)gwebkitjs_context_init,
          .value_table = NULL,
      };

      context_type = g_type_register_static(GWEBKITJS_TYPE_CONTEXT,
                                            "GwebkitJSContext",
                                            &context_info, 0);
    }
    return context_type;
}

static void
gwebkitjs_context_init(GWebKitJSContext *gctx, GWebKitJSContextClass *klass)
{
    gctx->ctx = NULL;
    gctx->webview = NULL;
    gctx->webview_id = 0;
}

static void
gwebkitjs_context_class_init(GWebKitJSContextClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    gobject_class->dispose = gwebkitjs_context_dispose;
    gobject_class->finalize = gwebkitjs_context_finalize;
}

static void
gwebkitjs_context_dispose(GObject *obj)
{
    GWebKitJSContext *gctx = GWEBKITJS_CONTEXT(obj);
    gwebkitjs_context_set_context(gctx, NULL);
}

static void
gwebkitjs_context_finalize(GObject *obj)
{
}

/**
 * gwebkitjs_context_new:
 * @ctx: The Javascript Context wrapped by GWebKitJSContext.
 *
 * Creates a new wrapper of a javascript context.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new(JSGlobalContextRef ctx)
{
    GWebKitJSContext *gctx;
    gctx = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    gwebkitjs_context_set_context(gctx, ctx);
    return gctx;
}

/**
 * gwebkitjs_context_new_from_frame:
 * @frame: The WebKit WebFrame to get the context from.
 *
 * Creates a new javascript context wrapper from a webkit wevframe.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new_from_frame(WebKitWebFrame *webframe)
{
    JSGlobalContextRef ctx;
    ctx = webkit_web_frame_get_global_context(webframe);
    return gwebkitjs_context_new(ctx);
}

/**
 * gwebkitjs_context_new_from_view:
 * @view: The WebKit WebView to get the context from.
 *
 * Creates a new javascript context wrapper from a webkit webview.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new_from_view(WebKitWebView *webview)
{
    GWebKitJSContext *gctx;
    gctx = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    gwebkitjs_context_set_view(gctx, webview);
    return gctx;
}

static void
_gwebkitjs_context_set_context(GWebKitJSContext *gctx, JSGlobalContextRef ctx)
{
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(gctx));

    if (gctx->ctx)
        JSGlobalContextRelease(gctx->ctx);
    gctx->ctx = ctx;
    if (gctx->ctx)
        JSGlobalContextRetain(gctx->ctx);
    /* TODO: g_object_notify(); */
}

/**
 * gwebkitjs_context_set_context:
 * @gctx: A #GWebKitJSContext.
 * @ctx: The Javascript Context wrapped by #GWebKitJSContext.
 *
 * Set the Javascript Context of a #GWebKitJSContext. This function will
 * automatically disconnect gctx from #WebKitWebView if any.
 **/
void
gwebkitjs_context_set_context(GWebKitJSContext *gctx, JSGlobalContextRef ctx)
{
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(gctx));

    if (gctx->webview) {
        if (gctx->webview_id) {
            g_signal_handler_disconnect(gctx->webview, gctx->webview_id);
            gctx->webview_id = 0;
        }
        g_object_unref(gctx->webview);
        gctx->webview = NULL;
    }
    _gwebkitjs_context_set_context(gctx, ctx);
}

/**
 * gwebkitjs_context_set_frame:
 * @gctx: A #GWebKitJSContext.
 * @frame: The WebKit WebFrame to get the context from.
 *
 * Set the Javascript Context of a #GWebKitJSContext from a #WebKitWebFrame.
 * This function will automatically disconnect gctx from #WebKitWebView if any.
 **/
void
gwebkitjs_context_set_frame(GWebKitJSContext *gctx, WebKitWebFrame *webframe)
{
    JSGlobalContextRef ctx;
    ctx = webkit_web_frame_get_global_context(webframe);
    gwebkitjs_context_set_context(gctx, ctx);
}

static void
gwebkitjs_context_webview_clear_cb(WebKitWebView *web_view,
                                   WebKitWebFrame *frame,
                                   JSGlobalContextRef ctx,
                                   JSObjectRef win_obj,
                                   GWebKitJSContext *gctx)
{
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(gctx));
    if (web_view != gctx->webview) {
        g_warn_if_reached();
        return;
    }
    _gwebkitjs_context_set_context(gctx, ctx);
}

/**
 * gwebkitjs_context_set_view:
 * @gctx: A #GWebKitJSContext.
 * @webview: The #WebKitWebView to bind to.
 *
 * Bind the #GWebKitJSContext to the javascript context of a #WebKitWebView.
 **/
void
gwebkitjs_context_set_view(GWebKitJSContext *gctx, WebKitWebView *webview)
{
    WebKitWebFrame *webframe;
    webframe = webkit_web_view_get_main_frame(webview);

    /* Also clear any binded webview. */
    g_object_freeze_notify(G_OBJECT(gctx));
    gwebkitjs_context_set_frame(gctx, webframe);

    g_object_ref(G_OBJECT(webview));
    gctx->webview = webview;
    gctx->webview_id =
        g_signal_connect(webview, "window-object-cleared",
                         G_CALLBACK(gwebkitjs_context_webview_clear_cb), gctx);
    g_object_thaw_notify(G_OBJECT(gctx));
}
