#include <webkit/webkitwebview.h>
#include <gwebkitjs_helper.h>
#include <gwebkitjs_context.h>
#include <gwebkitjs_value.h>

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

struct _GWebKitJSHelperPrivate {
    WebKitWebView *webview;
    gulong win_obj_clear_id;
};

static void gwebkitjs_helper_init(GWebKitJSHelper *self,
                                  GWebKitJSHelperClass *klass);
static void gwebkitjs_helper_class_init(GWebKitJSHelperClass *klass,
                                        gpointer data);
static void gwebkitjs_helper_dispose(GObject *obj);
static void gwebkitjs_helper_finalize(GObject *obj);

enum {
    SIGNAL_WINDOW_OBJECT_CLEARED,
    _SIGNAL_LAST
};

static guint signals[_SIGNAL_LAST] = {0};

GType
gwebkitjs_helper_get_type()
{
    static GType helper_type = 0;
    if (G_UNLIKELY(helper_type == 0)) {
        const GTypeInfo helper_info = {
            .class_size = sizeof(GWebKitJSHelperClass),
            .base_init = NULL,
            .base_finalize = NULL,
            .class_init = (GClassInitFunc)gwebkitjs_helper_class_init,
            .class_finalize = NULL,
            .class_data = NULL,
            .instance_size = sizeof(GWebKitJSHelper),
            .n_preallocs = 0,
            .instance_init = (GInstanceInitFunc)gwebkitjs_helper_init,
            .value_table = NULL,
        };

        helper_type = g_type_register_static(G_TYPE_OBJECT, "GWebKitJSHelper",
                                             &helper_info, 0);
    }
    return helper_type;
}

static void
gwebkitjs_helper_init(GWebKitJSHelper *self, GWebKitJSHelperClass *klass)
{
    GWebKitJSHelperPrivate *priv;
    priv = self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                                    GWEBKITJS_TYPE_HELPER,
                                                    GWebKitJSHelperPrivate);
    priv->webview = NULL;
    priv->win_obj_clear_id = 0;
}

static void
gwebkitjs_helper_class_init(GWebKitJSHelperClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(GWebKitJSHelperPrivate));
    gobject_class->dispose = gwebkitjs_helper_dispose;
    gobject_class->finalize = gwebkitjs_helper_finalize;
    /**
     * GWebKitJSHelper::window-object-cleared:
     * @helper: (transfer none) (allow-none):
     * @frame: (transfer none) (allow-none):
     * @ctx: (transfer none) (allow-none):
     * @win_obj: (transfer none) (allow-none):
     **/
    signals[SIGNAL_WINDOW_OBJECT_CLEARED] =
        g_signal_new("window-object-cleared", GWEBKITJS_TYPE_HELPER,
                     G_SIGNAL_RUN_LAST, 0, NULL, NULL, NULL, G_TYPE_NONE, 3,
                     WEBKIT_TYPE_WEB_FRAME, GWEBKITJS_TYPE_CONTEXT,
                     GWEBKITJS_TYPE_VALUE);
}

static void
gwebkitjs_helper_dispose(GObject *obj)
{
    GWebKitJSHelper *self = GWEBKITJS_HELPER(obj);
    if (self->priv->webview) {
        if (self->priv->win_obj_clear_id) {
            g_signal_handler_disconnect(self->priv->webview,
                                        self->priv->win_obj_clear_id);
            self->priv->win_obj_clear_id = 0;
        }
        g_object_unref(self->priv->webview);
        self->priv->webview = NULL;
    }
}

static void
gwebkitjs_helper_finalize(GObject *obj)
{
    /* GWebKitJSHelper *self = GWEBKITJS_HELPER(obj); */
}

static void
gwebkitjs_helper_window_object_cleared_cb(WebKitWebView *webview,
                                          WebKitWebFrame *frame,
                                          JSGlobalContextRef jsctx,
                                          JSObjectRef jsobj,
                                          GWebKitJSHelper *self)
{
    GWebKitJSContext *ctx;
    GWebKitJSValue *value;
    ctx = gwebkitjs_context_new_from_context(jsctx);
    gwj_return_if_false(ctx);
    value = gwebkitjs_value_new(GWEBKITJS_TYPE_VALUE, ctx, jsobj);
    if (G_UNLIKELY(!value)) {
        g_object_unref(ctx);
        return;
    }
    g_signal_emit(self, signals[SIGNAL_WINDOW_OBJECT_CLEARED], 0,
                  frame, ctx, value);
}

/**
 * gwebkitjs_helper_new:
 * webview: (allow-none) (transfer none):
 *
 * Returns: (allow-none) (transfer full):
 **/
GWebKitJSHelper*
gwebkitjs_helper_new(WebKitWebView *webview)
{
    GWebKitJSHelper *self;
    gwj_return_val_if_false(WEBKIT_IS_WEB_VIEW(webview), NULL);
    self = g_object_new(GWEBKITJS_TYPE_HELPER, NULL);
    self->priv->webview = g_object_ref(webview);
    self->priv->win_obj_clear_id = g_signal_connect(
        webview, "window-object-cleared",
        G_CALLBACK(gwebkitjs_helper_window_object_cleared_cb), self);
    printf("connection id: %lu\n", self->priv->win_obj_clear_id);
    return self;
}
