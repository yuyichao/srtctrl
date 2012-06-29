#include <gwebkitjs_util.h>
#include <gwebkitjs_context.h>
#include <gwebkitjs_value.h>
#include <gwebkitjs_base.h>
#include <JavaScriptCore/JSValueRef.h>
#include <JavaScriptCore/JSStringRef.h>
#include <math.h>

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
    GWebKitJSValue *global;
    GWebKitJSValue *object;
    GWebKitJSValue *tostring;
};

#define GWEBKITJS_CONTEXT_IS_VALID(_ctx)                        \
    ({                                                          \
        GWebKitJSContext *ctx = (_ctx);                         \
        ctx && GWEBKITJS_IS_CONTEXT(ctx) && ctx->priv->jsctx;   \
    })


/**
 * Declarations
 **/
static void gwebkitjs_context_init(GWebKitJSContext *self,
                                   GWebKitJSContextClass *klass);

static void gwebkitjs_context_class_init(GWebKitJSContextClass *klass,
                                         gpointer data);
static void gwebkitjs_context_dispose(GObject *obj);
static void gwebkitjs_context_finalize(GObject *obj);
static JSValueRef *gwebkitjs_context_make_arg_array(JSContextRef jsctx,
                                                    size_t argc,
                                                    GWebKitJSValue **argv);


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
    if (G_LIKELY(orig == value)) {
        g_hash_table_remove(context_table, key);
    }
    G_UNLOCK(context_table);
}

/**
 * _gwebkitjs_context_update_table:
 * @gctx: A new created #GWebKitJSContext. (cannot be NULL)
 *
 * Look up the corresponding JSGlobalContextRef of the #GWebKitJSContext.
 * If found, add the reference counting of the found #GWebKitJSContext.
 * The new one (@gctx) will NOT be unref().
 * Otherwise, add the new one to context_table.
 *
 * Return Value: the correct #GWebKitJSContext correspond to
 * the JSGlobalContextRef.
 **/
static GWebKitJSContext*
_gwebkitjs_context_update_table(GWebKitJSContext* gctx,
                                JSGlobalContextRef jsctx)
{
    gpointer orig;
update_start:
    G_LOCK(context_table);
    orig = g_hash_table_lookup(context_table, jsctx);
    if (!orig && gctx) {
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
        return orig;
    }
    return gctx;
}


/**
 * GObject Functions.
 **/
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
    GWebKitJSContextPrivate *priv = self->priv;
    if (priv->global) {
        g_object_unref(priv->global);
        priv->global = NULL;
    }
    if (priv->object) {
        g_object_unref(priv->object);
        priv->object = NULL;
    }
    if (priv->tostring) {
        g_object_unref(priv->tostring);
        priv->tostring = NULL;
    }
}

static void
gwebkitjs_context_finalize(GObject *obj)
{
    GWebKitJSContext *self = GWEBKITJS_CONTEXT(obj);
    GWebKitJSContextPrivate *priv = self->priv;
    /**
     * Release JSContext here in order to make sure all values of this context
     * has already been notified by weak reference which is done in dispose of
     * gobject after dispose function of GWebKitJSContext is called.
     **/
    if (priv->jsctx) {
        _gwebkitjs_context_remove_from_table(priv->jsctx, self);
        JSGlobalContextRelease(priv->jsctx);
        priv->jsctx = NULL;
    }
}

static gboolean
gwebkitjs_context_initialized(GWebKitJSContext *self)
{
    GWebKitJSContextPrivate *priv;
    gwj_return_val_if_false(GWEBKITJS_IS_CONTEXT(self), FALSE);

    priv = self->priv;
    return (priv->global && priv->object && priv->tostring);
}

static GWebKitJSContext*
gwebkitjs_context_init_context(GWebKitJSContext *self,
                               JSGlobalContextRef jsctx)
{
    GWebKitJSContextPrivate *priv;
    GWebKitJSContext *res;
    JSValueRef jsvalue;
    JSObjectRef global;
    JSObjectRef object;
    JSObjectRef tostring;
    gwj_return_val_if_false(jsctx, NULL);
    if (!GWEBKITJS_IS_CONTEXT(self)) {
        self = NULL;
        goto try_update;
    }
    priv = self->priv;
    priv->global = NULL;
    priv->object = NULL;
    priv->tostring = NULL;

    priv->jsctx = jsctx;
    JSGlobalContextRetain(jsctx);

    global = JSContextGetGlobalObject(jsctx);
    if (!global)
        goto free;

    object = JSObjectMake(jsctx, NULL, NULL);
    if (!object)
        goto free;

    jsvalue = gwebkitjs_util_get_property(jsctx, object, "toString", NULL);
    if (!jsvalue)
        goto free;
    tostring = JSValueToObject(jsctx, jsvalue, NULL);
    if (!tostring)
        goto free;
    if (!JSObjectIsFunction(jsctx, tostring))
        goto free;

try_update:
    res = _gwebkitjs_context_update_table(self, jsctx);

    if (!res) {
        /* This can only happen if self was NULL and no existing instance is
         * found in the table.
         */
        return NULL;
    } else if (res == self) {
        /* No existing instance is found in the table, try initialize the
         * new one and check if it is initialized correctly.
         */
        priv->global = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, global);
        priv->object = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, object);
        priv->tostring = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE,
                                             self, tostring);
        if (!gwebkitjs_context_initialized(self)) {
            g_object_unref(self);
            return NULL;
        }
    } else {
        /* An old instance is found in the table. (not necessarily initialized
         * since update_table() is called before initialization.)
         * Check if it has been initialized. Failing on this check indicate a
         * race condition with another new allocated instance. Therefore,
         * unref the found one (since it is not clear whether it is usable and
         * a reference is obtain in the update_table function) and try again.
         * Otherwise, unref the new one (self) and return the found one.
         */
        if (!gwebkitjs_context_initialized(res)) {
            g_object_unref(res);
            goto try_update;
        } else {
            g_object_unref(self);
        }
    }
    return res;
free:
    if (self)
        g_object_unref(self);
    self = NULL;
    goto try_update;
}

/**
 * JSCore API.
 **/

/**
 * gwebkitjs_context_new:
 * @global: (allow-none): The type of the global object.
 *
 * Find the corresponding #GWebKitJSContext of a JSGlobalContextRef.
 * Creates a new one if not exist.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new(GType global)
{
    JSClassRef globalclass;
    JSGlobalContextRef jsctx;
    GWebKitJSContext *res;
    GWebKitJSBaseClass *baseklass;

    baseklass = g_type_class_ref(global);
    globalclass = gwebkitjs_base_get_jsclass(baseklass);
    g_type_class_unref(baseklass);

    jsctx = JSGlobalContextCreate(globalclass);
    res = gwebkitjs_context_new_from_context(jsctx);
    JSGlobalContextRelease(jsctx);
    return res;
}

/**
 * gwebkitjs_context_new_from_context: (skip)
 * @jsctx: (allow-none): The Javascript Context wrapped by GWebKitJSContext.
 *
 * Find the corresponding #GWebKitJSContext of a JSGlobalContextRef.
 * Creates a new one if not exist.
 *
 * Return value: the new #GWebKitJSContext
 **/
GWebKitJSContext*
gwebkitjs_context_new_from_context(JSGlobalContextRef jsctx)
{
    GWebKitJSContext *self;
    gwj_return_val_if_false(jsctx, NULL);

    self = g_object_new(GWEBKITJS_TYPE_CONTEXT, NULL);
    gwj_return_val_if_false(self, NULL);

    return gwebkitjs_context_init_context(self, jsctx);
}

/**
 * gwebkitjs_context_new_from_frame:
 * @webframe: (transfer none): The WebKit WebFrame to get the context from.
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
    return gwebkitjs_context_new_from_context(jsctx);
}

/**
 * gwebkitjs_context_new_from_view:
 * @webview: (transfer none): The WebKit WebView to get the context from.
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
 * @self: (transfer none): A #GWebKitJSContext.
 *
 * Get the JSGlobalContextRef wrapped by #GWebKitJSContext.
 *
 * Return value: (transfer none): the JSGlobalContextRef wrapped by
 * #GWebKitJSContext.
 **/
JSGlobalContextRef
gwebkitjs_context_get_context(GWebKitJSContext *self)
{
    gwj_return_val_if_false(GWEBKITJS_IS_CONTEXT(self), NULL);
    return self->priv->jsctx;
}

/**
 * gwebkitjs_context_get_global:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 *
 * Get the global object of the #GWebKitJSContext.
 *
 * Return value: (transfer none): the global object of the #GWebKitJSContext.
 **/
GWebKitJSValue*
gwebkitjs_context_get_global(GWebKitJSContext *self)
{
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);
    return self->priv->global;
}

/**
 * gwebkitjs_context_make_bool:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 * @b: the boolean value of the created jsvalue.
 *
 * Create a #GWebKitJSValue from a boolean value.
 *
 * Return value: (transfer full) (allow-none): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_bool(GWebKitJSContext *self, gboolean b)
{
    JSValueRef jsvalue;
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);

    jsvalue = JSValueMakeBoolean(self->priv->jsctx, b);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_make_from_json_str:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 * @json: (allow-none): the JSON string to create the object from.
 *
 * Create a #GWebKitJSValue from a JSON string.
 *
 * Return value: (transfer full) (allow-none): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_from_json_str(GWebKitJSContext *self,
                                     const gchar *json)
{
    JSValueRef jsvalue;
    JSStringRef jsstr;
    gwj_return_val_if_false(json && GWEBKITJS_CONTEXT_IS_VALID(self), NULL);

    jsstr = JSStringCreateWithUTF8CString(json);
    jsvalue = JSValueMakeFromJSONString(self->priv->jsctx, jsstr);
    JSStringRelease(jsstr);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_make_null:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 *
 * Create a null #GWebKitJSValue.
 *
 * Return value: (transfer full) (allow-none): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_null(GWebKitJSContext *self)
{
    JSValueRef jsvalue;
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);

    jsvalue = JSValueMakeNull(self->priv->jsctx);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_make_number:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 * @num: the value(number) of the created jsvalue.
 *
 * Create a #GWebKitJSValue from a number.
 *
 * Return value: (transfer full) (allow-none): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_number(GWebKitJSContext *self, gdouble num)
{
    JSValueRef jsvalue;
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);

    jsvalue = JSValueMakeNumber(self->priv->jsctx, num);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_make_string:
 * @self: (transfer none): A #GWebKitJSContext.
 * @str: (allow-none) (transfer none): the string to create the object from.
 *
 * Create a #GWebKitJSValue from a string.
 *
 * Return value: (transfer full) (allow-none): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_string(GWebKitJSContext *self, const gchar *str)
{
    JSValueRef jsvalue;
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);

    jsvalue = gwebkitjs_util_make_str(self->priv->jsctx, str);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_make_undefined:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 *
 * Create a undefined #GWebKitJSValue.
 *
 * Return value: (transfer full) (allow-none): the created #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_context_make_undefined(GWebKitJSContext *self)
{
    JSValueRef jsvalue;
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);
    jsvalue = JSValueMakeUndefined(self->priv->jsctx);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsvalue);
}

/**
 * gwebkitjs_context_get_value_type:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value..
 * @value: (allow-none) (transfer none): A #GWebKitJSValue
 *
 * Check the type of a value.
 *
 * Return value: the type of the value.
 **/
GWebKitJSValueType
gwebkitjs_context_get_value_type(GWebKitJSContext *self, GWebKitJSValue *value)
{
    JSType jstype;
    JSGlobalContextRef jsctx;
    JSValueRef jsvalue;
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            GWEBKITJS_VALUE_TYPE_UNKNOWN);
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            GWEBKITJS_VALUE_TYPE_UNKNOWN);
    jstype = JSValueGetType(jsctx, jsvalue);
    switch (jstype) {
    case kJSTypeUndefined:
        return GWEBKITJS_VALUE_TYPE_UNDEFINED;
    case kJSTypeNull:
        return GWEBKITJS_VALUE_TYPE_NULL;
    case kJSTypeBoolean:
        return GWEBKITJS_VALUE_TYPE_BOOLEAN;
    case kJSTypeNumber:
        return GWEBKITJS_VALUE_TYPE_NUMBER;
    case kJSTypeString:
        return GWEBKITJS_VALUE_TYPE_STRING;
    case kJSTypeObject:
        return GWEBKITJS_VALUE_TYPE_OBJECT;
    default:
        return GWEBKITJS_VALUE_TYPE_UNKNOWN;
    }
}

/**
 * gwebkitjs_context_is_bool:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
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
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            FALSE);
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            FALSE);
    return JSValueIsBoolean(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_null:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related
 * to the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
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
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            FALSE);
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            FALSE);
    return JSValueIsNull(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_number:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
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
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            FALSE);
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            FALSE);
    return JSValueIsNumber(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_string:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
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
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            FALSE);
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            FALSE);
    return JSValueIsString(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_object:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
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
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            FALSE);
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            FALSE);
    return JSValueIsObject(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_undefined:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
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
    gwj_return_val_if_false((jsctx = gwebkitjs_context_get_context(self)),
                            FALSE);
    gwj_return_val_if_false((jsvalue = gwebkitjs_value_get_value(value)),
                            FALSE);
    return JSValueIsUndefined(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_is_function:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
 *
 * Check if the type of a value can be called as a function.
 *
 * Return value: whether the type of the value is undefined.
 **/
gboolean
gwebkitjs_context_is_function(GWebKitJSContext *self, GWebKitJSValue *value)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, FALSE);

    return JSObjectIsFunction(jsctx, jsobject);
}
/**
 * gwebkitjs_context_is_constructor:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value.
 * @value: (allow-none) (transfer none): A #GWebKitJSValue.
 *
 * Check if the type of a value can be called as a constructor.
 *
 * Return value: whether the type of the value is undefined.
 **/
gboolean
gwebkitjs_context_is_constructor(GWebKitJSContext *self, GWebKitJSValue *value)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, FALSE);

    return JSObjectIsConstructor(jsctx, jsobject);
}
/**
 * gwebkitjs_context_get_name_str:
 * @self: (allow-none) (transfer none): The #GWebKitJSContext related to
 * the value..
 * @value: (allow-none) (transfer none): A #GWebKitJSValue
 * @error:
 *
 * Check the type string of a value.
 *
 * Return value: (allow-none) a string that represent the type of @value.
 **/
gchar*
gwebkitjs_context_get_name_str(GWebKitJSContext *self, GWebKitJSValue *value,
                               GError **error)
{
    GWebKitJSValue *tostring;
    GWebKitJSValue *res_val;
    gchar *res;
    gwj_return_val_if_false(GWEBKITJS_CONTEXT_IS_VALID(self), NULL);
    gwj_return_val_if_false(gwebkitjs_context_initialized(self), NULL);
    gwj_return_val_if_false(gwebkitjs_value_get_value(value), NULL);
    tostring = self->priv->tostring;
    res_val = gwebkitjs_context_call_function(self, tostring, value,
                                              0, NULL, error);
    gwj_return_val_if_false(res_val, NULL);
    res = gwebkitjs_context_to_string(self, res_val, error);
    g_object_unref(res_val);
    return res;
}

/**
 * gwebkitjs_context_is_eqaul:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 * @left: (allow-none) (transfer none): A #GWebKitJSValue.
 * @right: (allow-none) (transfer none): Another #GWebKitJSValue.
 * @error: (allow-none): Return location for error or %NULL.
 *
 * Compare whether @left and @right are equal in the context @self.
 *
 * Returns: Result of the comparison.
 */
gboolean
gwebkitjs_context_is_equal(GWebKitJSContext *self, GWebKitJSValue *left,
                           GWebKitJSValue *right, GError **error)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsleft;
    JSValueRef jsright;
    gboolean res;
    JSValueRef jserror = NULL;
    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsleft = gwebkitjs_value_get_value(left);
    gwj_return_val_if_false(jsleft, FALSE);
    jsright = gwebkitjs_value_get_value(right);
    gwj_return_val_if_false(jsright, FALSE);

    res = JSValueIsEqual(jsctx, jsleft, jsright, &jserror);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return res;
}
/**
 * gwebkitjs_context_is_instance_of:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 * @instance: (allow-none) (transfer none): A #GWebKitJSValue.
 * @construct: (allow-none) (transfer none): Another #GWebKitJSValue.
 * @error: (allow-none): Return location for error or %NULL.
 *
 * Return Value:
 */
gboolean
gwebkitjs_context_is_instance_of(GWebKitJSContext *self,
                                 GWebKitJSValue *instance,
                                 GWebKitJSValue *construct, GError **error)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsins;
    JSValueRef jscons;
    gboolean res;
    JSValueRef jserror = NULL;
    JSObjectRef jsobj;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsins = gwebkitjs_value_get_value(instance);
    gwj_return_val_if_false(jsins, FALSE);
    jscons = gwebkitjs_value_get_value(construct);
    gwj_return_val_if_false(jscons, FALSE);
    jsobj = JSValueToObject(jsctx, jscons, &jserror);
    if (!jsobj) {
        gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
        return FALSE;
    }
    jserror = NULL;

    res = JSValueIsInstanceOfConstructor(jsctx, jsins, jsobj, &jserror);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return res;
}

/**
 * gwebkitjs_context_is_strict_eqaul:
 * @self: (allow-none) (transfer none): A #GWebKitJSContext.
 * @left: (allow-none) (transfer none): A #GWebKitJSValue.
 * @right: (allow-none) (transfer none): Another #GWebKitJSValue.
 *
 * Compare whether @left and @right are stictly equal in the context @self.
 *
 * Returns: Result of the comparison.
 */
gboolean
gwebkitjs_context_is_strict_equal(GWebKitJSContext *self,
                                  GWebKitJSValue *left, GWebKitJSValue *right)
{
    JSGlobalContextRef jsctx;
    JSValueRef jsleft;
    JSValueRef jsright;
    gboolean res;
    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsleft = gwebkitjs_value_get_value(left);
    gwj_return_val_if_false(jsleft, FALSE);
    jsright = gwebkitjs_value_get_value(right);
    gwj_return_val_if_false(jsright, FALSE);

    res = JSValueIsStrictEqual(jsctx, jsleft, jsright);
    return res;
}
static JSValueRef*
gwebkitjs_context_make_arg_array(JSContextRef jsctx,
                                 size_t argc, GWebKitJSValue **argv)
{
    JSValueRef *jsargv = NULL;
    if (argc <= 0 || !argv) {
        return NULL;
    } else {
        int i;
        jsargv = g_new0(JSValueRef, argc);
        for (i = 0;i < argc;i++) {
            jsargv[i] = gwebkitjs_value_get_value(argv[i]);
            if (!jsargv[i])
                jsargv[i] = JSValueMakeUndefined(jsctx);
        }
    }
    return jsargv;
}

/**
 * gwebkitjs_context_call_function:
 * @self: (allow-none) (transfer none):
 * @func: (allow-none) (transfer none):
 * @thisobj: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_call_function(GWebKitJSContext *self, GWebKitJSValue *func,
                                GWebKitJSValue *thisobj, size_t argc,
                                GWebKitJSValue **argv, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsfunc_val;
    JSObjectRef jsfunc;
    JSObjectRef jsthis;
    JSValueRef jserror = NULL;
    JSValueRef *jsargv;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsfunc_val = gwebkitjs_value_get_value(func);
    gwj_return_val_if_false(jsfunc_val, NULL);
    jsthis = (JSObjectRef)gwebkitjs_value_get_value(thisobj);
    jsfunc = JSValueToObject(jsctx, jsfunc_val, &jserror);
    if (!jsfunc) {
        gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
        return NULL;
    }
    jserror = NULL;

    jsargv = gwebkitjs_context_make_arg_array(jsctx, argc, argv);
    if (!jsargv)
        argc = 0;
    jsres = JSObjectCallAsFunction(jsctx, jsfunc, jsthis,
                                   argc, jsargv, &jserror);
    g_free(jsargv);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}
/**
 * gwebkitjs_context_call_function_simple:
 * @self: (allow-none) (transfer none):
 * @func: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_call_function_simple(GWebKitJSContext *self,
                                       GWebKitJSValue *func,
                                       size_t argc, GWebKitJSValue **argv,
                                       GError **error)
{
    return gwebkitjs_context_call_function(self, func, NULL,
                                           argc, argv, error);
}

/**
 * gwebkitjs_context_call_constructor:
 * @self: (allow-none) (transfer none):
 * @func: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_call_constructor(GWebKitJSContext *self,
                                   GWebKitJSValue *func, size_t argc,
                                   GWebKitJSValue **argv, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsfunc_val;
    JSObjectRef jsfunc;
    JSValueRef jserror = NULL;
    JSValueRef *jsargv;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsfunc_val = gwebkitjs_value_get_value(func);
    gwj_return_val_if_false(jsfunc_val, NULL);
    jsfunc = JSValueToObject(jsctx, jsfunc_val, &jserror);
    if (!jsfunc) {
        gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
        return NULL;
    }
    jserror = NULL;

    jsargv = gwebkitjs_context_make_arg_array(jsctx, argc, argv);
    if (!jsargv)
        argc = 0;
    jsres = JSObjectCallAsConstructor(jsctx, jsfunc, argc, jsargv, &jserror);
    g_free(jsargv);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_to_json_str:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @indent:
 * @error:
 *
 * Return Value: The JSON String correspond to the object;
 **/
gchar*
gwebkitjs_context_to_json_str(GWebKitJSContext *self, GWebKitJSValue *value,
                              guint indent, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSValueRef jserror = NULL;
    JSStringRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, NULL);

    jsres = JSValueCreateJSONString(jsctx, jsvalue, indent, &jserror);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_util_convert_str(jsres);
}
/**
 * gwebkitjs_context_to_json_str_simple:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @error:
 *
 * Return Value: The JSON String correspond to the object;
 **/
gchar*
gwebkitjs_context_to_json_str_simple(GWebKitJSContext *self,
                                     GWebKitJSValue *value, GError **error)
{
    return gwebkitjs_context_to_json_str(self, value, 0, error);
}

/**
 * gwebkitjs_context_eval_js:
 * @self: (allow-none) (transfer none):
 * @script: (allow-none) (transfer none):
 * @thisobj: (allow-none) (transfer none):
 * @url: (allow-none) (transfer none):
 * @lineno:
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_eval_js(GWebKitJSContext *self, const gchar *script,
                          GWebKitJSValue *thisobj, const gchar *url,
                          gint lineno, GError **error)
{
    JSContextRef jsctx;
    JSObjectRef jsthis;
    JSStringRef jsurl = NULL;
    JSStringRef jsscript;
    JSValueRef jserror = NULL;
    JSValueRef jsres;

    gwj_return_val_if_false(script, NULL);

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsscript = JSStringCreateWithUTF8CString(script);
    gwj_return_val_if_false(jsscript, NULL);
    jsthis = (JSObjectRef)gwebkitjs_value_get_value(thisobj);
    if (url)
        jsurl = JSStringCreateWithUTF8CString(url);

    jsres = JSEvaluateScript(jsctx, jsscript, jsthis, jsurl, lineno, &jserror);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);

    JSStringRelease(jsscript);
    if (jsurl)
        JSStringRelease(jsurl);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_eval_js_simple:
 * @self: (allow-none) (transfer none):
 * @script: (allow-none) (transfer none):
 * @thisobj: (allow-none) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_eval_js_simple(GWebKitJSContext *self, const gchar *script,
                                 GWebKitJSValue *thisobj, GError **error)
{
    return gwebkitjs_context_eval_js(self, script, thisobj, NULL, 0, error);
}

/**
 * gwebkitjs_context_to_bool:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 *
 * Return Value:
 **/
gboolean
gwebkitjs_context_to_bool(GWebKitJSContext *self, GWebKitJSValue *value)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);

    return JSValueToBoolean(jsctx, jsvalue);
}

/**
 * gwebkitjs_context_to_number:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @error: (allow-none):
 *
 * Return Value:
 **/
gdouble
gwebkitjs_context_to_number(GWebKitJSContext *self, GWebKitJSValue *value,
                            GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSValueRef jserror = NULL;
    gdouble res;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NAN);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, NAN);

    res = JSValueToNumber(jsctx, jsvalue, &jserror);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return res;
}

/**
 * gwebkitjs_context_to_string:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (allow-none) (transfer full):
 **/
gchar*
gwebkitjs_context_to_string(GWebKitJSContext *self, GWebKitJSValue *value,
                            GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSValueRef jserror = NULL;
    JSStringRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, NULL);

    jsres = JSValueToStringCopy(jsctx, jsvalue, &jserror);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_util_convert_str(jsres);
}

/**
 * gwebkitjs_context_get_property_names:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @n: (out):
 *
 * Return Value: (array length=n) (element-type utf8) (allow-none) (transfer full):
 **/
gchar**
gwebkitjs_context_get_property_names(GWebKitJSContext *self,
                                     GWebKitJSValue *value, gint *n)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSPropertyNameArrayRef jsnamearray;
    gchar **res = NULL;
    gint i;
    gwj_return_val_if_false(n, NULL);

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, NULL);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, NULL);

    jsnamearray = JSObjectCopyPropertyNames(jsctx, jsobject);
    gwj_return_val_if_false(jsnamearray, NULL);

    *n = JSPropertyNameArrayGetCount(jsnamearray);

    if (*n > 0)
        res = g_new0(gchar*, *n);
    if (res) {
        for (i = 0;i < *n;i++) {
            res[i] = gwebkitjs_util_dup_str(
                JSPropertyNameArrayGetNameAtIndex(jsnamearray, i));
        }
    }

    JSPropertyNameArrayRelease(jsnamearray);
    return res;
}

/**
 * gwebkitjs_context_delete_property:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @error: (allow-none):
 *
 * Return Value:
 **/
gboolean
gwebkitjs_context_delete_property(GWebKitJSContext *self,
                                  GWebKitJSValue *value,
                                  const gchar *name, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSStringRef jsname;
    JSValueRef jserror = NULL;
    gboolean res = FALSE;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, FALSE);

    jsname = JSStringCreateWithUTF8CString(name);
    gwj_return_val_if_false(jsname, FALSE);
    res = JSObjectDeleteProperty(jsctx, jsobject, jsname, &jserror);
    JSStringRelease(jsname);

    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return res;
}

/**
 * gwebkitjs_context_get_property:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (allow-none) (transfer full):
 **/
GWebKitJSValue*
gwebkitjs_context_get_property(GWebKitJSContext *self, GWebKitJSValue *value,
                               const gchar *name, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);

    jsres = gwebkitjs_util_get_property(jsctx, jsvalue, name, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_get_property_at_index:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @index:
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/
GWebKitJSValue*
gwebkitjs_context_get_property_at_index(GWebKitJSContext *self,
                                        GWebKitJSValue *value,
                                        guint index, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSValueRef jserror = NULL;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, FALSE);

    jsres = JSObjectGetPropertyAtIndex(jsctx, jsobject, index, &jserror);

    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_has_property:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 *
 * Return Value:
 **/
gboolean
gwebkitjs_context_has_property(GWebKitJSContext *self, GWebKitJSValue *value,
                               const gchar *name)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSStringRef jsname;
    gboolean res = FALSE;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, FALSE);

    jsname = JSStringCreateWithUTF8CString(name);
    gwj_return_val_if_false(jsname, FALSE);
    res = JSObjectHasProperty(jsctx, jsobject, jsname);
    JSStringRelease(jsname);

    return res;
}

/**
 * gwebkitjs_context_set_property:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @prop_value: (allow-none) (transfer none):
 * @attr:
 * @error:
 **/
void
gwebkitjs_context_set_property(GWebKitJSContext *self, GWebKitJSValue *value,
                               const gchar *name, GWebKitJSValue *prop_value,
                               GWebKitJSPropertyAttribute attr,
                               GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSValueRef jsprop;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_if_false(jsctx);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_if_false(jsvalue);
    jsprop = gwebkitjs_value_get_value(prop_value);
    gwj_return_if_false(jsprop);

    gwebkitjs_util_set_property(jsctx, jsvalue, name, jsprop, attr, error);
}

/**
 * gwebkitjs_context_set_property_at_index:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @index:
 * @prop_value: (allow-none) (transfer none):
 * @error:
 **/
void
gwebkitjs_context_set_property_at_index(GWebKitJSContext *self,
                                        GWebKitJSValue *value,
                                        guint index,
                                        GWebKitJSValue *prop_value,
                                        GError **error)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSValueRef jserror = NULL;
    JSValueRef jsprop;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_if_false(jsctx);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_if_false(jsvalue);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_if_false(jsobject);
    jsprop = gwebkitjs_value_get_value(prop_value);
    gwj_return_if_false(jsprop);

    JSObjectSetPropertyAtIndex(jsctx, jsobject, index, jsprop, &jserror);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
}

/**
 * gwebkitjs_context_get_prototype:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 *
 * Return Value: (allow-none) (transfer full):
 **/
GWebKitJSValue*
gwebkitjs_context_get_prototype(GWebKitJSContext *self, GWebKitJSValue *value)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, NULL);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_val_if_false(jsobject, NULL);

    jsres = JSObjectGetPrototype(jsctx, jsobject);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_set_prototype:
 * @self: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @proto: (allow-none) (transfer none):
 **/
void
gwebkitjs_context_set_prototype(GWebKitJSContext *self, GWebKitJSValue *value,
                                GWebKitJSValue *proto)
{
    JSContextRef jsctx;
    JSValueRef jsvalue;
    JSObjectRef jsobject;
    JSValueRef jsproto;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_if_false(jsctx);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_if_false(jsvalue);
    jsobject = JSValueToObject(jsctx, jsvalue, NULL);
    gwj_return_if_false(jsobject);
    jsproto = gwebkitjs_value_get_value(proto);
    gwj_return_if_false(jsproto);

    JSObjectSetPrototype(jsctx, jsobject, jsproto);
}

/**
 * gwebkitjs_context_make_function:
 * @self: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @argc:
 * @argnames: (allow-none) (transfer none) (array length=argc) (element-type utf8):
 * @body: (allow-none) (transfer none):
 * @url: (allow-none) (transfer none):
 * @lineno:
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/
GWebKitJSValue*
gwebkitjs_context_make_function(GWebKitJSContext *self, const char *name,
                                guint argc, const char **argnames,
                                const char *body, const char *url,
                                gint lineno, GError **error)
{
    JSContextRef jsctx;
    JSStringRef jsname = NULL;
    JSStringRef *jsargnames = NULL;
    JSStringRef jsbody;
    JSStringRef jsurl = NULL;
    JSValueRef jserror = NULL;
    JSValueRef jsres;
    int i;
    gwj_return_val_if_false(body, NULL);

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);
    if (name)
        jsname = JSStringCreateWithUTF8CString(name);
    if (argc && argnames) {
        jsargnames = g_new0(JSStringRef, argc);
        for (i = 0;i < argc;i++)
            jsargnames[i] = JSStringCreateWithUTF8CString(argnames[i]);
    } else {
        argc = 0;
    }
    jsbody = JSStringCreateWithUTF8CString(body);
    if (url)
        jsurl = JSStringCreateWithUTF8CString(url);

    jsres = JSObjectMakeFunction(jsctx, jsname, argc, jsargnames, jsbody,
                                 jsurl, lineno, &jserror);

    if (jsurl)
        JSStringRelease(jsurl);
    if (jsbody)
        JSStringRelease(jsbody);
    for (i = 0;i < argc;i++) {
        if (jsargnames[i]) {
            JSStringRelease(jsargnames[i]);
        }
    }
    if (jsargnames)
        g_free(jsargnames);
    if (jsname)
        JSStringRelease(jsname);
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_make_function_simple:
 * @self: (allow-none) (transfer none):
 * @argc:
 * @argnames: (allow-none) (transfer none) (array length=argc) (element-type utf8):
 * @body: (allow-none) (transfer none):
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/
GWebKitJSValue*
gwebkitjs_context_make_function_simple(GWebKitJSContext *self,
                                       guint argc, const char **argnames,
                                       const char *body, GError **error)
{
    return gwebkitjs_context_make_function(self, NULL, argc, argnames,
                                           body, NULL, 0, error);
}

/**
 * gwebkitjs_context_garbage_collect:
 * @self: (allow-none) (transfer none):
 **/
void
gwebkitjs_context_garbage_collect(GWebKitJSContext *self)
{
    JSContextRef jsctx;
    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_if_false(jsctx);
    JSGarbageCollect(jsctx);
}

/**
 * gwebkitjs_context_make_array:
 * @self: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_make_array(GWebKitJSContext *self, size_t argc,
                             GWebKitJSValue **argv, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jserror = NULL;
    JSValueRef *jsargv;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);

    jsargv = gwebkitjs_context_make_arg_array(jsctx, argc, argv);
    if (!jsargv)
        argc = 0;
    jsres = JSObjectMakeArray(jsctx, argc, jsargv, &jserror);
    g_free(jsargv);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_make_date:
 * @self: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_make_date(GWebKitJSContext *self, size_t argc,
                             GWebKitJSValue **argv, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jserror = NULL;
    JSValueRef *jsargv;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);

    jsargv = gwebkitjs_context_make_arg_array(jsctx, argc, argv);
    if (!jsargv)
        argc = 0;
    jsres = JSObjectMakeDate(jsctx, argc, jsargv, &jserror);
    g_free(jsargv);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_make_error:
 * @self: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_make_error(GWebKitJSContext *self, size_t argc,
                             GWebKitJSValue **argv, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jserror = NULL;
    JSValueRef *jsargv;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);

    jsargv = gwebkitjs_context_make_arg_array(jsctx, argc, argv);
    if (!jsargv)
        argc = 0;
    jsres = JSObjectMakeError(jsctx, argc, jsargv, &jserror);
    g_free(jsargv);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

/**
 * gwebkitjs_context_make_regexp:
 * @self: (allow-none) (transfer none):
 * @argc:
 * @argv: (allow-none) (array length=argc) (transfer none):
 * @error: (allow-none):
 *
 * Return Value: (transfer full) (allow-none):
 **/
GWebKitJSValue*
gwebkitjs_context_make_regexp(GWebKitJSContext *self, size_t argc,
                             GWebKitJSValue **argv, GError **error)
{
    JSContextRef jsctx;
    JSValueRef jserror = NULL;
    JSValueRef *jsargv;
    JSValueRef jsres;

    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, NULL);

    jsargv = gwebkitjs_context_make_arg_array(jsctx, argc, argv);
    if (!jsargv)
        argc = 0;
    jsres = JSObjectMakeRegExp(jsctx, argc, jsargv, &jserror);
    g_free(jsargv);
    if (jsres)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(jsctx, jserror, error);
    return gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, self, jsres);
}

gboolean
gwebkitjs_context_is_of_class(GWebKitJSContext *self, GWebKitJSValue *value,
                              GType type)
{
    JSClassRef jsclass;
    JSContextRef jsctx;
    JSValueRef jsvalue;
    jsctx = gwebkitjs_context_get_context(self);
    gwj_return_val_if_false(jsctx, FALSE);
    jsvalue = gwebkitjs_value_get_value(value);
    gwj_return_val_if_false(jsvalue, FALSE);
    jsclass = gwebkitjs_base_get_jsclass_from_type(type);
    gwj_return_val_if_false(jsclass, FALSE);
    return JSValueIsObjectOfClass(jsctx, jsvalue, jsclass);
}
