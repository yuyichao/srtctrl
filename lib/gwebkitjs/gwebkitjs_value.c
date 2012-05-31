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
    JSValueRef *jsvalue;
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
}

static void
gwebkitjs_value_base_init(GWebKitJSValueClass *klass)
{
}

static void
gwebkitjs_value_class_init(GWebKitJSValueClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
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
