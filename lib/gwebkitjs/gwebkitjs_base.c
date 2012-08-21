#include <gwebkitjs_context.h>
#include <gwebkitjs_base.h>
#include <gwebkitjs_util.h>
#include <gwebkitjs_closure.h>
#include <JavaScriptCore/JSStringRef.h>
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

struct _GWebKitJSBasePrivate {
    gboolean toggle_added;
};

struct _GWebKitJSBaseClassPrivate {
    gchar *name;
    JSClassRef jsclass;
    JSClassDefinition jsdefine;
    GWebKitJSClosure *init_clsr;
};

static void gwebkitjs_base_init(GWebKitJSBase *self,
                                GWebKitJSBaseClass *klass);
static void gwebkitjs_base_base_init(GWebKitJSBaseClass *klass);
static void gwebkitjs_base_class_init(GWebKitJSBaseClass *klass,
                                      gpointer data);
static void gwebkitjs_base_dispose(GObject *obj);
static void gwebkitjs_base_finalize(GObject *obj);

static GWebKitJSClosureType clsr_type_v_p_p = NULL;

static gboolean gwebkitjs_base_is_valid_name(const gchar *name);
static JSClassRef gwebkitjs_base_get_jsclass(GWebKitJSBaseClass *klass);

/**
 * GWebKitJSBaseClass::has_property:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 *
 * Returns:
 **/
/**
 * GWebKitJSBaseClass::get_property:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @error:
 *
 * Returns: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseClass::set_property:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @error:
 *
 * Returns:
 **/
/**
 * GWebKitJSBaseClass::delete_property:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @error:
 *
 * Returns:
 **/
/**
 * GWebKitJSBaseClass::get_property_names:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 *
 * Returns: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseClass::call_function:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @thisobj: (allow-none) (transfer none):
 * @argv: (allow-none) (transfer none):
 * @error:
 *
 * Returns: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseClass::call_construct:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @argv: (allow-none) (transfer none):
 * @error:
 *
 * Returns: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseClass::has_instance:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @instance: (allow-none) (transfer none):
 * @error:
 *
 * Returns:
 **/
/**
 * GWebKitJSBaseClass::convert_to:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @type:
 * @error:
 *
 * Returns: (allow-none) (transfer full):
 **/

static void
gwebkitjs_base_init_clsr()
{
    clsr_type_v_p_p = gwebkitjs_closure_new_type(NULL, 2, &ffi_type_pointer,
                                                 &ffi_type_pointer);
}

GType
gwebkitjs_base_get_type()
{
    static GType base_type = 0;
    if (G_UNLIKELY(base_type == 0)) {
        const GTypeInfo base_info = {
            .class_size = sizeof(GWebKitJSBaseClass),
            .base_init = (GBaseInitFunc)gwebkitjs_base_base_init,
            .base_finalize = NULL,
            .class_init = (GClassInitFunc)gwebkitjs_base_class_init,
            .class_finalize = NULL,
            .class_data = NULL,
            .instance_size = sizeof(GWebKitJSBase),
            .n_preallocs = 0,
            .instance_init = (GInstanceInitFunc)gwebkitjs_base_init,
            .value_table = NULL,
        };

        base_type = g_type_register_static(GWEBKITJS_TYPE_VALUE,
                                           "GWebKitJSBase",
                                           &base_info, G_TYPE_FLAG_ABSTRACT);
        g_type_add_class_private(base_type, sizeof(GWebKitJSBaseClassPrivate));
        gwebkitjs_base_init_clsr();
    }
    return base_type;
}

static void
gwebkitjs_base_init(GWebKitJSBase *self, GWebKitJSBaseClass *klass)
{
    GWebKitJSBasePrivate *priv;
    priv = self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                                    GWEBKITJS_TYPE_BASE,
                                                    GWebKitJSBasePrivate);
    gwebkitjs_base_get_jsclass(klass);
    priv->toggle_added = FALSE;
}

static void
gwebkitjs_base_base_init(GWebKitJSBaseClass *klass)
{
    klass->priv = G_TYPE_CLASS_GET_PRIVATE(klass, GWEBKITJS_TYPE_BASE,
                                           GWebKitJSBaseClassPrivate);
    klass->priv->jsclass = NULL;
    klass->priv->jsdefine = kJSClassDefinitionEmpty;
    klass->priv->name = NULL;
}

static void
gwebkitjs_base_class_init(GWebKitJSBaseClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSBasePrivate));
    gobject_class->dispose = gwebkitjs_base_dispose;
    gobject_class->finalize = gwebkitjs_base_finalize;
}

static void
gwebkitjs_base_dispose(GObject *obj)
{
    /* GWebKitJSBase *self = GWEBKITJS_BASE(obj); */
}

static void
gwebkitjs_base_finalize(GObject *obj)
{
    /* GWebKitJSBase *self = GWEBKITJS_BASE(obj); */
}

static void
gwebkitjs_base_toggle_cb(gpointer data, GObject *self, gboolean is_last)
{
    if (is_last)
        gwebkitjs_value_unprotect_value(GWEBKITJS_VALUE(self));
    else
        gwebkitjs_value_protect_value(GWEBKITJS_VALUE(self));
}

static gboolean
gwebkitjs_base_is_derived_class(GType type, JSGlobalContextRef jsctx,
                                JSObjectRef jsvalue)
{
    guint i;
    guint n;
    GType *children;
    JSClassRef jsclass;
    gboolean res = FALSE;
    children = g_type_children(type, &n);
    for (i = 0;i < n;i++) {
        jsclass = gwebkitjs_base_get_jsclass_from_type(children[i]);
        if (JSValueIsObjectOfClass(jsctx, jsvalue, jsclass)) {
            res = TRUE;
            break;
        }
    }
    g_free(children);
    return res;
}

static void
gwebkitjs_base_init_cb(gpointer ptr, JSGlobalContextRef jsctx,
                       JSObjectRef jsvalue)
{
    GType type;
    GWebKitJSContext *ctx;
    GWebKitJSBase *self;
    type = GPOINTER_TO_INT(ptr);
    /**
     * So this is the problem trying to relate each jsclass with a gtype.
     * We only do real work when this is the most derived type we know,
     * in order to ensure @self has the right type.....
     **/
    if (gwebkitjs_base_is_derived_class(type, jsctx, jsvalue))
        return;
    ctx = gwebkitjs_context_new_from_context(jsctx, FALSE);
    self = GWEBKITJS_BASE(gwebkitjs_value_new(type, ctx, jsvalue));
    JSObjectSetPrivate(jsvalue, self);
    if (g_atomic_int_compare_and_exchange(&self->priv->toggle_added,
                                          FALSE, TRUE)) {
        g_object_add_toggle_ref(G_OBJECT(self), gwebkitjs_base_toggle_cb,
                                NULL);
        gwebkitjs_value_unprotect_value(GWEBKITJS_VALUE(self));
        g_object_unref(self);
    }
    g_object_unref(ctx);
}

static void
gwebkitjs_base_finalize_cb(JSObjectRef jsobj)
{
    GWebKitJSBase *self;
    self = JSObjectGetPrivate(jsobj);
    if (!self)
        return;
    if (g_atomic_int_compare_and_exchange(&self->priv->toggle_added,
                                          TRUE, FALSE)) {
        g_object_remove_toggle_ref(G_OBJECT(self), gwebkitjs_base_toggle_cb,
                                   NULL);
    }
    JSObjectSetPrivate(jsobj, NULL);
}

static bool
gwebkitjs_base_has_property_cb(JSContextRef jsctx, JSObjectRef jsobj,
                               JSStringRef jsname)
{
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    bool res;
    gchar *name;
    self = JSObjectGetPrivate(jsobj);
    gwj_return_val_if_false(self, false);
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    gwj_return_val_if_false(klass, false);
    gwj_return_val_if_false(klass->has_property, false);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx,
                                             FALSE);
    gwj_return_val_if_false(ctx, false);
    name = gwebkitjs_util_dup_str(jsname);
    if (G_UNLIKELY(!name)) {
        res = false;
    } else {
        res = klass->has_property(self, ctx, name);
        g_free(name);
    }
    g_object_unref(ctx);
    return res;
}

static JSValueRef
gwebkitjs_base_get_property_cb(JSContextRef jsctx, JSObjectRef jsobj,
                               JSStringRef jsname, JSValueRef *jserr)
{
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    gchar *name;
    GWebKitJSValue *res;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return NULL;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return NULL;
    }
    gwj_return_val_if_false(klass->get_property, NULL);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return NULL;
    }
    name = gwebkitjs_util_dup_str(jsname);
    if (G_UNLIKELY(!name)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Cannot Get Name.");
        res = NULL;
    } else {
        res = klass->get_property(self, ctx, name, NULL);
        g_free(name);
    }
    g_object_unref(ctx);
    if (res) {
        JSValueRef jsres = gwebkitjs_value_get_value(res);
        g_object_unref(res);
        return jsres;
    }
    return NULL;
}

static bool
gwebkitjs_base_set_property_cb(JSContextRef jsctx, JSObjectRef jsobj,
                               JSStringRef jsname, JSValueRef jsvalue,
                               JSValueRef *jserr)
{
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    GWebKitJSValue *value;
    bool res = false;
    gchar *name;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return false;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return false;
    }
    gwj_return_val_if_false(klass->set_property, false);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return false;
    }
    value = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsvalue);
    if (G_UNLIKELY(!value))
        goto out;
    name = gwebkitjs_util_dup_str(jsname);
    if (G_LIKELY(name)) {
        res = klass->set_property(self, ctx, name, value, NULL);
        g_free(name);
    }
    g_object_unref(value);
out:
    g_object_unref(ctx);
    return res;
}

static bool
gwebkitjs_base_delete_property_cb(JSContextRef jsctx, JSObjectRef jsobj,
                                  JSStringRef jsname, JSValueRef *jserr)
{
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    bool res = false;
    gchar *name;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return false;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return false;
    }
    gwj_return_val_if_false(klass->delete_property, false);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return false;
    }
    name = gwebkitjs_util_dup_str(jsname);
    if (G_LIKELY(name)) {
        res = klass->delete_property(self, ctx, name, NULL);
        g_free(name);
    }
    g_object_unref(ctx);
    return res;
}

static void
gwebkitjs_base_get_property_names_cb(JSContextRef jsctx, JSObjectRef jsobj,
                                     JSPropertyNameAccumulatorRef jsnames)
{
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    GObject *obj;
    GArray *ary;
    self = JSObjectGetPrivate(jsobj);
    gwj_return_if_false(self);
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    gwj_return_if_false(klass);
    gwj_return_if_false(klass->get_property_names);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    gwj_return_if_false(ctx);
    obj = klass->get_property_names(self, ctx);
    ary = gwebkitjs_util_get_name_ary(obj);
    if (G_LIKELY(ary)) {
        guint i;
        JSStringRef jsname;
        for (i = 0;i < ary->len;i++) {
            jsname = JSStringCreateWithUTF8CString(((gchar**)(ary->data))[i]);
            JSPropertyNameAccumulatorAddName(jsnames, jsname);
            JSStringRelease(jsname);
        }
    }
    if (obj)
        g_object_unref(obj);
    g_object_unref(ctx);
}

static JSValueRef
gwebkitjs_base_call_function_cb(JSContextRef jsctx, JSObjectRef jsobj,
                                JSObjectRef jsthis, size_t argc,
                                const JSValueRef *jsargv, JSValueRef *jserr)
{
    int i;
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    GWebKitJSValue *res;
    GWebKitJSValue *this;
    JSValueRef jsres = NULL;
    GWebKitJSValue *argv[argc];
    GObject *argvobj;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return NULL;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return NULL;
    }
    gwj_return_val_if_false(klass->call_function, NULL);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return NULL;
    }
    this = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsthis);
    if (G_UNLIKELY(!this)) {
        this = gwebkitjs_context_get_global(ctx);
        g_object_ref(this);
    }
    for (i = 0;i < argc;i++) {
        argv[i] = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsargv[i]);
        if (!argv[i])
            goto free_argv;
    }
    argvobj = gwebkitjs_util_argv_to_obj(argc, argv);
    res = klass->call_function(self, ctx, this, argvobj, NULL);
    g_object_unref(argvobj);
    if (res) {
        jsres = gwebkitjs_value_get_value(res);
        g_object_unref(res);
    }
free_argv:
    for (i = 0;i < argc;i++) {
        if (argv[i])
            g_object_unref(argv[i]);
    }
    g_object_unref(this);
    g_object_unref(ctx);
    return jsres;
}

static JSObjectRef
gwebkitjs_base_call_construct_cb(JSContextRef jsctx, JSObjectRef jsobj,
                                 size_t argc, const JSValueRef *jsargv,
                                 JSValueRef *jserr)
{
    int i;
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    GWebKitJSValue *res;
    JSValueRef jsres = NULL;
    GWebKitJSValue *argv[argc];
    GObject *argvobj;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return NULL;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return NULL;
    }
    gwj_return_val_if_false(klass->call_construct, NULL);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return NULL;
    }
    for (i = 0;i < argc;i++) {
        argv[i] = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsargv[i]);
        if (!argv[i])
            goto free_argv;
    }
    argvobj = gwebkitjs_util_argv_to_obj(argc, argv);
    res = klass->call_construct(self, ctx, argvobj, NULL);
    g_object_unref(argvobj);
    if (res) {
        jsres = gwebkitjs_value_get_value(res);
        g_object_unref(res);
    }
free_argv:
    for (i = 0;i < argc;i++) {
        if (argv[i])
            g_object_unref(argv[i]);
    }
    g_object_unref(ctx);
    if (jsres)
        return JSValueToObject(jsctx, jsres, jserr);
    return NULL;
}

static bool
gwebkitjs_base_has_instance_cb(JSContextRef jsctx, JSObjectRef jsobj,
                               JSValueRef jsins, JSValueRef *jserr)
{
    bool res = false;
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    GWebKitJSValue *ins;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return false;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return false;
    }
    gwj_return_val_if_false(klass->has_instance, false);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return false;
    }
    ins = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsins);
    if (G_UNLIKELY(!ins)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Instance Object Not Found.");
        goto free_ctx;
    }
    res = klass->has_instance(self, ctx, ins, NULL);
    g_object_unref(ins);
free_ctx:
    g_object_unref(ctx);
    return res;
}

static JSValueRef
gwebkitjs_base_convert_to_cb(JSContextRef jsctx, JSObjectRef jsobj,
                             JSType type, JSValueRef *jserr)
{
    GWebKitJSBase *self;
    GWebKitJSBaseClass *klass;
    GWebKitJSContext *ctx;
    GWebKitJSValue *res;
    self = JSObjectGetPrivate(jsobj);
    if (G_UNLIKELY(!self)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Object Not Found.");
        return NULL;
    }
    klass = GWEBKITJS_BASE_GET_CLASS(self);
    if (G_UNLIKELY(!klass)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Class Not Found.");
        return NULL;
    }
    gwj_return_val_if_false(klass->convert_to, NULL);
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx, FALSE);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return NULL;
    }
    res = klass->convert_to(self, ctx, type + 1, NULL);
    g_object_unref(ctx);
    if (res) {
        JSValueRef jsres = gwebkitjs_value_get_value(res);
        g_object_unref(res);
        return jsres;
    }
    return NULL;
}

static JSClassDefinition*
gwebkitjs_base_get_definition(GWebKitJSBaseClass *klass)
{
    GWebKitJSBaseClass *pklass;
    JSClassRef pjsclass;
    JSClassDefinition *define;
    GWebKitJSBaseClassPrivate *priv;
    gwj_return_val_if_false(GWEBKITJS_IS_BASE_CLASS(klass), NULL);
    priv = klass->priv;
    if (priv->jsdefine.className)
        return &priv->jsdefine;

    define = &priv->jsdefine;
    pklass = g_type_class_peek_parent(klass);
    pjsclass = gwebkitjs_base_get_jsclass(pklass);
    define->version = 0;
    define->attributes = kJSClassAttributeNone;
    define->parentClass = pjsclass;
    if (gwebkitjs_base_is_valid_name(priv->name))
        define->className = priv->name;
    else
        define->className = "GWebKitJS";
    klass->priv->init_clsr = gwebkitjs_closure_create(
        clsr_type_v_p_p, G_CALLBACK(gwebkitjs_base_init_cb),
        GINT_TO_POINTER(G_TYPE_FROM_CLASS(klass)));
    define->initialize =
        (JSObjectInitializeCallback)priv->init_clsr->func;
    define->finalize = gwebkitjs_base_finalize_cb;
    if (klass->has_property)
        define->hasProperty = gwebkitjs_base_has_property_cb;
    if (klass->get_property)
        define->getProperty = gwebkitjs_base_get_property_cb;
    if (klass->set_property)
        define->setProperty = gwebkitjs_base_set_property_cb;
    if (klass->delete_property)
        define->deleteProperty = gwebkitjs_base_delete_property_cb;
    if (klass->get_property_names)
        define->getPropertyNames = gwebkitjs_base_get_property_names_cb;
    if (klass->call_function)
        define->callAsFunction = gwebkitjs_base_call_function_cb;
    if (klass->call_construct)
        define->callAsConstructor = gwebkitjs_base_call_construct_cb;
    if (klass->has_instance)
        define->hasInstance = gwebkitjs_base_has_instance_cb;
    if (klass->convert_to)
        define->convertToType = gwebkitjs_base_convert_to_cb;
    return define;
}

/**
 * gwebkitjs_base_get_jsclass: (skip)
 * @type:
 *
 * Returns:
 **/
static JSClassRef
gwebkitjs_base_get_jsclass(GWebKitJSBaseClass *klass)
{
    JSClassDefinition *define;
    gwj_return_val_if_false(GWEBKITJS_IS_BASE_CLASS(klass), NULL);
    if (G_TYPE_FROM_CLASS(klass) == GWEBKITJS_TYPE_BASE)
        return NULL;

    if (!klass->priv->jsclass) {
        define = gwebkitjs_base_get_definition(klass);
        klass->priv->jsclass = JSClassCreate(define);
    }

    return klass->priv->jsclass;
}

static gboolean
gwebkitjs_base_is_valid_name(const gchar *name)
{
    static gchar *black_list[] = {
        "Boolean",
        "Null",
        "Undefined",
        "Number",
        "String",
        "Array",
        "Error",
        "Date",
        "Function",
        "RegExp",
        "Object"
    };
    int i;
    if (!name)
        return FALSE;
    for (i = 0;i < sizeof(black_list) / sizeof(gchar*);i++) {
        if (!g_strcmp0(black_list[i], name))
            return FALSE;
    }
    return TRUE;
}

void
gwebkitjs_base_set_name(GType type, const gchar *name)
{
    GWebKitJSBaseClass *klass;
    gwj_return_if_false(g_type_is_a(type, GWEBKITJS_TYPE_BASE));
    gwj_return_if_false(type != GWEBKITJS_TYPE_BASE);
    if (!gwebkitjs_base_is_valid_name(name))
        return;

    klass = g_type_class_ref(type);
    do {
        if (klass->priv->jsdefine.className)
            break;
        g_free(klass->priv->name);
        klass->priv->name = g_strdup(name);
    } while(0);
    g_type_class_unref(klass);
}

/**
 * gwebkitjs_base_new:
 * @ctx: (allow-none) (transfer none):
 * @type:
 *
 * Returns: (allow-none) (transfer full):
 **/
GWebKitJSValue*
gwebkitjs_base_new(GWebKitJSContext *ctx, GType type)
{
    JSObjectRef jsobj;
    JSClassRef jsclass;
    JSContextRef jsctx;
    GWebKitJSValue *res;
    jsctx = gwebkitjs_context_get_context(ctx);
    gwj_return_val_if_false(jsctx, NULL);
    jsclass = gwebkitjs_base_get_jsclass_from_type(type);
    gwj_return_val_if_false(jsclass, NULL);

    jsobj = JSObjectMake(jsctx, jsclass, NULL);
    res = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsobj);
    return res;
}

/**
 * gwebkitjs_base_get_jsclass_from_type: (skip)
 **/
JSClassRef
gwebkitjs_base_get_jsclass_from_type(GType type)
{
    GWebKitJSBaseClass *klass;
    JSClassRef jsclass;
    gwj_return_val_if_false(g_type_is_a(type, GWEBKITJS_TYPE_BASE), NULL);
    gwj_return_val_if_false(type != GWEBKITJS_TYPE_BASE, NULL);

    klass = g_type_class_ref(type);
    jsclass = gwebkitjs_base_get_jsclass(klass);
    g_type_class_unref(klass);
    return jsclass;
}
