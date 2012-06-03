#include <gwebkitjs_context.h>
#include <gwebkitjs_value.h>
#include <JavaScriptCore/JSValueRef.h>
#include <JavaScriptCore/JSStringRef.h>

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
    JSGlobalContextRef jsctx;
};


/**
 * Context Table Related Stuff.
 **/


/**
 * A hash table that saves the mapping between JSGlobalContextRef
 * and GWebKitJSContext. Used to find the right GWebKitJSContext
 * from a JSCore callback.
 **/
static GHashTable *context_table = NULL;
G_LOCK_DEFINE_STATIC(context_table);

/**
 * _gwebkit_context_init_table:
 *
 * Initialize the context table if it has not been initialized already.
 **/
static void
_gwebkitjs_context_init_table()
{
    if (G_UNLIKELY(!context_table)) {
        context_table = g_hash_table_new(g_direct_hash, g_direct_equal);
    }
}

/**
 * _gwebkitjs_context_remove_from_table:
 * @key: A JSGlobalContextRef (key of context_table).
 * @value: A #GWebKitJSContext (value of context_table).
 *
 * Remove the key-value pair from the context_table, do nothing if the
 * current value of key is not the same with the given value.
 **/
static void
_gwebkitjs_context_remove_from_table(gpointer key, gpointer value)
{
    gpointer orig;
    G_LOCK(context_table);
    orig = g_hash_table_lookup(context_table, key);
    if (G_LIKELY(orig == value))
        g_hash_table_remove(context_table, key);
    G_UNLOCK(context_table);
}

/**
 * _gwebkitjs_context_update_table:
 * @gctx: A new created #GWebKitJSContext. (cannot be NULL)
 *
 * Look up the corresponding JSGlobalContextRef of the #GWebKitJSContext.
 * If found, add the reference counting of the found #GWebKitJSContext
 * and unref() the new one. Otherwise, add the new one to context_table.
 *
 * Return Value: the correct #GWebKitJSContext correspond to
 * the JSGlobalContextRef.
 **/
static GWebKitJSContext*
_gwebkitjs_context_update_table(GWebKitJSContext* gctx)
{
    gpointer orig;
    JSGlobalContextRef jsctx;
    jsctx = gctx->priv->jsctx;
update_start:
    G_LOCK(context_table);
    orig = g_hash_table_lookup(context_table, jsctx);
    if (!orig) {
        g_hash_table_replace(context_table, jsctx, gctx);
    }
    G_UNLOCK(context_table);
    if (orig) {
        orig = g_object_ref(orig);
        /* If disposing has already started but the object hasn't been removed
         * from context_table.
         */
        if (G_UNLIKELY(!orig)) {
            _gwebkitjs_context_remove_from_table(jsctx, orig);
            goto update_start;
        }
        g_object_unref(gctx);
        return orig;
    }
    return gctx;
}

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
    _gwebkitjs_context_init_table();
    if (G_UNLIKELY(!context_type)) {
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
    priv->jsctx = NULL;
}

static void
gwebkitjs_context_class_init(GWebKitJSContextClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSContextPrivate));
    gobject_class->dispose = gwebkitjs_context_dispose;
    gobject_class->finalize = gwebkitjs_context_finalize;
}

static void
gwebkitjs_context_dispose(GObject *obj)
{
    GWebKitJSContext *self = GWEBKITJS_CONTEXT(obj);
    if (self->priv->jsctx) {
        _gwebkitjs_context_remove_from_table(self->priv->jsctx, self);
        JSGlobalContextRelease(self->priv->jsctx);
        self->priv->jsctx = NULL;
    }
}

static void
gwebkitjs_context_finalize(GObject *obj)
{
}

/**
 * gwebkitjs_context_new: (skip)
 * @jsctx: The Javascript Context wrapped by GWebKitJSContext.
 *
 * Find the corresponding #GWebKitJSContext of a JSGlobalContextRef.
 * Creates a new one if not exist.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new(JSGlobalContextRef jsctx)
{
    GWebKitJSContext *self;
    g_return_val_if_fail(jsctx, NULL);

    self = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    g_return_val_if_fail(self, NULL);

    self->priv->jsctx = jsctx;
    JSGlobalContextRetain(jsctx);
    return _gwebkitjs_context_update_table(self);
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
    JSGlobalContextRef jsctx;
    jsctx = webkit_web_frame_get_global_context(webframe);
    return gwebkitjs_context_new(jsctx);
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
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    return self->priv->jsctx;
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
    g_return_val_if_fail(self->priv->jsctx, NULL);

    jsvalue = JSValueMakeBoolean(self->priv->jsctx, b);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
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
    JSValueRef jsvalue;
    JSStringRef jsstr;
    g_return_val_if_fail(json, NULL);
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    g_return_val_if_fail(self->priv->jsctx, NULL);

    jsstr = JSStringCreateWithUTF8CString(json);
    jsvalue = JSValueMakeFromJSONString(self->priv->jsctx, jsstr);
    JSStringRelease(jsstr);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
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
    g_return_val_if_fail(self->priv->jsctx, NULL);

    jsvalue = JSValueMakeNull(self->priv->jsctx);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
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
    g_return_val_if_fail(self->priv->jsctx, NULL);

    jsvalue = JSValueMakeNumber(self->priv->jsctx, num);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
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
    JSValueRef jsvalue;
    JSStringRef jsstr;
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(self), NULL);
    g_return_val_if_fail(self->priv->jsctx, NULL);

    jsstr = JSStringCreateWithUTF8CString(str);
    jsvalue = JSValueMakeString(self->priv->jsctx, jsstr);
    JSStringRelease(jsstr);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
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
    g_return_val_if_fail(self->priv->jsctx, NULL);
    jsvalue = JSValueMakeUndefined(self->priv->jsctx);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_get_value_type:
 * @self: The #GWebKitJSContext related to the value..
 * @value: A #GWebKitJSValue
 *
 * Check the type of a value.
 *
 * Return value: the type of the value.
 **/
GWebKitJSValueType
gwebkitjs_context_get_value_type(GWebKitJSContext *self, GWebKitJSValue *value)
{
    return gwebkitjs_value_get_value_type(value, self);
}

/**
 * gwebkitjs_context_is_bool:
 * @self: The #GWebKitJSContext related to the value.
 * @value: A #GWebKitJSValue.
 *
 * Check if the type of a value is boolean.
 *
 * Return value: whether the type of the value is boolean.
 **/
gboolean
gwebkitjs_context_is_bool(GWebKitJSContext *self,
                          GWebKitJSValue *value)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    g_return_val_if_fail((jsctx = gwebkitjs_context_get_context(self)), FALSE);
    g_return_val_if_fail((jsvalue = gwebkitjs_value_get_value(value)), FALSE);
    return JSValueIsBoolean(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_null:
 * @self: The #GWebKitJSContext related to the value.
 * @value: A #GWebKitJSValue.
 *
 * Check if the type of a value is null.
 *
 * Return value: whether the type of the value is null.
 **/
gboolean
gwebkitjs_context_is_null(GWebKitJSContext *self,
                          GWebKitJSValue *value)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    g_return_val_if_fail((jsctx = gwebkitjs_context_get_context(self)), FALSE);
    g_return_val_if_fail((jsvalue = gwebkitjs_value_get_value(value)), FALSE);
    return JSValueIsNull(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_number:
 * @self: The #GWebKitJSContext related to the value.
 * @value: A #GWebKitJSValue.
 *
 * Check if the type of a value is number.
 *
 * Return value: whether the type of the value is number.
 **/
gboolean
gwebkitjs_context_is_number(GWebKitJSContext *self,
                            GWebKitJSValue *value)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    g_return_val_if_fail((jsctx = gwebkitjs_context_get_context(self)), FALSE);
    g_return_val_if_fail((jsvalue = gwebkitjs_value_get_value(value)), FALSE);
    return JSValueIsNumber(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_string:
 * @self: The #GWebKitJSContext related to the value.
 * @value: A #GWebKitJSValue.
 *
 * Check if the type of a value is string.
 *
 * Return value: whether the type of the value is string.
 **/
gboolean
gwebkitjs_context_is_string(GWebKitJSContext *self,
                            GWebKitJSValue *value)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    g_return_val_if_fail((jsctx = gwebkitjs_context_get_context(self)), FALSE);
    g_return_val_if_fail((jsvalue = gwebkitjs_value_get_value(value)), FALSE);
    return JSValueIsString(jsctx, jsvalue);
}


/**
 * gwebkitjs_context_is_object:
 * @self: The #GWebKitJSContext related to the value.
 * @value: A #GWebKitJSValue.
 *
 * Check if the type of a value is object.
 *
 * Return value: whether the type of the value is object.
 **/
gboolean
gwebkitjs_context_is_object(GWebKitJSContext *self,
                            GWebKitJSValue *value)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    g_return_val_if_fail((jsctx = gwebkitjs_context_get_context(self)), FALSE);
    g_return_val_if_fail((jsvalue = gwebkitjs_value_get_value(value)), FALSE);
    return JSValueIsObject(jsctx, jsvalue);
}


/**
 * gwebkitjs_context_is_undefined:
 * @self: The #GWebKitJSContext related to the value.
 * @value: A #GWebKitJSValue.
 *
 * Check if the type of a value is undefined.
 *
 * Return value: whether the type of the value is undefined.
 **/
gboolean gwebkitjs_context_is_undefined(GWebKitJSContext *self,
                                        GWebKitJSValue *value)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    g_return_val_if_fail((jsctx = gwebkitjs_context_get_context(self)), FALSE);
    g_return_val_if_fail((jsvalue = gwebkitjs_value_get_value(value)), FALSE);
    return JSValueIsUndefined(jsctx, jsvalue);
}
