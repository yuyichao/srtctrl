#ifndef __GWEBKITJS_BASE_H__
#define __GWEBKITJS_BASE_H__

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

#include <gwebkitjs_value.h>

#define GWEBKITJS_TYPE_BASE (gwebkitjs_base_get_type())
#define GWEBKITJS_BASE(obj)                                  \
    (G_TYPE_CHECK_INSTANCE_CAST((obj), GWEBKITJS_TYPE_BASE,  \
                                GWebKitJSBase))
#define GWEBKITJS_IS_BASE(obj)                               \
    (G_TYPE_CHECK_INSTANCE_TYPE((obj), GWEBKITJS_TYPE_BASE))
#define GWEBKITJS_BASE_CLASS(klass)                          \
    (G_TYPE_CHECK_CLASS_CAST((klass), GWEBKITJS_TYPE_BASE,   \
                             GWebKitJSBaseClass))
#define GWEBKITJS_IS_BASE_CLASS(klass)                       \
    (G_TYPE_CHECK_CLASS_TYPE((klass), GWEBKITJS_TYPE_BASE))
#define GWEBKITJS_BASE_GET_CLASS(obj)                        \
    (G_TYPE_INSTANCE_GET_CLASS((obj), GWEBKITJS_TYPE_BASE,   \
                               GWebKitJSBaseClass))

typedef struct _GWebKitJSBase GWebKitJSBase;
typedef struct _GWebKitJSBasePrivate GWebKitJSBasePrivate;
typedef struct _GWebKitJSBaseClass GWebKitJSBaseClass;
typedef struct _GWebKitJSBaseClassPrivate GWebKitJSBaseClassPrivate;

struct _GWebKitJSBase {
    GWebKitJSValue parent;
    GWebKitJSBasePrivate *priv;
};

struct _GWebKitJSBaseClass {
    GWebKitJSValueClass parent_class;
    GWebKitJSBaseClassPrivate *priv;
    gboolean (*has_property)(GWebKitJSBase *self, GWebKitJSContext *ctx,
                             const char *name);
    GWebKitJSValue *(*get_property)(GWebKitJSBase *self, GWebKitJSContext *ctx,
                                    const char *name, GError **error);
    gboolean (*set_property)(
        GWebKitJSBase *self, GWebKitJSContext *ctx, const char *name,
        GWebKitJSValue *value, GError **error);
    gboolean (*delete_property)(GWebKitJSBase *self, GWebKitJSContext *ctx,
                                const char *name, GError **error);
    /**
     * I don't really want to say bad word in source code but I think this
     * REALLY is the right time to do that..... WTF pygobject!!!!! for not
     * supporting directly returning arrays and I have to use a object to do
     * that!!!! Fine here since this library is DESIGNED for language bindings
     * (therefore it can be a little hard to use for c programmers), but isn't
     * gir designed for easy language binding!!!...... also please catch python
     * exceptions and turn it into a GError, when the callback has a error out
     * argument....
     **/
    GObject *(*get_property_names)(GWebKitJSBase *self, GWebKitJSContext *ctx);
    GWebKitJSValue *(*call_function)(
        GWebKitJSBase *self, GWebKitJSContext *ctx, GWebKitJSValue *thisobj,
        size_t argc, GWebKitJSValue **argv, GError **error);
    GWebKitJSValue *(*call_construct)(
        GWebKitJSBase *self, GWebKitJSContext *ctx,
        size_t argc, GWebKitJSValue **argv, GError **error);
    gboolean (*has_instance)(GWebKitJSBase *self, GWebKitJSContext *ctx,
                             GWebKitJSValue *instance, GError **error);
    GWebKitJSValue *(*convert_to)(GWebKitJSBase *self, GWebKitJSContext *ctx,
                                  GWebKitJSValueType type, GError **error);
};

#ifdef __cplusplus
extern "C" {
#endif
    GType gwebkitjs_base_get_type();
    JSClassRef gwebkitjs_base_get_jsclass(GWebKitJSBaseClass *class);
    void gwebkitjs_base_set_name(GType type, const gchar *name);
#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_BASE_H__ */
