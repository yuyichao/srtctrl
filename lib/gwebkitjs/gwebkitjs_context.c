#include "gwebkitjs_context.h"

/***************************************************************************
 *   Copyright (C) 2012~2012 by Yichao Yu                                  *
 *   yyc1992@gmail.com                                                     *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation, either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
 ***************************************************************************/

enum {
  PROP_0,
  PROP_CONTEXT
};

struct _GWebKitJSContextPrivate {
    JSGlobalContextRef ctx;
    WebKitWebView *webview;
    gulong webview_id;
};

static void gwebkitjs_context_init(GWebKitJSContext *self,
                                   GWebKitJSContextClass *klass);

static void gwebkitjs_context_class_init(GWebKitJSContextClass *klass,
                                         gpointer data);
static void gwebkitjs_context_dispose(GObject *obj);
static void gwebkitjs_context_finalize(GObject *obj);
static void gwebkitjs_context_set_property(GObject *obj, guint prop_id,
                                           const GValue *value,
                                           GParamSpec *pspec);
static void gwebkitjs_context_get_property(GObject *obj, guint prop_id,
                                           GValue *value,
                                           GParamSpec *pspec);

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

        context_type = g_type_register_static(G_TYPE_OBJECT,
                                              "GWebKitJSContext",
                                              &context_info, 0);
    }
    return context_type;
}

static void
gwebkitjs_context_init(GWebKitJSContext *self, GWebKitJSContextClass *klass)
{
    GWebKitJSContextPrivate *priv;
    priv = self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                                    GWEBKITJS_TYPE_CONTEXT,
                                                    GWebKitJSContextPrivate);
    priv->ctx = NULL;
    priv->webview = NULL;
    priv->webview_id = 0;
}

static void
gwebkitjs_context_class_init(GWebKitJSContextClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSContextPrivate));
    gobject_class->set_property = gwebkitjs_context_set_property;
    gobject_class->get_property = gwebkitjs_context_get_property;
    gobject_class->dispose = gwebkitjs_context_dispose;
    gobject_class->finalize = gwebkitjs_context_finalize;
    g_object_class_install_property(
        gobject_class, PROP_CONTEXT,
        g_param_spec_pointer("context",
                             "Context",
                             "The JSGlobalContext wrapped by the object",
                             G_PARAM_READWRITE));
}

static void
gwebkitjs_context_dispose(GObject *obj)
{
    GWebKitJSContext *self = GWEBKITJS_CONTEXT(obj);
    gwebkitjs_context_set_context(self, NULL);
}

static void
gwebkitjs_context_finalize(GObject *obj)
{
}

static void
gwebkitjs_context_set_property(GObject *obj, guint prop_id,
                               const GValue *value, GParamSpec *pspec)
{
    GWebKitJSContext *self = GWEBKITJS_CONTEXT(obj);

    switch (prop_id) {
    case PROP_CONTEXT:
        gwebkitjs_context_set_context(self, g_value_get_pointer(value));
        break;
    default:
        G_OBJECT_WARN_INVALID_PROPERTY_ID(obj, prop_id, pspec);
        break;
    }
}

static void
gwebkitjs_context_get_property(GObject *obj, guint prop_id,
                               GValue *value, GParamSpec *pspec)
{
    GWebKitJSContext *self = GWEBKITJS_CONTEXT(obj);
    GWebKitJSContextPrivate *priv = self->priv;

    switch (prop_id) {
    case PROP_CONTEXT:
        g_value_set_pointer(value, priv->ctx);
        break;
    default:
        G_OBJECT_WARN_INVALID_PROPERTY_ID(obj, prop_id, pspec);
        break;
    }
}

/**
 * gwebkitjs_context_new: (skip)
 * @ctx: The Javascript Context wrapped by GWebKitJSContext.
 *
 * Creates a new wrapper of a javascript context.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new(JSGlobalContextRef ctx)
{
    GWebKitJSContext *self;
    self = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    gwebkitjs_context_set_context(self, ctx);
    return self;
}

/**
 * gwebkitjs_context_new_from_frame:
 * @webframe: The WebKit WebFrame to get the context from.
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
 * @webview: The WebKit WebView to get the context from.
 *
 * Creates a new javascript context wrapper from a webkit webview.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new_from_view(WebKitWebView *webview)
{
    GWebKitJSContext *self;
    self = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    gwebkitjs_context_set_view(self, webview);
    return self;
}

static void
_gwebkitjs_context_set_context(GWebKitJSContext *self, JSGlobalContextRef ctx)
{
    GWebKitJSContextPrivate *priv;
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(self));
    priv = self->priv;

    if (priv->ctx)
        JSGlobalContextRelease(priv->ctx);
    priv->ctx = ctx;
    if (priv->ctx)
        JSGlobalContextRetain(priv->ctx);
    g_object_notify(G_OBJECT(self), "context");
}

/**
 * gwebkitjs_context_set_context: (skip)
 * @self: A #GWebKitJSContext.
 * @ctx: The Javascript Context wrapped by #GWebKitJSContext.
 *
 * Set the Javascript Context of a #GWebKitJSContext. This function will
 * automatically disconnect self from #WebKitWebView if any.
 **/
void
gwebkitjs_context_set_context(GWebKitJSContext *self, JSGlobalContextRef ctx)
{
    GWebKitJSContextPrivate *priv;
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(self));
    priv = self->priv;

    if (priv->webview) {
        if (priv->webview_id) {
            g_signal_handler_disconnect(priv->webview, priv->webview_id);
            priv->webview_id = 0;
        }
        g_object_unref(priv->webview);
        priv->webview = NULL;
    }
    _gwebkitjs_context_set_context(self, ctx);
}

/**
 * gwebkitjs_context_set_frame:
 * @self: A #GWebKitJSContext.
 * @webframe: The WebKit WebFrame to get the context from.
 *
 * Set the Javascript Context of a #GWebKitJSContext from a #WebKitWebFrame.
 * This function will automatically disconnect self from #WebKitWebView if any.
 **/
void
gwebkitjs_context_set_frame(GWebKitJSContext *self, WebKitWebFrame *webframe)
{
    JSGlobalContextRef ctx;
    ctx = webkit_web_frame_get_global_context(webframe);
    gwebkitjs_context_set_context(self, ctx);
}

static void
gwebkitjs_context_webview_clear_cb(WebKitWebView *web_view,
                                   WebKitWebFrame *frame,
                                   JSGlobalContextRef ctx,
                                   JSObjectRef win_obj,
                                   GWebKitJSContext *self)
{
    GWebKitJSContextPrivate *priv;
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(self));
    priv = self->priv;
    if (web_view != priv->webview) {
        g_warn_if_reached();
        return;
    }
    _gwebkitjs_context_set_context(self, ctx);
}

/**
 * gwebkitjs_context_set_view:
 * @self: A #GWebKitJSContext.
 * @webview: The #WebKitWebView to bind to.
 *
 * Bind the #GWebKitJSContext to the javascript context of a #WebKitWebView.
 **/
void
gwebkitjs_context_set_view(GWebKitJSContext *self, WebKitWebView *webview)
{
    WebKitWebFrame *webframe;
    GWebKitJSContextPrivate *priv;
    g_return_if_fail(GWEBKITJS_IS_CONTEXT_CLASS(self));
    priv = self->priv;
    webframe = webkit_web_view_get_main_frame(webview);

    /* Also clear any binded webview. */
    g_object_freeze_notify(G_OBJECT(self));
    gwebkitjs_context_set_frame(self, webframe);

    g_object_ref(G_OBJECT(webview));
    priv->webview = webview;
    priv->webview_id =
        g_signal_connect(webview, "window-object-cleared",
                         G_CALLBACK(gwebkitjs_context_webview_clear_cb), self);
    g_object_thaw_notify(G_OBJECT(self));
}
