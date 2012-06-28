#include <gwebkitjs_context.h>
#include <gwebkitjs_base.h>
#include <gwebkitjs_util.h>
#include <gwebkitjs_closure.h>

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

/**
 * GWebKitJSBaseHasProperty:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 *
 * Return Value:
 **/
/**
 * GWebKitJSBaseGetProperty:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseSetProperty:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @value: (allow-none) (transfer none):
 * @error:
 *
 * Return Value:
 **/
/**
 * GWebKitJSBaseDeleteProperty:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @name: (allow-none) (transfer none):
 * @error:
 *
 * Return Value:
 **/
/**
 * GWebKitJSBaseGetPropertyNames:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @n: (out)
 * @error:
 *
 * Return Value: (allow-none) (transfer full) (array length=n) (element-type utf8):
 **/
/**
 * GWebKitJSBaseCallFunction:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @thisobj: (allow-none) (transfer none):
 * @argc:
 * @argv: (array length=argc) (allow-none) (transfer none):
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseCallConstruct:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @argc:
 * @argv: (array length=argc) (allow-none) (transfer none):
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/
/**
 * GWebKitJSBaseHasInstance:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @instance: (allow-none) (transfer none):
 * @error:
 *
 * Return Value:
 **/

static void
gwebkitjs_base_init_clsr()
{
    clsr_type_v_p_p = gwebkitjs_closure_new_type(NULL, 2, &ffi_type_pointer,
                                                 &ffi_type_pointer);
}

/**
 * GWebKitJSBaseConvertTo:
 * @self: (allow-none) (transfer none):
 * @ctx: (allow-none) (transfer none):
 * @type:
 * @error:
 *
 * Return Value: (allow-none) (transfer full):
 **/

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

static void
gwebkitjs_base_init_cb(gpointer ptr, JSGlobalContextRef jsctx,
                       JSObjectRef jsvalue)
{
    GType type;
    GWebKitJSContext *ctx;
    GWebKitJSBase *self;
    type = GPOINTER_TO_INT(ptr);
    ctx = gwebkitjs_context_new_from_context(jsctx);
    self = GWEBKITJS_BASE(gwebkitjs_value_new(type, ctx, jsvalue));
    JSObjectSetPrivate(jsvalue, self);
    if (g_atomic_int_compare_and_exchange(&self->priv->toggle_added,
                                          FALSE, TRUE)) {
        g_object_add_toggle_ref(G_OBJECT(self), gwebkitjs_base_toggle_cb,
                                NULL);
        g_object_unref(self);
    }
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

bool
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
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx);
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

JSValueRef
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
    ctx = gwebkitjs_context_new_from_context((JSGlobalContextRef)jsctx);
    if (G_UNLIKELY(!ctx)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
        return NULL;
    }
    name = gwebkitjs_util_dup_str(jsname);
    if (G_UNLIKELY(!name)) {
        gwebkitjs_util_make_jserror(jsctx, jserr, "GWebKitJSError",
                                    "Context Not Found.");
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
    if (priv->name)
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
    return define;
}

/**
 * gwebkitjs_base_get_jsclass: (skip)
 * @type:
 *
 * Return Value:
 **/
JSClassRef
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

void
gwebkitjs_base_set_name(GType type, const gchar *name)
{
    GWebKitJSBaseClass *klass;
    gwj_return_if_false(g_type_is_a(type, GWEBKITJS_TYPE_BASE));
    gwj_return_if_false(type != GWEBKITJS_TYPE_BASE);

    klass = g_type_class_ref(type);
    do {
        if (klass->priv->jsdefine.className)
            break;
        g_free(klass->priv->name);
        if (name)
            klass->priv->name = g_strdup(name);
        else
            klass->priv->name = NULL;
    } while(0);
    g_type_class_unref(klass);
}
