#ifndef __GWEBKITJS_CONTEXT_H__
#define __GWEBKITJS_CONTEXT_H__

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
#include <JavaScriptCore/JSContextRef.h>
#include <webkit/webkitwebview.h>
#include <gwebkitjs_value.h>
#include <gwebkitjs_util.h>

#define GWEBKITJS_TYPE_CONTEXT (gwebkitjs_context_get_type())
#define GWEBKITJS_CONTEXT(obj)                                  \
    (G_TYPE_CHECK_INSTANCE_CAST((obj), GWEBKITJS_TYPE_CONTEXT,  \
                                GWebKitJSContext))
#define GWEBKITJS_IS_CONTEXT(obj)                               \
    (G_TYPE_CHECK_INSTANCE_TYPE((obj), GWEBKITJS_TYPE_CONTEXT))
#define GWEBKITJS_CONTEXT_CLASS(klass)                          \
    (G_TYPE_CHECK_CLASS_CAST((klass), GWEBKITJS_TYPE_CONTEXT,   \
                             GWebKitJSContextClass))
#define GWEBKITJS_IS_CONTEXT_CLASS(klass)                       \
    (G_TYPE_CHECK_CLASS_TYPE((klass), GWEBKITJS_TYPE_CONTEXT))
#define GWEBKITJS_CONTEXT_GET_CLASS(obj)                        \
    (G_TYPE_INSTANCE_GET_CLASS((obj), GWEBKITJS_TYPE_CONTEXT,   \
                               GWebKitJSContextClass))

typedef struct _GWebKitJSContext GWebKitJSContext;
typedef struct _GWebKitJSContextPrivate GWebKitJSContextPrivate;
typedef struct _GWebKitJSContextClass GWebKitJSContextClass;

struct _GWebKitJSContext {
    GObject parent;
    GWebKitJSContextPrivate *priv;
};

struct _GWebKitJSContextClass {
    GObjectClass parent_class;
};

#ifdef __cplusplus
extern "C" {
#endif
    GType gwebkitjs_context_get_type();
    GWebKitJSContext *gwebkitjs_context_new(GType global);
    GWebKitJSContext *gwebkitjs_context_new_from_context(
        JSGlobalContextRef jsctx);
    GWebKitJSContext *gwebkitjs_context_new_from_frame(
        WebKitWebFrame *webframe);
    GWebKitJSContext *gwebkitjs_context_new_from_view(WebKitWebView *webview);

    JSGlobalContextRef gwebkitjs_context_get_context(GWebKitJSContext *self);
    GWebKitJSValue *gwebkitjs_context_get_global(GWebKitJSContext *self);

    GWebKitJSValue *gwebkitjs_context_make_bool(GWebKitJSContext *self,
                                                gboolean b);
    GWebKitJSValue *gwebkitjs_context_make_from_json_str(GWebKitJSContext *self,
                                                         const gchar *json);
    GWebKitJSValue *gwebkitjs_context_make_null(GWebKitJSContext *self);
    GWebKitJSValue *gwebkitjs_context_make_number(GWebKitJSContext *self,
                                                  gdouble num);
    GWebKitJSValue *gwebkitjs_context_make_string(GWebKitJSContext *self,
                                                  const gchar *str);
    GWebKitJSValue *gwebkitjs_context_make_undefined(GWebKitJSContext *self);

    GWebKitJSValueType gwebkitjs_context_get_value_type(GWebKitJSContext *self,
                                                        GWebKitJSValue *value);
    gchar *gwebkitjs_context_get_name_str(GWebKitJSContext *self,
                                          GWebKitJSValue *value,
                                          GError **error);
    gboolean gwebkitjs_context_is_bool(GWebKitJSContext *self,
                                       GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_null(GWebKitJSContext *self,
                                       GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_number(GWebKitJSContext *self,
                                         GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_string(GWebKitJSContext *self,
                                         GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_object(GWebKitJSContext *self,
                                         GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_undefined(GWebKitJSContext *self,
                                            GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_function(GWebKitJSContext *self,
                                            GWebKitJSValue *value);
    gboolean gwebkitjs_context_is_constructor(GWebKitJSContext *self,
                                              GWebKitJSValue *value);

    gboolean gwebkitjs_context_is_instance_of(GWebKitJSContext *self,
                                              GWebKitJSValue *instance,
                                              GWebKitJSValue *construct,
                                              GError **error);
    gboolean gwebkitjs_context_is_of_class(GWebKitJSContext *self,
                                           GWebKitJSValue *value,
                                           GType type);

    GWebKitJSValue *gwebkitjs_context_call_function(GWebKitJSContext *self,
                                                    GWebKitJSValue *func,
                                                    GWebKitJSValue *thisobj,
                                                    size_t argc,
                                                    GWebKitJSValue **argv,
                                                    GError **error);
    GWebKitJSValue *gwebkitjs_context_call_function_simple(
        GWebKitJSContext *self, GWebKitJSValue *func,
        size_t argc, GWebKitJSValue **argv, GError **error);
    GWebKitJSValue *gwebkitjs_context_call_constructor(GWebKitJSContext *self,
                                                       GWebKitJSValue *func,
                                                       size_t argc,
                                                       GWebKitJSValue **argv,
                                                       GError **error);

    gboolean gwebkitjs_context_is_equal(GWebKitJSContext *self,
                                        GWebKitJSValue *left,
                                        GWebKitJSValue *right,
                                        GError **error);
    gboolean gwebkitjs_context_is_strict_equal(GWebKitJSContext *self,
                                               GWebKitJSValue *left,
                                               GWebKitJSValue *right);

    gchar *gwebkitjs_context_to_json_str(GWebKitJSContext *self,
                                         GWebKitJSValue *value, guint indent,
                                         GError **error);
    gchar *gwebkitjs_context_to_json_str_simple(GWebKitJSContext *self,
                                                GWebKitJSValue *value,
                                                GError **error);
    gboolean gwebkitjs_context_to_bool(GWebKitJSContext *self,
                                       GWebKitJSValue *value);
    gdouble gwebkitjs_context_to_number(GWebKitJSContext *self,
                                        GWebKitJSValue *value,
                                        GError **error);
    gchar *gwebkitjs_context_to_string(GWebKitJSContext *self,
                                       GWebKitJSValue *value,
                                       GError **error);
    GWebKitJSValue *gwebkitjs_context_eval_js(GWebKitJSContext *self,
                                              const gchar *script,
                                              GWebKitJSValue *thisobj,
                                              const gchar *url,
                                              gint lineno,
                                              GError **error);
    GWebKitJSValue *gwebkitjs_context_eval_js_simple(GWebKitJSContext *self,
                                                     const gchar *script,
                                                     GWebKitJSValue *thisobj,
                                                     GError **error);
    gchar **gwebkitjs_context_get_property_names(GWebKitJSContext *self,
                                                 GWebKitJSValue *value,
                                                 gint *n);
    gboolean gwebkitjs_context_delete_property(GWebKitJSContext *self,
                                               GWebKitJSValue *value,
                                               const gchar *name,
                                               GError **error);
    GWebKitJSValue *gwebkitjs_context_get_property(
        GWebKitJSContext *self, GWebKitJSValue *value, const gchar *name,
        GError **error);
    GWebKitJSValue *gwebkitjs_context_get_property_at_index(
        GWebKitJSContext *self, GWebKitJSValue *value, guint index,
        GError **error);
    gboolean gwebkitjs_context_has_property(GWebKitJSContext *self,
                                            GWebKitJSValue *value,
                                            const gchar *name);
    void gwebkitjs_context_set_property(GWebKitJSContext *self,
                                        GWebKitJSValue *value,
                                        const gchar *name,
                                        GWebKitJSValue *prop_value,
                                        GWebKitJSPropertyAttribute attr,
                                        GError **error);
    void gwebkitjs_context_set_property_at_index(GWebKitJSContext *self,
                                                 GWebKitJSValue *value,
                                                 guint index,
                                                 GWebKitJSValue *prop_value,
                                                 GError **error);
    GWebKitJSValue *gwebkitjs_context_get_prototype(GWebKitJSContext *self,
                                                    GWebKitJSValue *value);
    void gwebkitjs_context_set_prototype(GWebKitJSContext *self,
                                         GWebKitJSValue *value,
                                         GWebKitJSValue *proto);
    GWebKitJSValue *gwebkitjs_context_make_function(GWebKitJSContext *self,
                                                    const char *name,
                                                    guint argc,
                                                    const char **argnames,
                                                    const char *body,
                                                    const char *url,
                                                    gint lineno,
                                                    GError **error);
    GWebKitJSValue *gwebkitjs_context_make_function_simple(
        GWebKitJSContext *self, guint argc, const char **argnames,
        const char *body, GError **error);
    void gwebkitjs_context_garbage_collect(GWebKitJSContext *self);
    GWebKitJSValue *gwebkitjs_context_make_array(GWebKitJSContext *self,
                                                 size_t argc,
                                                 GWebKitJSValue **argv,
                                                 GError **error);
    GWebKitJSValue *gwebkitjs_context_make_date(GWebKitJSContext *self,
                                                size_t argc,
                                                GWebKitJSValue **argv,
                                                GError **error);
    GWebKitJSValue *gwebkitjs_context_make_error(GWebKitJSContext *self,
                                                 size_t argc,
                                                 GWebKitJSValue **argv,
                                                 GError **error);
    GWebKitJSValue *gwebkitjs_context_make_regexp(GWebKitJSContext *self,
                                                  size_t argc,
                                                  GWebKitJSValue **argv,
                                                  GError **error);
    GWebKitJSValue *gwebkitjs_context_make_object(GWebKitJSContext *ctx,
                                                  GType type);

    // JSObjectMakeConstructor (need Base)
    // JSObjectMakeFunctionWithCallback (need Base)
#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_CONTEXT_H__ */
