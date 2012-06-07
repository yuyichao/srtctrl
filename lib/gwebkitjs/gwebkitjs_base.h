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
typedef struct _GWebKitJSBaseClass GWebKitJSBaseClass;
typedef struct _GWebKitJSBaseClassPrivate GWebKitJSBaseClassPrivate;

struct _GWebKitJSBase {
    GWebKitJSValue parent;
};

typedef const gchar *(*GWebKitJSBaseGetName)(GWebKitJSBase *self);
typedef gboolean (*GWebKitJSBaseHasProperty)(
    GWebKitJSBase *self, GWebKitJSContext *ctx, const char *name);
typedef GWebKitJSValue *(*GWebKitJSBaseGetProperty)(
    GWebKitJSBase *self, GWebKitJSContext *ctx,
    const char *name, GError **error);
typedef gboolean (*GWebKitJSBaseSetProperty)(
    GWebKitJSBase *self, GWebKitJSContext *ctx, const char *name,
    GWebKitJSValue *value, GError **error);
typedef gboolean (*GWebKitJSBaseDeleteProperty)(
    GWebKitJSBase *self, GWebKitJSContext *ctx,
    const char *name, GError **error);
typedef gchar **(*GWebKitJSBaseGetPropertyNames)(
    GWebKitJSBase *self, GWebKitJSContext *ctx, gint *n, GError **error);
typedef GWebKitJSValue *(*GWebKitJSBaseCallFunction)(
    GWebKitJSBase *self, GWebKitJSContext *ctx, GWebKitJSValue *thisobj,
    size_t argc, GWebKitJSValue **argv, GError **error);
typedef GWebKitJSValue *(*GWebKitJSBaseCallConstruct)(
    GWebKitJSBase *self, GWebKitJSContext *ctx,
    size_t argc, GWebKitJSValue **argv, GError **error);
typedef gboolean (*GWebKitJSBaseHasInstance)(
    GWebKitJSBase *self, GWebKitJSContext *ctx,
    GWebKitJSValue *instance, GError **error);
typedef GWebKitJSValue *(*GWebKitJSBaseConvertTo)(
    GWebKitJSBase *self, GWebKitJSContext *ctx,
    GWebKitJSValueType type, GError **error);

struct _GWebKitJSBaseClass {
    GWebKitJSValueClass parent_class;
    GWebKitJSBaseClassPrivate *priv;
    GWebKitJSBaseGetName get_name;
    GWebKitJSBaseHasProperty has_property;
    GWebKitJSBaseGetProperty get_property;
    GWebKitJSBaseSetProperty set_property;
    GWebKitJSBaseDeleteProperty delete_property;
    GWebKitJSBaseGetPropertyNames get_property_names;
    GWebKitJSBaseCallFunction call_function;
    GWebKitJSBaseCallConstruct call_construct;
    GWebKitJSBaseHasInstance has_instance;
    GWebKitJSBaseConvertTo convert_to;
};

#ifdef __cplusplus
extern "C" {
#endif
    GType gwebkitjs_base_get_type();
    JSClassRef gwebkitjs_base_get_jsclass(GType type);
#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_BASE_H__ */
