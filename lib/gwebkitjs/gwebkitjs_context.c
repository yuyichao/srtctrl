#include <gwebkitjs_context.h>
#include <gwebkitjs_value.h>
#include <JavaScriptCore/JSValueRef.h>
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

struct _GWebKitJSContextPrivate {
    JSGlobalContextRef ctx;
};

static void gwebkitjs_context_init(GWebKitJSContext *self,
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
}

static void
gwebkitjs_context_class_init(GWebKitJSContextClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSContextPrivate));
    /* gobject_class->set_property = gwebkitjs_context_set_property; */
    /* gobject_class->get_property = gwebkitjs_context_get_property; */
    gobject_class->dispose = gwebkitjs_context_dispose;
    gobject_class->finalize = gwebkitjs_context_finalize;
}

static void
gwebkitjs_context_dispose(GObject *obj)
{
    GWebKitJSContext *self = GWEBKITJS_CONTEXT(obj);
    if (self->priv->ctx)
        JSGlobalContextRelease(self->priv->ctx);
    self->priv->ctx = NULL;
}

static void
gwebkitjs_context_finalize(GObject *obj)
{
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
    GWebKitJSContextPrivate *priv;
    self = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    if (!self)
        return NULL;
    priv = self->priv;
    priv->ctx = ctx;
    if (priv->ctx)
        JSGlobalContextRetain(priv->ctx);
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
    WebKitWebFrame *webframe;
    webframe = webkit_web_view_get_main_frame(webview);
    return gwebkitjs_context_new_from_frame(webframe);
}

/**
 * gwebkitjs_context_get_context: (skip)
 * @self: A #GWebKitJSContext.
 *
 * Get the JSGlobalContextRef wrapped by #GWebKitJSContext.
 *
 * Return value: the JSGlobalContextRef wrapped by #GWebKitJSContext.
 **/
JSGlobalContextRef
gwebkitjs_context_get_context(GWebKitJSContext *self)
{
    return self->priv->ctx;
}

/**
 * gwebkitjs_context_make_bool:
 * @self: A #GWebKitJSContext.
 * @b: the boolean value of the created jsvalue.
 *
 * Create a #GWebKitJSValue from a boolean value.
 *
 * Return value: (transfer full): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_bool(GWebKitJSContext *self, gboolean b)
{
    JSValueRef jsvalue;
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    g_return_val_if_fail(self->priv->ctx, NULL);
    jsvalue = JSValueMakeBoolean(self->priv->ctx, b);
    return gwebkitjs_value_new(self, jsvalue);
}

/**
 * gwebkitjs_context_make_from_json_str:
 * @self: A #GWebKitJSContext.
 * @json: the JSON string to create the object from.
 *
 * Create a #GWebKitJSValue from a JSON string.
 *
 * Return value: (transfer full): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_from_json_str(GWebKitJSContext *self,
                                     const gchar *json)
{
    return NULL;
}

/**
 * gwebkitjs_context_make_null:
 * @self: A #GWebKitJSContext.
 *
 * Create a null #GWebKitJSValue.
 *
 * Return value: (transfer full): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_null(GWebKitJSContext *self)
{
    JSValueRef jsvalue;
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    g_return_val_if_fail(self->priv->ctx, NULL);
    jsvalue = JSValueMakeNull(self->priv->ctx);
    return gwebkitjs_value_new(self, jsvalue);
}

/**
 * gwebkitjs_context_make_number:
 * @self: A #GWebKitJSContext.
 * @num: the value(number) of the created jsvalue.
 *
 * Create a #GWebKitJSValue from a number.
 *
 * Return value: (transfer full): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_number(GWebKitJSContext *self, gdouble num)
{
    JSValueRef jsvalue;
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    g_return_val_if_fail(self->priv->ctx, NULL);
    jsvalue = JSValueMakeNumber(self->priv->ctx, num);
    return gwebkitjs_value_new(self, jsvalue);
}

/**
 * gwebkitjs_context_make_string:
 * @self: A #GWebKitJSContext.
 * @str: the string to create the object from.
 *
 * Create a #GWebKitJSValue from a string.
 *
 * Return value: (transfer full): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_string(GWebKitJSContext *self, const gchar *str)
{
    return NULL;
}

/**
 * gwebkitjs_context_make_undefined:
 * @self: A #GWebKitJSContext.
 *
 * Create a undefined #GWebKitJSValue.
 *
 * Return value: (transfer full): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_undefined(GWebKitJSContext *self)
{
    JSValueRef jsvalue;
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    g_return_val_if_fail(self->priv->ctx, NULL);
    jsvalue = JSValueMakeUndefined(self->priv->ctx);
    return gwebkitjs_value_new(self, jsvalue);
}
