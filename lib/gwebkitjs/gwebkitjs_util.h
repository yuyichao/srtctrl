#ifndef __GWEBKITJS_UTIL_H__
#define __GWEBKITJS_UTIL_H__

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

#include <glib-object.h>
#include <gwebkitjs_value.h>
#include <JavaScriptCore/JSObjectRef.h>

typedef enum {
    GWEBKITJS_PROPERTY_ATTRIBUTE_NONE = 0,
    GWEBKITJS_PROPERTY_ATTRIBUTE_READONLY = (1 << 0),
    GWEBKITJS_PROPERTY_ATTRIBUTE_DONTENUM = (1 << 1),
    GWEBKITJS_PROPERTY_ATTRIBUTE_DONTDELETE = (1 << 2),
} GWebKitJSPropertyAttribute;

#define gwj_return_if_false(exp)                \
    do {                                        \
        if (G_UNLIKELY(!(exp)))                 \
            return;                             \
    } while(0)

#define gwj_return_val_if_false(exp, val)       \
    do {                                        \
        if (G_UNLIKELY(!(exp)))                 \
            return (val);                       \
    } while(0)

#ifdef __cplusplus
extern "C" {
#endif
    gchar *gwebkitjs_util_dup_str(JSStringRef jsstr);
    gchar *gwebkitjs_util_convert_str(JSStringRef jsstr);
    gchar *gwebkitjs_util_value_to_str(JSContextRef ctx, JSValueRef jsvalue);
    JSValueRef gwebkitjs_util_make_str(JSContextRef ctx, const char *str);

    gchar *gwebkitjs_util_jserror_get_name(JSContextRef ctx,
                                           JSValueRef jserror);
    gchar *gwebkitjs_util_jserror_get_message(JSContextRef ctx,
                                              JSValueRef jserror);
    void gwebkitjs_util_gerror_from_jserror(JSContextRef ctx,
                                            JSValueRef jserror,
                                            GError **error);
    void gwebkitjs_util_make_jserror(JSContextRef ctx, JSValueRef *jserror,
                                     const gchar *name, const gchar *msg);
    void gwebkitjs_util_jserror_from_gerror(JSContextRef ctx,
                                            JSValueRef *jserror,
                                            GError *error);
    JSValueRef gwebkitjs_util_get_property(JSContextRef ctx,
                                           JSValueRef self,
                                           const gchar *name,
                                           GError **error);
    void gwebkitjs_util_set_property(JSContextRef ctx,
                                     JSValueRef self,
                                     const gchar *name,
                                     JSValueRef prop,
                                     GWebKitJSPropertyAttribute prop_attr,
                                     GError **error);
    GObject *gwebkitjs_util_list_to_obj(int n, gchar **array);
    GArray *gwebkitjs_util_get_name_ary(GObject *obj);
    GObject *gwebkitjs_util_argv_to_obj(int argc, GWebKitJSValue **argv);
    GWebKitJSValue **gwebkitjs_util_get_argv(GObject *obj, int *argc);
#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_UTIL_H__ */
