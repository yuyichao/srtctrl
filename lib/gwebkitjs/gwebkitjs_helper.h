#ifndef __GWEBKITJS_HELPER_H__
#define __GWEBKITJS_HELPER_H__

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
#include <gwebkitjs_context.h>

#define GWEBKITJS_TYPE_HELPER (gwebkitjs_helper_get_type())
#define GWEBKITJS_HELPER(obj)                                  \
    (G_TYPE_CHECK_INSTANCE_CAST((obj), GWEBKITJS_TYPE_HELPER,  \
                                GWebKitJSHelper))
#define GWEBKITJS_IS_HELPER(obj)                                \
    (G_TYPE_CHECK_INSTANCE_TYPE((obj), GWEBKITJS_TYPE_HELPER))
#define GWEBKITJS_HELPER_CLASS(klass)                          \
    (G_TYPE_CHECK_CLASS_CAST((klass), GWEBKITJS_TYPE_HELPER,   \
                             GWebKitJSHelperClass))
#define GWEBKITJS_IS_HELPER_CLASS(klass)                        \
    (G_TYPE_CHECK_CLASS_TYPE((klass), GWEBKITJS_TYPE_HELPER))
#define GWEBKITJS_HELPER_GET_CLASS(obj)                        \
    (G_TYPE_INSTANCE_GET_CLASS((obj), GWEBKITJS_TYPE_HELPER,   \
                               GWebKitJSHelperClass))

typedef struct _GWebKitJSHelper GWebKitJSHelper;
typedef struct _GWebKitJSHelperPrivate GWebKitJSHelperPrivate;
typedef struct _GWebKitJSHelperClass GWebKitJSHelperClass;

struct _GWebKitJSHelper {
    GObject parent;
    GWebKitJSHelperPrivate *priv;
};

struct _GWebKitJSHelperClass {
    GObjectClass parent_class;
};

#ifdef __cplusplus
extern "C" {
#endif
    GType gwebkitjs_helper_get_type();
    GWebKitJSHelper *gwebkitjs_helper_new(WebKitWebView *webview);
    WebKitWebView *gwebkitjs_helper_get_view(GWebKitJSHelper *self);
    GWebKitJSContext *gwebkitjs_helper_get_context(GWebKitJSHelper *self);
    GWebKitJSValue *gwebkitjs_helper_get_global(GWebKitJSHelper *self);
#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_HELPER_H__ */
