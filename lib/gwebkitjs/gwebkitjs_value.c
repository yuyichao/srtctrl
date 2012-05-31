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
    JSValueRef jsvalue;
    GWebKitJSContext *ctx;
};

static void gwebkitjs_value_init(GWebKitJSValue *self,
                                 GWebKitJSValueClass *klass);

static void gwebkitjs_value_class_init(GWebKitJSValueClass *klass,
                                       gpointer data);
static void gwebkitjs_value_dispose(GObject *obj);
static void gwebkitjs_value_finalize(GObject *obj);
/* static void gwebkitjs_value_set_property(GObject *obj, guint prop_id, */
/*                                          const GValue *value, */
/*                                          GParamSpec *pspec); */
/* static void gwebkitjs_value_get_property(GObject *obj, guint prop_id, */
/*                                          GValue *value, */
/*                                          GParamSpec *pspec); */

GType
gwebkitjs_value_get_type()
{
    static GType value_type = 0;
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
    priv->jsvalue = NULL;
    priv->ctx = NULL;
}

static void
gwebkitjs_value_class_init(GWebKitJSValueClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSValuePrivate));
    /* gobject_class->set_property = gwebkitjs_value_set_property; */
    /* gobject_class->get_property = gwebkitjs_value_get_property; */
    gobject_class->dispose = gwebkitjs_value_dispose;
    gobject_class->finalize = gwebkitjs_value_finalize;
}

static void
gwebkitjs_value_dispose(GObject *obj)
{
    /* GWebKitJSValue *self = GWEBKITJS_VALUE(obj); */
}

static void
gwebkitjs_value_finalize(GObject *obj)
{
}

/* static void */
/* gwebkitjs_value_set_property(GObject *obj, guint prop_id, */
/*                                const GValue *value, GParamSpec *pspec) */
/* { */
/*     GWebKitJSValue *self = GWEBKITJS_VALUE(obj); */

/*     switch (prop_id) { */
/*     default: */
/*         G_OBJECT_WARN_INVALID_PROPERTY_ID(obj, prop_id, pspec); */
/*         break; */
/*     } */
/* } */

/* static void */
/* gwebkitjs_value_get_property(GObject *obj, guint prop_id, */
/*                                GValue *value, GParamSpec *pspec) */
/* { */
/*     GWebKitJSValue *self = GWEBKITJS_VALUE(obj); */

/*     switch (prop_id) { */
/*     default: */
/*         G_OBJECT_WARN_INVALID_PROPERTY_ID(obj, prop_id, pspec); */
/*         break; */
/*     } */
/* } */

/**
 * gwebkitjs_value_new: (skip)
 * @ctx: The #GWebKitJSContext which wraps the Javascript Context of the value.
 * @jsvalue: The JSValueRef to be wrapped by #GWebKitJSValue.
 *
 * Creates a new wrapper of a javascript value. NOTE: this function does NOT
 * protect the jsvalue, call JSValueProtect manually if necessary.
 *
 * Return value: the new #GWebKitJSValue.
 **/
GWebKitJSValue*
gwebkitjs_value_new(GWebKitJSContext *ctx, JSValueRef jsvalue)
{
    GWebKitJSValue *self;
    GWebKitJSValuePrivate *priv;
    g_return_val_if_fail(GWEBKITJS_IS_CONTEXT(ctx), NULL);

    self = g_object_new(GWEBKITJS_TYPE_VALUE, NULL);
    if (!self)
        return NULL;
    priv = self->priv;
    priv->ctx = ctx;
    /* TODO: add weak ref */
    priv->jsvalue = jsvalue;
    return self;
}

GWebKitJSValueType
gwebkitjs_value_get_value_type(GWebKitJSValue *self)
{
    JSContextRef jsctx;
    JSType jstype;
    g_return_val_if_fail(GWEBKITJS_IS_VALUE(self),
                         GWEBKITJS_VALUE_TYPE_UNKNOWN);
    g_return_val_if_fail(self->priv->jsvalue,
                         GWEBKITJS_VALUE_TYPE_UNKNOWN);
    jsctx = gwebkitjs_context_get_context(self->priv->ctx);
    g_return_val_if_fail(jsctx,
                         GWEBKITJS_VALUE_TYPE_UNKNOWN);
    jstype = JSValueGetType(jsctx, self->priv->jsvalue);
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
