#include <gwebkitjs_util.h>
#include <JavaScriptCore/JSValueRef.h>
#include <JavaScriptCore/JSStringRef.h>

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

/**
 * gwebkitjs_util_dup_str: (skip)
 **/
gchar*
gwebkitjs_util_dup_str(JSStringRef jsstr)
{
    char *str = NULL;
    gint l;
    gwj_return_val_if_false(jsstr, NULL);
    l = JSStringGetMaximumUTF8CStringSize(jsstr);
    if (l > 0) {
        gchar *buf;
        buf = g_malloc0((l + 1) * sizeof(gchar));
        JSStringGetUTF8CString(jsstr, buf, l + 1);
        str = g_strdup(buf);
        g_free(buf);
    }
    return str;
}

/**
 * gwebkitjs_util_convert_str: (skip)
 **/
gchar*
gwebkitjs_util_convert_str(JSStringRef jsstr)
{
    gchar *str;
    gwj_return_val_if_false(jsstr, NULL);
    str = gwebkitjs_util_dup_str(jsstr);
    JSStringRelease(jsstr);
    return str;
}

/**
 * gwebkitjs_util_value_to_str: (skip)
 **/
gchar*
gwebkitjs_util_value_to_str(JSContextRef ctx, JSValueRef jsvalue)
{
    JSStringRef jsstr;
    gwj_return_val_if_false(ctx && jsvalue, NULL);

    jsstr = JSValueToStringCopy(ctx, jsvalue, NULL);
    return gwebkitjs_util_convert_str(jsstr);
}

/**
 * gwebkitjs_util_make_str: (skip)
 **/
JSValueRef
gwebkitjs_util_make_str(JSContextRef ctx, const char *str)
{
    JSValueRef jsvalue;
    JSStringRef jsstr;
    gwj_return_val_if_false(ctx && str, NULL);

    jsstr = JSStringCreateWithUTF8CString(str);
    gwj_return_val_if_false(jsstr, NULL);
    jsvalue = JSValueMakeString(ctx, jsstr);
    JSStringRelease(jsstr);

    return jsvalue;
}

/**
 * gwebkitjs_util_jserror_get_name: (skip)
 **/
gchar*
gwebkitjs_util_jserror_get_name(JSContextRef ctx, JSValueRef jserror)
{
    JSValueRef jsname;
    jsname = gwebkitjs_util_get_property(ctx, jserror, "name", NULL);
    return gwebkitjs_util_value_to_str(ctx, jsname);
}

/**
 * gwebkitjs_util_jserror_get_message: (skip)
 **/
gchar*
gwebkitjs_util_jserror_get_message(JSContextRef ctx, JSValueRef jserror)
{
    JSValueRef jsname;
    jsname = gwebkitjs_util_get_property(ctx, jserror, "message", NULL);
    return gwebkitjs_util_value_to_str(ctx, jsname);
}

/**
 * gwebkitjs_util_gerror_from_jserror: (skip)
 **/
void
gwebkitjs_util_gerror_from_jserror(JSContextRef ctx, JSValueRef jserror,
                                   GError **error)
{
    gchar *name;
    gchar *msg;
    GQuark domain;
    gwj_return_if_false(ctx);
    gwj_return_if_false(jserror);
    gwj_return_if_false(error);

    name = gwebkitjs_util_jserror_get_name(ctx, jserror);
    msg = gwebkitjs_util_jserror_get_message(ctx, jserror);
    gwj_return_if_false(name || msg);
    domain = g_quark_from_string(name ? name : "Error");
    g_free(name);
    *error = g_error_new_literal(domain, 0, msg ? msg : "");
    g_free(msg);
}

/**
 * gwebkitjs_util_make_jserror: (skip)
 **/
void
gwebkitjs_util_make_jserror(JSContextRef ctx, JSValueRef *jserror,
                            const gchar *name, const gchar *msg)
{
    JSValueRef jsname;
    JSValueRef jsmsg;

    gwj_return_if_false(ctx && jserror);

    if (!(name || msg)) {
        *jserror = NULL;
        return;
    }

    if (msg) {
        jsmsg = gwebkitjs_util_make_str(ctx, msg);
        if (jsmsg)
            *jserror = JSObjectMakeError(ctx, 1, &jsmsg, NULL);
        else
            *jserror = JSObjectMakeError(ctx, 0, NULL, NULL);
    } else {
        *jserror = JSObjectMakeError(ctx, 0, NULL, NULL);
    }

    gwj_return_if_false(*jserror);

    if (name) {
        jsname = gwebkitjs_util_make_str(ctx, name);
        if (jsname)
            gwebkitjs_util_set_property(ctx, *jserror, "name", jsname,
                                        GWEBKITJS_PROPERTY_ATTRIBUTE_NONE,
                                        NULL);
    }
}

/**
 * gwebkitjs_util_jserror_from_gerror: (skip)
 **/
void
gwebkitjs_util_jserror_from_gerror(JSContextRef ctx, JSValueRef *jserror,
                                   GError *error)
{
    const gchar *name = NULL;
    const gchar *msg = NULL;

    if (error) {
        name = g_quark_to_string(error->domain);
        msg = error->message;
    }
    gwebkitjs_util_make_jserror(ctx, jserror, name, msg);
}

/**
 * gwebkitjs_util_get_property: (skip)
 **/
JSValueRef
gwebkitjs_util_get_property(JSContextRef ctx, JSValueRef self,
                            const gchar *name, GError **error)
{
    JSStringRef jsname;
    JSValueRef jserror = NULL;
    JSValueRef res;
    JSObjectRef jsobject;
    gwj_return_val_if_false(ctx && self && name, NULL);
    jsobject = JSValueToObject(ctx, self, &jserror);
    if (!jsobject) {
        gwebkitjs_util_gerror_from_jserror(ctx, jserror, error);
        return NULL;
    }
    jsname = JSStringCreateWithUTF8CString(name);
    gwj_return_val_if_false(jsname, NULL);
    res = JSObjectGetProperty(ctx, jsobject, jsname, &jserror);
    JSStringRelease(jsname);
    if (res)
        jserror = NULL;
    gwebkitjs_util_gerror_from_jserror(ctx, jserror, error);
    return res;
}

/**
 * gwebkitjs_util_set_property: (skip)
 **/
void
gwebkitjs_util_set_property(JSContextRef ctx, JSValueRef self,
                            const gchar *name, JSValueRef prop,
                            GWebKitJSPropertyAttribute prop_attr,
                            GError **error)
{
    JSStringRef jsname;
    JSValueRef jserror = NULL;
    JSObjectRef jsobject;
    gwj_return_if_false(ctx && self && name && prop);
    jsobject = JSValueToObject(ctx, self, &jserror);
    if (!jsobject) {
        gwebkitjs_util_gerror_from_jserror(ctx, jserror, error);
        return;
    }
    jsname = JSStringCreateWithUTF8CString(name);
    gwj_return_if_false(jsname);
    JSObjectSetProperty(ctx, jsobject, jsname, prop, prop_attr, &jserror);
    JSStringRelease(jsname);
    gwebkitjs_util_gerror_from_jserror(ctx, jserror, error);
}
