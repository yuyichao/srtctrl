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
 * Return Value: (allow-none) (transfer none):
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
            .base_init = NULL,
            .base_finalize = (GBaseInitFunc)gwebkitjs_base_base_init,
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
    gwebkitjs_base_get_jsclass(klass);
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
gwebkitjs_base_init_cb(gpointer ptr, JSGlobalContextRef jsctx,
                       JSObjectRef jsvalue)
{
    GType type;
    GWebKitJSContext *ctx;
    GWebKitJSValue *value;
    type = GPOINTER_TO_INT(ptr);
    ctx = gwebkitjs_context_new_from_context(jsctx);
    value = gwebkitjs_value_new(type, ctx, jsvalue);
    JSObjectSetPrivate(jsvalue, value);
}

static JSClassDefinition*
gwebkitjs_base_get_definition(GWebKitJSBaseClass *klass)
{
    GWebKitJSBaseClass *pklass;
    JSClassRef pjsclass;
    JSClassDefinition *define;
    gwj_return_val_if_false(GWEBKITJS_IS_BASE_CLASS(klass), NULL);
    if (klass->priv->jsdefine.className)
        return &klass->priv->jsdefine;

    define = &klass->priv->jsdefine;
    pklass = g_type_class_peek_parent(klass);
    pjsclass = gwebkitjs_base_get_jsclass(pklass);
    define->version = 0;
    define->attributes = kJSClassAttributeNone;
    define->parentClass = pjsclass;
    if (klass->priv->name)
        define->className = klass->priv->name;
    else
        define->className = "GWebKitJS";
    klass->priv->init_clsr = gwebkitjs_closure_create(
        clsr_type_v_p_p, G_CALLBACK(gwebkitjs_base_init_cb),
        GINT_TO_POINTER(G_TYPE_FROM_CLASS(klass)));
    define->initialize =
        (JSObjectInitializeCallback)klass->priv->init_clsr->func;
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
