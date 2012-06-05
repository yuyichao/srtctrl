#include <gwebkitjs_util.h>
#include <gwebkitjs_value.h>
#include <gwebkitjs_context.h>

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

struct _GWebKitJSValuePrivate {
    gint hold_value;
    JSValueRef jsvalue;
    GRecMutex ctx_lock;
    GHashTable *ctx_table;
};

#define GWEBKITJS_VALUE_IS_VALID(_jsvalue)                        \
    ({                                                            \
        GWebKitJSValue *jsvalue = (jsvalue);                      \
        jsvalue && GWEBKITJS_IS_VALUE(ctx) && ctx->priv->jsvalue; \
    })


/**
 * Declarations
 **/
static void gwebkitjs_value_init(GWebKitJSValue *self,
                                 GWebKitJSValueClass *klass);
static void gwebkitjs_value_class_init(GWebKitJSValueClass *klass,
                                       gpointer data);
static void gwebkitjs_value_dispose(GObject *obj);
static void gwebkitjs_value_finalize(GObject *obj);

static void _gwebkitjs_value_init_table();
static void _gwebkitjs_value_remove_from_table(JSValueRef key,
                                               GWebKitJSValue *value);
static GWebKitJSValue* _gwebkitjs_value_update_table(GWebKitJSValue* gvalue,
                                                     JSValueRef jsvalue);

static void gwebkitjs_value_add_context(GWebKitJSValue *self,
                                        GWebKitJSContext *ctx);
static void gwebkitjs_value_remove_context(GWebKitJSValue *self,
                                           GWebKitJSContext *ctx);


/**
 * GObject Functions.
 **/
GType
gwebkitjs_value_get_type()
{
    static GType value_type = 0;
    _gwebkitjs_value_init_table();
    if (G_UNLIKELY(value_type == 0)) {
        const GTypeInfo value_info = {
            .class_size = sizeof(GWebKitJSValueClass),
            .base_init = NULL,
            .base_finalize = NULL,
            .class_init = (GClassInitFunc)gwebkitjs_value_class_init,
            .class_finalize = NULL,
            .class_data = NULL,
            .instance_size = sizeof(GWebKitJSValue),
            .n_preallocs = 0,
            .instance_init = (GInstanceInitFunc)gwebkitjs_value_init,
            .value_table = NULL,
        };

        value_type = g_type_register_static(G_TYPE_OBJECT,
                                            "GWebKitJSValue",
                                            &value_info, G_TYPE_FLAG_ABSTRACT);
    }
    return value_type;
}

static void
gwebkitjs_value_init(GWebKitJSValue *self, GWebKitJSValueClass *klass)
{
    GWebKitJSValuePrivate *priv;
    priv = self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                                    GWEBKITJS_TYPE_VALUE,
                                                    GWebKitJSValuePrivate);
    priv->hold_value = 1;
    priv->jsvalue = NULL;
    g_rec_mutex_init(&priv->ctx_lock);
    priv->ctx_table = g_hash_table_new(g_direct_hash, g_direct_equal);
}

static void
gwebkitjs_value_class_init(GWebKitJSValueClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSValuePrivate));
    gobject_class->dispose = gwebkitjs_value_dispose;
    gobject_class->finalize = gwebkitjs_value_finalize;
}

static void
gwebkitjs_value_dispose(GObject *obj)
{
    GWebKitJSValue *self = GWEBKITJS_VALUE(obj);
    gwebkitjs_value_unprotect_value(self);
    if (self->priv->jsvalue) {
        _gwebkitjs_value_remove_from_table(self->priv->jsvalue, self);
        self->priv->jsvalue = NULL;
    }
    if (self->priv->ctx_table) {
        g_hash_table_unref(self->priv->ctx_table);
        self->priv->ctx_table = NULL;
    }
}

static void
gwebkitjs_value_finalize(GObject *obj)
{
    GWebKitJSValue *self = GWEBKITJS_VALUE(obj);
    g_rec_mutex_clear(&self->priv->ctx_lock);
}


/**
 * Value Table Functions.
 **/
/**
 * A hash table that saves the mapping between JSValueRef
 * and GWebKitJSContext. Used to find the right GWebKitJSContext
 * from a JSCore callback.
 **/
static GHashTable *value_table = NULL;
G_LOCK_DEFINE_STATIC(value_table);

/**
 * _gwebkitjs_value_init_table:
 *
 * Initialize the value table if it has not been initialized already.
 **/
static void
_gwebkitjs_value_init_table()
{
    if (G_UNLIKELY(!value_table)) {
        value_table = g_hash_table_new(g_direct_hash, g_direct_equal);
    }
}

/**
 * _gwebkitjs_value_remove_from_table:
 * @key: A JSValueRef (key of value_table).
 * @value: A #GWebKitJSValue (value of value_table).
 *
 * Remove the key-value pair from the value_table, do nothing if the
 * current value of key is not the same with the given value.
 **/
static void
_gwebkitjs_value_remove_from_table(JSValueRef key, GWebKitJSValue *value)
{
    gpointer orig;
    G_LOCK(value_table);
    orig = g_hash_table_lookup(value_table, key);
    if (G_LIKELY(orig == value))
        g_hash_table_remove(value_table, key);
    G_UNLOCK(value_table);
}

/**
 * _gwebkitjs_value_update_table:
 * @gctx: A new created #GWebKitJSValue. (cannot be NULL)
 *
 * Look up the corresponding JSValueRef of the #GWebKitJSValue. If found,
 * add the reference counting of the found #GWebKitJSValue and unref() the
 * new one. Otherwise, add the new one to value_table.
 *
 * Return Value: the correct #GWebKitJSValue correspond to the JSValueRef.
 **/
static GWebKitJSValue*
_gwebkitjs_value_update_table(GWebKitJSValue* gvalue, JSValueRef jsvalue)
{
    gpointer orig;
update_start:
    G_LOCK(value_table);
    orig = g_hash_table_lookup(value_table, jsvalue);
    if (!orig && gvalue) {
        g_hash_table_replace(value_table, (gpointer)jsvalue, gvalue);
    }
    G_UNLOCK(value_table);
    if (orig) {
        orig = g_object_ref(orig);
        /* If disposing has already started but the object hasn't been removed
         * from value_table.
         */
        if (G_UNLIKELY(!orig)) {
            _gwebkitjs_value_remove_from_table(jsvalue, orig);
            goto update_start;
        }
        if (gvalue)
            g_object_unref(gvalue);
        return orig;
    }
    return gvalue;
}


/**
 * Context Table and Reference Counting.
 **/
static void
gwebkitjs_value_context_dispose_cb(GWebKitJSValue *self, GWebKitJSContext *ctx)
{
    gwebkitjs_value_remove_context(self, ctx);
}

static void
gwebkitjs_value_remove_context(GWebKitJSValue *self, GWebKitJSContext *ctx)
{
    gboolean exist;
    gboolean hold_value = FALSE;
    g_rec_mutex_lock(&self->priv->ctx_lock);
    exist = g_hash_table_remove(self->priv->ctx_table, ctx);
    hold_value = exist && (self->priv->hold_value > 0);
    g_rec_mutex_unlock(&self->priv->ctx_lock);
    if (exist) {
        if (hold_value) {
            JSValueUnprotect(gwebkitjs_context_get_context(ctx),
                             self->priv->jsvalue);
        }
        g_object_weak_ref(G_OBJECT(ctx),
                          (GWeakNotify)gwebkitjs_value_context_dispose_cb,
                          self);
    }
}

static void
gwebkitjs_value_add_context(GWebKitJSValue *self, GWebKitJSContext *ctx)
{
    gpointer orig;
    gboolean hold_value = FALSE;
    g_rec_mutex_lock(&self->priv->ctx_lock);
    orig = g_hash_table_lookup(self->priv->ctx_table, ctx);
    if (!orig) {
        g_hash_table_add(self->priv->ctx_table, ctx);
        hold_value = self->priv->hold_value > 0;
    }
    g_rec_mutex_unlock(&self->priv->ctx_lock);
    if (!orig) {
        if (hold_value) {
            JSValueProtect(gwebkitjs_context_get_context(ctx),
                           self->priv->jsvalue);
        }
        g_object_weak_unref(G_OBJECT(ctx),
                            (GWeakNotify)gwebkitjs_value_context_dispose_cb,
                            self);
    }
}

static void
gwebkitjs_value_protect_cb(GWebKitJSContext *ctx, GWebKitJSValue *self)
{
    JSValueProtect(gwebkitjs_context_get_context(ctx),
                   self->priv->jsvalue);
}

static void
gwebkitjs_value_unprotect_cb(GWebKitJSContext *ctx, GWebKitJSValue *self)
{
    JSValueUnprotect(gwebkitjs_context_get_context(ctx),
                     self->priv->jsvalue);
}

/**
 * gwebkitjs_value_protect_value: (skip)
 * @self: A #GWebKitJSValue.
 *
 * Protect the JSValueRef wrapped by the #GWebKitJSValue. This function and
 * gwebkitjs_value_unprotect_value() is only useful for self-defined object
 * to avoid reference loop when the only reference left of the object
 * is hold by JSCore.
 **/
void
gwebkitjs_value_protect_value(GWebKitJSValue *self)
{
    GList *ctxs = NULL;
    gwj_return_if_false(GWEBKITJS_IS_VALUE(self));

    g_rec_mutex_lock(&self->priv->ctx_lock);
    if (self->priv->hold_value++ == 0) {
        ctxs = g_hash_table_get_values(self->priv->ctx_table);
    }
    g_rec_mutex_unlock(&self->priv->ctx_lock);

    if (ctxs)
        g_list_foreach(ctxs, (GFunc)gwebkitjs_value_protect_cb, self);
}

/**
 * gwebkitjs_value_unprotect_value: (skip)
 * @self: A #GWebKitJSValue.
 *
 * Protect the JSValueRef wrapped by the #GWebKitJSValue. This function and
 * gwebkitjs_value_protect_value() is only useful for self-defined object
 * to avoid reference loop when the only reference left of the object
 * is hold by JSCore.
 **/
void gwebkitjs_value_unprotect_value(GWebKitJSValue *self)
{
    GList *ctxs = NULL;
    gwj_return_if_false(GWEBKITJS_IS_VALUE(self));

    g_rec_mutex_lock(&self->priv->ctx_lock);
    if (--self->priv->hold_value == 0) {
        ctxs = g_hash_table_get_values(self->priv->ctx_table);
    }
    g_rec_mutex_unlock(&self->priv->ctx_lock);

    if (ctxs)
        g_list_foreach(ctxs,  (GFunc)gwebkitjs_value_unprotect_cb, self);
}


/**
 * JSCore API.
 **/
/**
 * gwebkitjs_value_get_value: (skip)
 * @self: A #GWebKitJSValue.
 *
 * Get the JSValueRef wrapped by #GWebKitJSValue.
 *
 * Return value: the JSValueRef wrapped by #GWebKitJSValue.
 **/
JSValueRef
gwebkitjs_value_get_value(GWebKitJSValue *self)
{
    gwj_return_val_if_false(GWEBKITJS_IS_VALUE(self), NULL);
    return self->priv->jsvalue;
}

/**
 * gwebkitjs_value_new: (skip)
 * @type: The GType of the instance, must be derived from #GWebKitJSValue or
 * %NULL for dry lookup.
 * @ctx: The #GWebKitJSContext related to the value.
 * @jsvalue: The JSValueRef to be wrapped by #GWebKitJSValue.
 *
 * Creates a new wrapper of a javascript value.
 *
 * Return value: the new #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_value_new(GType type, GWebKitJSContext *ctx, JSValueRef jsvalue)
{
    GWebKitJSValue *self = NULL;
    gwj_return_val_if_false(jsvalue, NULL);
    if (type) {
        gwj_return_val_if_false(g_type_is_a(type, GWEBKITJS_TYPE_VALUE), NULL);
        self = g_object_new(type, NULL);
        if (self)
            self->priv->jsvalue = jsvalue;
    }
    self = _gwebkitjs_value_update_table(self, jsvalue);

    if (self)
        gwebkitjs_value_add_context(self, ctx);
    return self;
}

/**
 * Proxy of functions in gwebkitjs_context
 **/

/**
 * gwebkitjs_value_get_value_type:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check the type of a value.
 *
 * Return value: the type of the value.
 **/
GWebKitJSValueType
gwebkitjs_value_get_value_type(GWebKitJSValue *self, GWebKitJSContext *ctx)
{
    return gwebkitjs_context_get_value_type(ctx, self);
}

/**
 * gwebkitjs_value_is_bool:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check if the type of a value is boolean.
 *
 * Return value: whether the type of the value is boolean.
 **/
gboolean
gwebkitjs_value_is_bool(GWebKitJSValue *self,
                        GWebKitJSContext *ctx)
{
    return gwebkitjs_context_is_bool(ctx, self);
}

/**
 * gwebkitjs_value_is_null:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check if the type of a value is null.
 *
 * Return value: whether the type of the value is null.
 **/
gboolean
gwebkitjs_value_is_null(GWebKitJSValue *self,
                        GWebKitJSContext *ctx)
{
    return gwebkitjs_context_is_null(ctx, self);
}

/**
 * gwebkitjs_value_is_number:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check if the type of a value is number.
 *
 * Return value: whether the type of the value is number.
 **/
gboolean
gwebkitjs_value_is_number(GWebKitJSValue *self,
                          GWebKitJSContext *ctx)
{
    return gwebkitjs_context_is_number(ctx, self);
}

/**
 * gwebkitjs_value_is_string:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check if the type of a value is string.
 *
 * Return value: whether the type of the value is string.
 **/
gboolean
gwebkitjs_value_is_string(GWebKitJSValue *self,
                                   GWebKitJSContext *ctx)
{
    return gwebkitjs_context_is_string(ctx, self);
}

/**
 * gwebkitjs_value_is_object:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check if the type of a value is object.
 *
 * Return value: whether the type of the value is object.
 **/
gboolean
gwebkitjs_value_is_object(GWebKitJSValue *self,
                          GWebKitJSContext *ctx)
{
    return gwebkitjs_context_is_object(ctx, self);
}


/**
 * gwebkitjs_value_is_undefined:
 * @self: A #GWebKitJSValue.
 * @ctx: The #GWebKitJSContext related to the value.
 *
 * Check if the type of a value is undefined.
 *
 * Return value: whether the type of the value is undefined.
 **/
gboolean gwebkitjs_value_is_undefined(GWebKitJSValue *self,
                                      GWebKitJSContext *ctx)
{
    return gwebkitjs_context_is_undefined(ctx, self);
}
