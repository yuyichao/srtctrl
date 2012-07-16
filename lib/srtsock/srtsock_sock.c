#include <srtsock_sock.h>
#include <srtsock_buff.h>
#include <string.h>
#include <stdio.h>

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

#if GLIB_CHECK_VERSION(2, 32, 0)
#  define __EMBED_GMUTEX 1
#else
#  define __EMBED_GMUTEX 0
#endif


#if !GLIB_CHECK_VERSION(2, 30, 0)
/* The following code is copied from glib2-2.32 */

#include <ffi.h>
static ffi_type*
value_to_ffi_type(const GValue *gvalue, gpointer *value, gint *enum_tmpval,
                  gboolean *tmpval_used)
{
    ffi_type *rettype = NULL;
    GType type = g_type_fundamental(G_VALUE_TYPE(gvalue));
    g_assert(type != G_TYPE_INVALID);

    if (enum_tmpval) {
        g_assert(tmpval_used != NULL);
        *tmpval_used = FALSE;
    }

    switch (type) {
    case G_TYPE_BOOLEAN:
    case G_TYPE_CHAR:
    case G_TYPE_INT:
        rettype = &ffi_type_sint;
        *value = (gpointer)&(gvalue->data[0].v_int);
        break;
    case G_TYPE_ENUM:
        /* enums are stored in v_long even though they are integers, which makes
         * marshalling through libffi somewhat complicated.  They need to be
         * marshalled as signed ints, but we need to use a temporary int sized
         * value to pass to libffi otherwise it'll pull the wrong value on
         * BE machines with 32-bit integers when treating v_long as 32-bit int.
         */
        g_assert(enum_tmpval != NULL);
        rettype = &ffi_type_sint;
        *enum_tmpval = g_value_get_enum(gvalue);
        *value = enum_tmpval;
        *tmpval_used = TRUE;
        break;
    case G_TYPE_UCHAR:
    case G_TYPE_UINT:
    case G_TYPE_FLAGS:
        rettype = &ffi_type_uint;
        *value = (gpointer)&(gvalue->data[0].v_uint);
        break;
    case G_TYPE_STRING:
    case G_TYPE_OBJECT:
    case G_TYPE_BOXED:
    case G_TYPE_PARAM:
    case G_TYPE_POINTER:
    case G_TYPE_INTERFACE:
    case G_TYPE_VARIANT:
        rettype = &ffi_type_pointer;
        *value = (gpointer)&(gvalue->data[0].v_pointer);
        break;
    case G_TYPE_FLOAT:
        rettype = &ffi_type_float;
        *value = (gpointer)&(gvalue->data[0].v_float);
        break;
    case G_TYPE_DOUBLE:
        rettype = &ffi_type_double;
        *value = (gpointer)&(gvalue->data[0].v_double);
        break;
    case G_TYPE_LONG:
        rettype = &ffi_type_slong;
        *value = (gpointer)&(gvalue->data[0].v_long);
        break;
    case G_TYPE_ULONG:
        rettype = &ffi_type_ulong;
        *value = (gpointer)&(gvalue->data[0].v_ulong);
        break;
    case G_TYPE_INT64:
        rettype = &ffi_type_sint64;
        *value = (gpointer)&(gvalue->data[0].v_int64);
        break;
    case G_TYPE_UINT64:
        rettype = &ffi_type_uint64;
        *value = (gpointer)&(gvalue->data[0].v_uint64);
        break;
    default:
        rettype = &ffi_type_pointer;
        *value = NULL;
        g_warning("value_to_ffi_type: Unsupported fundamental type: %s",
                  g_type_name (type));
        break;
    }
    return rettype;
}

static void
value_from_ffi_type(GValue *gvalue, gpointer *value)
{
    ffi_arg *int_val = (ffi_arg*)value;

    switch (g_type_fundamental(G_VALUE_TYPE(gvalue))) {
    case G_TYPE_INT:
        g_value_set_int(gvalue, (gint)*int_val);
        break;
    case G_TYPE_FLOAT:
        g_value_set_float(gvalue, *(gfloat*)value);
        break;
    case G_TYPE_DOUBLE:
        g_value_set_double(gvalue, *(gdouble*)value);
        break;
    case G_TYPE_BOOLEAN:
        g_value_set_boolean(gvalue, (gboolean)*int_val);
        break;
    case G_TYPE_STRING:
        g_value_set_string(gvalue, *(gchar**)value);
        break;
    case G_TYPE_CHAR:
        g_value_set_char(gvalue, (gint8)*int_val);
        break;
    case G_TYPE_UCHAR:
        g_value_set_uchar(gvalue, (guchar)*int_val);
        break;
    case G_TYPE_UINT:
        g_value_set_uint(gvalue, (guint)*int_val);
        break;
    case G_TYPE_POINTER:
        g_value_set_pointer(gvalue, *(gpointer*)value);
        break;
    case G_TYPE_LONG:
        g_value_set_long(gvalue, (glong)*int_val);
        break;
    case G_TYPE_ULONG:
        g_value_set_ulong(gvalue, (gulong)*int_val);
        break;
    case G_TYPE_INT64:
        g_value_set_int64(gvalue, (gint64)*int_val);
        break;
    case G_TYPE_UINT64:
        g_value_set_uint64(gvalue, (guint64)*int_val);
        break;
    case G_TYPE_BOXED:
        g_value_set_boxed(gvalue, *(gpointer*)value);
        break;
    case G_TYPE_ENUM:
        g_value_set_enum(gvalue, (gint)*int_val);
        break;
    case G_TYPE_FLAGS:
        g_value_set_flags(gvalue, (guint)*int_val);
        break;
    case G_TYPE_PARAM:
        g_value_set_param(gvalue, *(gpointer*)value);
        break;
    case G_TYPE_OBJECT:
        g_value_set_object(gvalue, *(gpointer*)value);
        break;
    case G_TYPE_VARIANT:
        g_value_set_variant(gvalue, *(gpointer*)value);
        break;
    default:
        g_warning("value_from_ffi_type: Unsupported fundamental type: %s",
                  g_type_name(g_type_fundamental(G_VALUE_TYPE(gvalue))));
    }
}

static void
g_cclosure_marshal_generic(GClosure *closure, GValue *return_gvalue,
                           guint n_param_values, const GValue *param_values,
                           gpointer invocation_hint, gpointer marshal_data)
{
    ffi_type *rtype;
    void *rvalue;
    int n_args;
    ffi_type **atypes;
    void **args;
    int i;
    ffi_cif cif;
    GCClosure *cc = (GCClosure*)closure;
    gint *enum_tmpval;
    gboolean tmpval_used = FALSE;

    enum_tmpval = g_alloca (sizeof (gint));
    if (return_gvalue && G_VALUE_TYPE(return_gvalue)) {
        rtype = value_to_ffi_type(return_gvalue, &rvalue,
                                  enum_tmpval, &tmpval_used);
    } else {
        rtype = &ffi_type_void;
    }

    rvalue = g_alloca(MAX(rtype->size, sizeof(ffi_arg)));

    n_args = n_param_values + 1;
    atypes = g_alloca(sizeof(ffi_type*) * n_args);
    args =  g_alloca(sizeof(gpointer) * n_args);

    if (tmpval_used)
        enum_tmpval = g_alloca(sizeof(gint));

    if (G_CCLOSURE_SWAP_DATA(closure)) {
        atypes[n_args-1] = value_to_ffi_type(param_values + 0,
                                             &args[n_args-1],
                                             enum_tmpval,
                                             &tmpval_used);
        atypes[0] = &ffi_type_pointer;
        args[0] = &closure->data;
    } else {
        atypes[0] = value_to_ffi_type(param_values + 0,
                                      &args[0],
                                      enum_tmpval,
                                      &tmpval_used);
        atypes[n_args-1] = &ffi_type_pointer;
        args[n_args-1] = &closure->data;
    }

    for (i = 1; i < n_args - 1; i++) {
        if (tmpval_used)
            enum_tmpval = g_alloca(sizeof(gint));

        atypes[i] = value_to_ffi_type(param_values + i,
                                      &args[i],
                                      enum_tmpval,
                                      &tmpval_used);
    }

    if (ffi_prep_cif(&cif, FFI_DEFAULT_ABI, n_args, rtype, atypes) != FFI_OK)
        return;

    ffi_call(&cif, marshal_data ? marshal_data : cc->callback, rvalue, args);

    if (return_gvalue && G_VALUE_TYPE (return_gvalue))
        value_from_ffi_type(return_gvalue, rvalue);
}
#endif

struct _SrtSockSockPrivate {
    GSocket *sock;

    GSocketConnection *conn;

    GSource *out_src;
    GSource *in_src;
    GSource *err_src;

    SrtSockBuff *send_buff;

#if __EMBED_GMUTEX
    GMutex out_src_lock;
    GMutex in_src_lock;
    GMutex send_lock;
#else
    GMutex *out_src_lock;
    GMutex *in_src_lock;
    GMutex *send_lock;
#endif

    GSocketFamily family;
    GSocketType type;
    GSocketProtocol protocol;
    gint fd;

    gboolean sending :1;
    gboolean sync_sending :1;
    gboolean listening :1;
    gboolean receiving :1;
};

#define SRTSOCK_SOCK_IS_VALID(_ctx)             \
    ({                                          \
        SrtSockSock *__ctx = (_ctx);            \
        __ctx && SRTSOCK_IS_SOCK(__ctx) &&      \
            srtsock_sock_get_sock(__ctx, NULL); \
    })

enum {
    SIGNAL_ACCEPT,
    SIGNAL_RECEIVE,
    SIGNAL_DISCONN,
    SIGNAL_LAST,
};

enum
{
    PROP_0,
    PROP_FAMILY,
    PROP_TYPE,
    PROP_PROTOCOL,
    PROP_FD,
    /* PROP_BLOCKING, */
    /* PROP_LISTEN_BACKLOG, */
    /* PROP_KEEPALIVE, */
    /* PROP_LOCAL_ADDRESS, */
    /* PROP_REMOTE_ADDRESS, */
    /* PROP_TIMEOUT, */
    /* PROP_TTL, */
    /* PROP_BROADCAST, */
    /* PROP_MULTICAST_LOOPBACK, */
    /* PROP_MULTICAST_TTL */
};

static guint sock_signals[SIGNAL_LAST] = { 0 };

/**
 * Declarations
 **/
static void _srtsock_sock_init(SrtSockSock *self,
                               SrtSockSockClass *klass);
static void srtsock_sock_class_init(SrtSockSockClass *klass,
                                    gpointer data);
static void srtsock_sock_dispose(GObject *obj);
static void srtsock_sock_finalize(GObject *obj);
static gboolean srtsock_sock_update_in_src(SrtSockSock *self);
static gboolean srtsock_sock_update_out_src(SrtSockSock *self);
static gboolean srtsock_sock_add_err_src(SrtSockSock *self, gboolean on);
static GSocket *srtsock_sock_get_sock(SrtSockSock *self, GError **error);
/**
 * GObject Functions.
 **/
GType
srtsock_sock_get_type()
{
    static GType sock_type = 0;
    if (G_UNLIKELY(!sock_type)) {
        const GTypeInfo sock_info = {
            .class_size = sizeof(SrtSockSockClass),
            .base_init = NULL,
            .base_finalize = NULL,
            .class_init = (GClassInitFunc)srtsock_sock_class_init,
            .class_finalize = NULL,
            .class_data = NULL,
            .instance_size = sizeof(SrtSockSock),
            .n_preallocs = 0,
            .instance_init = (GInstanceInitFunc)_srtsock_sock_init,
            .value_table = NULL,
        };
        sock_type = g_type_register_static(G_TYPE_OBJECT,
                                           "SrtSockSock",
                                           &sock_info, 0);
    }
    return sock_type;
}

static void
_srtsock_sock_init(SrtSockSock *self, SrtSockSockClass *klass)
{
    SrtSockSockPrivate *priv;
    priv = self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                                    SRTSOCK_TYPE_SOCK,
                                                    SrtSockSockPrivate);
    priv->sock = NULL;
    priv->conn = NULL;
    priv->out_src = NULL;
    priv->in_src = NULL;
    priv->send_buff = srtsock_buff_new();
#if __EMBED_GMUTEX
    g_mutex_init(&priv->send_lock);
    g_mutex_init(&priv->in_src_lock);
    g_mutex_init(&priv->out_src_lock);
#else
    priv->send_lock = g_mutex_new();
    priv->in_src_lock = g_mutex_new();
    priv->out_src_lock = g_mutex_new();
#endif
    priv->sending = FALSE;
    priv->sync_sending = FALSE;
    priv->listening = FALSE;
    priv->receiving = FALSE;
    priv->family = G_SOCKET_FAMILY_INVALID;
    priv->type = G_SOCKET_TYPE_INVALID;
    priv->protocol = G_SOCKET_PROTOCOL_UNKNOWN;
    priv->fd = -1;
}

static gboolean
srtsock_sock_break_accum(GSignalInvocationHint *ihint, GValue *ret_v,
                         const GValue *handler_ret_v, gpointer p)
{
    gboolean handler_ret;
    handler_ret = g_value_get_boolean(handler_ret_v);
    if (handler_ret) {
        if (ret_v)
            g_value_set_boolean(ret_v, TRUE);
        return FALSE;
    } else {
        if (ret_v)
            g_value_set_boolean(ret_v, FALSE);
        return TRUE;
    }
}

static void
srtsock_sock_get_property(GObject *obj, guint prop_id, GValue *value,
                          GParamSpec *pspec)
{
    SrtSockSock *self = SRTSOCK_SOCK(obj);
    SrtSockSockPrivate *priv = self->priv;
    GSocket *sock = priv->sock;

    switch (prop_id) {
    case PROP_FAMILY:
        if (!sock)
            g_value_set_enum(value, priv->family);
        g_value_set_enum(value, g_socket_get_family(sock));
        break;
    case PROP_TYPE:
        if (!sock)
            g_value_set_enum(value, priv->type);
        g_value_set_enum(value, g_socket_get_socket_type(sock));
        break;
    case PROP_PROTOCOL:
        if (!sock)
            g_value_set_enum(value, priv->protocol);
        g_value_set_enum(value, g_socket_get_protocol(sock));
        break;
    case PROP_FD:
        if (!sock)
            g_value_set_int(value, priv->fd);
        g_value_set_int(value, g_socket_get_fd(sock));
        break;
    default:
        G_OBJECT_WARN_INVALID_PROPERTY_ID (obj, prop_id, pspec);
    }
}

static void
srtsock_sock_set_property(GObject *obj, guint prop_id, const GValue *value,
                          GParamSpec *pspec)
{
    SrtSockSock *self;
    self = SRTSOCK_SOCK(obj);
    if (self->priv->sock) {
        return;
    }
    switch (prop_id) {
    case PROP_FAMILY:
        self->priv->family = g_value_get_enum(value);
        break;
    case PROP_TYPE:
        self->priv->type = g_value_get_enum(value);
        break;
    case PROP_PROTOCOL:
        self->priv->protocol = g_value_get_enum(value);
        break;
    case PROP_FD:
        self->priv->fd = g_value_get_int(value);
        if (self->priv->fd >= 0)
            srtsock_sock_get_sock(self, NULL);
        break;
    default:
        G_OBJECT_WARN_INVALID_PROPERTY_ID (obj, prop_id, pspec);
    }
}

static void
srtsock_sock_class_init(SrtSockSockClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(SrtSockSockPrivate));
    gobject_class->dispose = srtsock_sock_dispose;
    gobject_class->finalize = srtsock_sock_finalize;
    gobject_class->set_property = srtsock_sock_set_property;
    gobject_class->get_property = srtsock_sock_get_property;
    g_object_class_install_property(
        gobject_class, PROP_FAMILY,
        g_param_spec_enum("family", "Socket family",
                          "The sockets address family",
                          G_TYPE_SOCKET_FAMILY,
                          G_SOCKET_FAMILY_INVALID,
                          G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));
    g_object_class_install_property(
        gobject_class, PROP_TYPE,
        g_param_spec_enum("type", "Socket type", "The sockets type",
                          G_TYPE_SOCKET_TYPE, G_SOCKET_TYPE_INVALID,
                          G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));
    g_object_class_install_property(
        gobject_class, PROP_PROTOCOL,
        g_param_spec_enum("protocol", "Socket protocol",
                          "The id of the protocol to use, or -1 for unknown",
                          G_TYPE_SOCKET_PROTOCOL, G_SOCKET_PROTOCOL_UNKNOWN,
                          G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));
    g_object_class_install_property(
        gobject_class, PROP_FD,
        g_param_spec_int("fd", "File descriptor", "The sockets file descriptor",
                         G_MININT, G_MAXINT, -1,
                         G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));
    /**
     * SrtSockSock::accept:
     * @sock: (transfer none) (allow-none):
     * @conn: (transfer none) (allow-none):
     *
     * Returns:
     **/
    sock_signals[SIGNAL_ACCEPT] = g_signal_new("accept", SRTSOCK_TYPE_SOCK,
                                               G_SIGNAL_RUN_LAST, 0,
                                               srtsock_sock_break_accum, NULL,
                                               g_cclosure_marshal_generic,
                                               G_TYPE_BOOLEAN, 1,
                                               SRTSOCK_TYPE_SOCK);
    /**
     * SrtSockSock::receive:
     * @sock: (transfer none) (allow-none):
     * @data: (transfer none) (allow-none):
     *
     * Returns:
     **/
    sock_signals[SIGNAL_RECEIVE] = g_signal_new("receive", SRTSOCK_TYPE_SOCK,
                                                G_SIGNAL_RUN_LAST, 0,
                                                srtsock_sock_break_accum,
                                                NULL,
                                                g_cclosure_marshal_generic,
                                                G_TYPE_BOOLEAN, 1,
                                                G_TYPE_OBJECT);
    /**
     * SrtSockSock::disconn:
     * @sock: (transfer none) (allow-none):
     *
     * Returns:
     **/
    sock_signals[SIGNAL_DISCONN] = g_signal_new("disconn", SRTSOCK_TYPE_SOCK,
                                                G_SIGNAL_RUN_LAST, 0,
                                                NULL, NULL,
                                                g_cclosure_marshal_VOID__VOID,
                                                G_TYPE_NONE, 0);
}

static void
srtsock_sock_dispose(GObject *obj)
{
    SrtSockSock *self = SRTSOCK_SOCK(obj);
    SrtSockSockPrivate *priv = self->priv;
    if (priv->sock) {
        g_socket_close(priv->sock, NULL);
        g_object_unref(priv->sock);
        priv->sock = NULL;
    }
    if (priv->conn) {
        g_object_unref(priv->conn);
        priv->conn = NULL;
    }
    if (priv->out_src) {
        g_source_unref(priv->out_src);
        priv->out_src = NULL;
    }
    if (priv->in_src) {
        g_source_unref(priv->in_src);
        priv->in_src = NULL;
    }
    if (priv->err_src) {
        g_source_unref(priv->err_src);
        priv->err_src = NULL;
    }
    if (priv->send_buff) {
        srtsock_buff_free(priv->send_buff);
        priv->send_buff = NULL;
    }
}

static void
srtsock_sock_finalize(GObject *obj)
{
    SrtSockSock *self = SRTSOCK_SOCK(obj);
#if __EMBED_GMUTEX
    g_mutex_clear(&self->priv->send_lock);
    g_mutex_clear(&self->priv->in_src_lock);
    g_mutex_clear(&self->priv->out_src_lock);
#else
    g_mutex_free(self->priv->send_lock);
    g_mutex_free(self->priv->in_src_lock);
    g_mutex_free(self->priv->out_src_lock);
#endif
}

static GSocket*
srtsock_sock_get_sock(SrtSockSock *self, GError **error)
{
    SrtSockSockPrivate *priv;
    priv = self->priv;
    if (priv->sock)
        return priv->sock;
    if (priv->fd > 0) {
        priv->sock = g_socket_new_from_fd(priv->fd, error);
        return priv->sock;
    }
    if (priv->family == G_SOCKET_FAMILY_INVALID)
        priv->family = G_SOCKET_FAMILY_IPV4;
    if (priv->type == G_SOCKET_TYPE_INVALID)
        priv->type = G_SOCKET_TYPE_STREAM;
    if (priv->protocol == G_SOCKET_PROTOCOL_UNKNOWN)
        priv->protocol = G_SOCKET_PROTOCOL_DEFAULT;
    priv->sock = g_socket_new(priv->family, priv->type, priv->protocol, error);
    return priv->sock;
}

/**
 * srtsock_sock_new:
 * @family:
 * @type:
 * @protocol:
 * @error:
 *
 * Returns: (transfer full) (allow-none):
 **/
SrtSockSock*
srtsock_sock_new(GSocketFamily family, GSocketType type,
                 GSocketProtocol protocol, GError **error)
{
    SrtSockSock *self;
    self = g_object_new(SRTSOCK_TYPE_SOCK, "family", family,
                        "type", type, "protocol", protocol, NULL);
    if (!srtsock_sock_get_sock(self, error)) {
        g_object_unref(self);
        return NULL;
    }
    return self;
}

/**
 * srtsock_sock_new_from_fd:
 * @fd:
 * @error:
 *
 * Returns: (transfer full) (allow-none):
 **/
SrtSockSock*
srtsock_sock_new_from_fd(int fd, GError **error)
{
    SrtSockSock *self;
    self = g_object_new(SRTSOCK_TYPE_SOCK, "fd", fd, NULL);
    if (!srtsock_sock_get_sock(self, error)) {
        g_object_unref(self);
        return NULL;
    }
    srtsock_sock_add_err_src(self, TRUE);
    return self;
}

static SrtSockSock*
srtsock_sock_new_from_sock_with_type(GType type, GSocket *sock)
{
    SrtSockSock *self;
    g_return_val_if_fail(g_type_is_a(type, SRTSOCK_TYPE_SOCK), NULL);
    g_return_val_if_fail(G_IS_SOCKET(sock), NULL);
    self = g_object_new(type, NULL);
    g_return_val_if_fail(self, NULL);
    self->priv->sock = g_object_ref(sock);
    if (!self->priv->sock) {
        g_object_unref(self);
        return NULL;
    }
    if (g_socket_is_connected(sock))
        srtsock_sock_add_err_src(self, TRUE);
    return self;
}

/**
 * srtsock_sock_new_from_sock:
 * @sock: (transfer none) (allow-none):
 *
 * Returns: (transfer full) (allow-none):
 **/
/* static SrtSockSock* */
/* srtsock_sock_new_from_sock(GSocket *sock) */
/* { */
/*     return srtsock_sock_new_from_sock_with_type(SRTSOCK_TYPE_SOCK, sock); */
/* } */

static GSocketConnection*
srtsock_sock_get_connection(SrtSockSock *self)
{
    SrtSockSockPrivate *priv;
    GSocket *sock;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), NULL);
    sock = srtsock_sock_get_sock(self, NULL);
    g_return_val_if_fail(sock, NULL);
    priv = self->priv;
    if (priv->conn)
        return priv->conn;
    priv->conn = g_socket_connection_factory_create_connection(sock);
    return priv->conn;
}

typedef enum {
    _POLL_IN,
    _POLL_OUT,
    _POLL_ERR,
} PollErrSrc;

static void
srtsock_sock_on_poll_err(SrtSockSock *self, GIOCondition cond, PollErrSrc src)
{
    /* Hopefully good enough? */
    srtsock_sock_close(self, NULL);
}

static gboolean
srtsock_sock_err_cb(GSocket *gsock, GIOCondition cond, SrtSockSock *self)
{
    srtsock_sock_on_poll_err(self, cond, _POLL_IN);
    return TRUE;
}

static gboolean
srtsock_sock_add_err_src(SrtSockSock *self, gboolean on)
{
    SrtSockSockPrivate *priv;
    priv = self->priv;
    if (on) {
        if (priv->err_src)
            return TRUE;
        priv->err_src = g_socket_create_source(priv->sock, G_IO_ERR | G_IO_HUP |
                                               G_IO_NVAL, NULL);
        if (!priv->err_src)
            return FALSE;
        g_source_set_callback(priv->err_src,
                              (GSourceFunc)srtsock_sock_err_cb,
                              g_object_ref(self), g_object_unref);
        g_source_attach(priv->err_src, g_main_context_get_thread_default());
        g_source_unref(priv->err_src);
    } else {
        GSource *old_src;
        if (!priv->err_src)
            return TRUE;
        old_src = priv->err_src;
        priv->err_src = NULL;
        g_source_destroy(old_src);
    }
    return TRUE;
}

static gboolean
srtsock_sock_io_err_ok(gint code)
{
    return (code == G_IO_ERROR_CANCELLED ||
            code == G_IO_ERROR_PENDING ||
            code == G_IO_ERROR_TIMED_OUT ||
            code == G_IO_ERROR_WOULD_BLOCK);
}

static gboolean
srtsock_sock_in_cb(GSocket *gsock, GIOCondition cond, SrtSockSock *self)
{
    if (cond & (G_IO_ERR | G_IO_HUP | G_IO_NVAL)) {
        srtsock_sock_on_poll_err(self, cond, _POLL_IN);
        return TRUE;
    } else if (cond & (G_IO_IN | G_IO_PRI)) {
        if (self->priv->listening) {
            /* Since there is no g_socket_accept_with_blocking(), there is a
             * rare condition in which this function can be blocking.
             */
            GSocket *ngsock;
            GError *error = NULL;
            g_socket_set_blocking(gsock, FALSE);
            ngsock = g_socket_accept(gsock, NULL, &error);
            if (ngsock) {
                SrtSockSock *nsock;
                nsock = srtsock_sock_new_from_sock_with_type(
                    G_TYPE_FROM_INSTANCE(self), ngsock);
                g_object_unref(ngsock);
                if (nsock) {
                    gboolean handled;
                    srtsock_sock_add_err_src(nsock, TRUE);
                    g_signal_emit(self, sock_signals[SIGNAL_ACCEPT], 0,
                                  nsock, &handled);
                    g_object_unref(nsock);
                }
            } else {
                if (error) {
                    if (!srtsock_sock_io_err_ok(error->code))
                        srtsock_sock_close(self, NULL);
                    g_error_free(error);
                }
            }
        }
        if (self->priv->receiving) {
            guint rsize;
            gchar buff[65536];
            GError *error = NULL;
            rsize = g_socket_receive_with_blocking(self->priv->sock, buff,
                                                   65536, FALSE, NULL, &error);
            if (rsize > 0) {
                GObject *obj;
                obj = srtsock_obj_from_buff(rsize, buff);
                if (obj) {
                    gboolean handled;
                    g_signal_emit(self, sock_signals[SIGNAL_RECEIVE], 0,
                                  obj, &handled);
                    g_object_unref(obj);
                }
            } else if (!rsize) {
                srtsock_sock_close(self, NULL);
            } else {
                if (error) {
                    if (!srtsock_sock_io_err_ok(error->code))
                        srtsock_sock_close(self, NULL);
                    g_error_free(error);
                }
            }
        }
        srtsock_sock_update_in_src(self);
    } else {
        return FALSE;
    }
    return TRUE;
}

static gboolean
_srtsock_sock_update_in_src(SrtSockSock *self, gboolean on)
{
    SrtSockSockPrivate *priv;

    priv = self->priv;
    if (on) {
        if (priv->in_src)
            return TRUE;
        priv->in_src = g_socket_create_source(priv->sock, G_IO_IN |
                                              G_IO_ERR | G_IO_HUP |
                                              G_IO_NVAL, NULL);
        if (!priv->in_src)
            return FALSE;
        g_source_set_callback(priv->in_src,
                              (GSourceFunc)srtsock_sock_in_cb,
                              g_object_ref(self), g_object_unref);
        g_source_attach(priv->in_src, g_main_context_get_thread_default());
        g_source_unref(priv->in_src);
    } else {
        GSource *old_src;
        if (!priv->in_src)
            return TRUE;
        old_src = priv->in_src;
        priv->in_src = NULL;
        g_source_destroy(old_src);
    }
    return TRUE;
}

static gboolean
srtsock_sock_update_in_src(SrtSockSock *self)
{
    gboolean res;
    srtsock_sock_get_sock(self, NULL);
#if __EMBED_GMUTEX
    g_mutex_lock(&self->priv->in_src_lock);
#else
    g_mutex_lock(self->priv->in_src_lock);
#endif
    res = _srtsock_sock_update_in_src(self, self->priv->listening ||
                                      self->priv->receiving);
#if __EMBED_GMUTEX
    g_mutex_unlock(&self->priv->in_src_lock);
#else
    g_mutex_unlock(self->priv->in_src_lock);
#endif
    return res;
}

static gboolean
srtsock_sock_out_cb(GSocket *gsock, GIOCondition cond, SrtSockSock *self)
{
    if (cond & (G_IO_ERR | G_IO_HUP | G_IO_NVAL)) {
        srtsock_sock_on_poll_err(self, cond, _POLL_OUT);
        return TRUE;
    } else if (cond & (G_IO_OUT)) {
        if (!
#if __EMBED_GMUTEX
            g_mutex_trylock(&self->priv->send_lock)
#else
            g_mutex_trylock(self->priv->send_lock)
#endif
            ) {
            srtsock_sock_update_out_src(self);
            return TRUE;
        }
        gssize rsize;
        guint size = 0;
        gchar *buff = NULL;
        GError *error = NULL;
        buff = srtsock_buff_get(self->priv->send_buff, &size);
        rsize = g_socket_send_with_blocking(gsock, buff, size, FALSE,
                                            NULL, &error);
        if (rsize > 0) {
            srtsock_buff_pop(self->priv->send_buff, rsize);
        } else {
            srtsock_buff_pop(self->priv->send_buff, 0);
            if (buff)
                srtsock_sock_close(self, NULL);
            if (error) {
                if (!srtsock_sock_io_err_ok(error->code))
                    srtsock_sock_close(self, NULL);
                g_error_free(error);
            }
        }
        srtsock_sock_update_out_src(self);
#if __EMBED_GMUTEX
        g_mutex_unlock(&self->priv->send_lock);
#else
        g_mutex_unlock(self->priv->send_lock);
#endif
    } else {
        return FALSE;
    }
    return TRUE;
}

static gboolean
_srtsock_sock_update_out_src(SrtSockSock *self, gboolean on)
{
    SrtSockSockPrivate *priv;

    priv = self->priv;
    if (on) {
        if (priv->out_src)
            return TRUE;
        priv->out_src = g_socket_create_source(priv->sock, G_IO_OUT | G_IO_ERR |
                                               G_IO_HUP | G_IO_NVAL, NULL);
        if (!priv->out_src)
            return FALSE;
        g_source_set_callback(priv->out_src,
                              (GSourceFunc)srtsock_sock_out_cb,
                              g_object_ref(self), g_object_unref);
        g_source_attach(priv->out_src, g_main_context_get_thread_default());
        g_source_unref(priv->out_src);
    } else {
        GSource *old_src;
        if (!priv->out_src)
            return TRUE;
        old_src = priv->out_src;
        priv->out_src = NULL;
        g_source_destroy(old_src);
    }
    return TRUE;
}

static gboolean
srtsock_sock_update_out_src(SrtSockSock *self)
{
    gboolean res;
    SrtSockSockPrivate *priv;
    srtsock_sock_get_sock(self, NULL);
    priv = self->priv;
#if __EMBED_GMUTEX
    g_mutex_lock(&priv->out_src_lock);
#else
    g_mutex_lock(priv->out_src_lock);
#endif
    res = _srtsock_sock_update_out_src(self, priv->sending &&
                                       !priv->sync_sending &&
                                       !srtsock_buff_empty(priv->send_buff));
#if __EMBED_GMUTEX
    g_mutex_unlock(&priv->out_src_lock);
#else
    g_mutex_unlock(priv->out_src_lock);
#endif
    return res;
}

/**
 * srtsock_sock_accept:
 * @self: (transfer none) (allow-none):
 * @error: (allow-none):
 *
 * Returns: (allow-none) (transfer full):
 **/
SrtSockSock*
srtsock_sock_accept(SrtSockSock *self, GError **error)
{
    SrtSockSock *nsock;
    GSocket *ngsock;
    GError *ierror = NULL;
    GSocket *sock;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), NULL);
    sock = srtsock_sock_get_sock(self, error);
    g_return_val_if_fail(sock, NULL);
    if (!g_socket_listen(sock, &ierror)) {
        if (ierror) {
            if (!srtsock_sock_io_err_ok(ierror->code))
                srtsock_sock_close(self, NULL);
            if (error)
                *error = ierror;
            else
                g_error_free(ierror);
        }
        return NULL;
    }
    if (ierror) {
        g_error_free(ierror);
        ierror = NULL;
    }
    g_socket_set_blocking(sock, TRUE);
    ngsock = g_socket_accept(sock, NULL, &ierror);
    if (ierror) {
        if (!srtsock_sock_io_err_ok(ierror->code))
            srtsock_sock_close(self, NULL);
        if (error)
            *error = ierror;
        else
            g_error_free(ierror);
    }
    if (!ngsock) {
        return NULL;
    }
    nsock = srtsock_sock_new_from_sock_with_type(G_TYPE_FROM_INSTANCE(self),
                                                 ngsock);
    if (nsock)
        srtsock_sock_add_err_src(nsock, TRUE);
    g_object_unref(ngsock);
    return nsock;
}

/** srtsock_sock_start_accept:
 * @self: (transfer none) (allow-none):
 *
 * Returns:
 **/
gboolean
srtsock_sock_start_accept(SrtSockSock *self)
{
    gboolean res;
    GSocket *sock;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    sock = srtsock_sock_get_sock(self, NULL);
    g_return_val_if_fail(sock, FALSE);
    if (!g_socket_listen(sock, NULL))
        return FALSE;
    self->priv->listening = TRUE;
    res = srtsock_sock_update_in_src(self);
    return res;
}

/** srtsock_sock_stop_accept:
 * @self: (transfer none) (allow-none):
 **/
void
srtsock_sock_stop_accept(SrtSockSock *self)
{
    g_return_if_fail(SRTSOCK_SOCK_IS_VALID(self));
    self->priv->listening = FALSE;
    srtsock_sock_update_in_src(self);
}

/**
 * srtsock_sock_bind:
 * @self: (transfer none) (allow-none):
 * @addr: (transfer none) (allow-none):
 * @error: (allow-none):
 **/
gboolean
srtsock_sock_bind(SrtSockSock *self, GSocketAddress *addr,
                  gboolean allow_reuse, GError **error)
{
    gboolean res;
    GSocket *sock;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    sock = srtsock_sock_get_sock(self, error);
    g_return_val_if_fail(sock, FALSE);
    res = g_socket_bind(sock, addr, allow_reuse, error);
    if (res)
        srtsock_sock_add_err_src(self, TRUE);
    return res;
}

/**
 * srtsock_sock_close:
 * @self: (transfer none) (allow-none):
 * @error:
 *
 * Returns:
 **/
gboolean
srtsock_sock_close(SrtSockSock *self, GError **error)
{
    gboolean res;
    SrtSockSockPrivate *priv;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), TRUE);
    priv = self->priv;
    priv->listening = FALSE;
    priv->sending = FALSE;
    priv->receiving = FALSE;
    srtsock_sock_update_in_src(self);
    srtsock_sock_update_out_src(self);
    srtsock_sock_add_err_src(self, FALSE);
    if (priv->send_buff) {
        srtsock_buff_free(priv->send_buff);
        priv->send_buff = NULL;
    }
    res = g_socket_close(priv->sock, error);
    g_signal_emit(self, sock_signals[SIGNAL_DISCONN], 0);
    return res;
}

/**
 * srtsock_sock_conn:
 * @self: (transfer none) (allow-none):
 * @addr: (transfer none) (allow-none):
 * @error: (allow-none):
 *
 * Returns:
 **/
gboolean
srtsock_sock_conn(SrtSockSock *self, GSocketAddress *addr, GError **error)
{
    GSocketConnection *conn;
    gboolean res;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    conn = srtsock_sock_get_connection(self);
    g_return_val_if_fail(conn, FALSE);
    res = g_socket_connection_connect(conn, addr, NULL, error);
    if (res)
        srtsock_sock_add_err_src(self, TRUE);
    return res;
}

/**
 * srtsock_sock_conn_async:
 * @self: (transfer none) (allow-none):
 * @addr: (transfer none) (allow-none):
 * @callback: (scope async) (closure user_data):
 * @user_data: (closure):
 **/
gboolean
srtsock_sock_conn_async(SrtSockSock *self, GSocketAddress *addr,
                        GAsyncReadyCallback callback, gpointer user_data)
{
    GSocketConnection *conn;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    conn = srtsock_sock_get_connection(self);
    g_return_val_if_fail(conn, FALSE);
    g_socket_connection_connect_async(conn, addr, NULL, callback, user_data);
    return TRUE;
}

/**
 * srtsock_sock_conn_finish:
 * @self: (transfer none) (allow-none):
 * @result: (transfer none) (allow-none):
 * @error:
 *
 * Returns:
 **/
gboolean
srtsock_sock_conn_finish(SrtSockSock *self, GAsyncResult *result,
                         GError **error)
{
    GSocketConnection *conn;
    gboolean res;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    conn = srtsock_sock_get_connection(self);
    g_return_val_if_fail(conn, FALSE);
    res = g_socket_connection_connect_finish(conn, result, error);
    if (res)
        srtsock_sock_add_err_src(self, TRUE);
    return res;
}

/**
 * srtsock_sock_get_local_address:
 * @self: (transfer none) (allow-none):
 * @error:
 *
 * Returns: (transfer full) (allow-none):
 **/
GSocketAddress*
srtsock_sock_get_local_address(SrtSockSock *self, GError **error)
{
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    return g_socket_get_local_address(self->priv->sock, error);
}

/**
 * srtsock_sock_get_family:
 * @self: (transfer none) (allow-none):
 *
 * Returns:
 **/
GSocketFamily
srtsock_sock_get_family(SrtSockSock *self)
{
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), G_SOCKET_FAMILY_INVALID);
    return g_socket_get_family(self->priv->sock);
}

/**
 * srtsock_sock_get_remote_address:
 * @self: (transfer none) (allow-none):
 * @error:
 *
 * Returns: (transfer full) (allow-none):
 **/
GSocketAddress*
srtsock_sock_get_remote_address(SrtSockSock *self, GError **error)
{
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    return g_socket_get_remote_address(self->priv->sock, error);
}

/**
 * srtsock_sock_recv:
 * @self: (transfer none) (allow-none):
 * @size:
 * @rsize: (out) (allow-none):
 * @error:
 *
 * Returns: (array length=rsize) (element-type guint8) (allow-none) (transfer full):
 **/
gchar*
srtsock_sock_recv(SrtSockSock *self, gsize size, gssize *rsize, GError **error)
{
    gchar *buff;
    GError *ierror = NULL;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    g_return_val_if_fail(rsize, NULL);
    buff = g_malloc0(size);
    *rsize = g_socket_receive_with_blocking(self->priv->sock, buff, size,
                                            TRUE, NULL, &ierror);
    if (!*rsize) {
        g_free(buff);
        srtsock_sock_close(self, NULL);
        return NULL;
    } else if (*rsize < 0) {
        *rsize = 0;
        g_free(buff);
        if (ierror) {
            if (!srtsock_sock_io_err_ok(ierror->code))
                srtsock_sock_close(self, NULL);
            if (error)
                *error = ierror;
            else
                g_error_free(ierror);
        }
        return NULL;
    }
    buff = g_realloc(buff, *rsize);
    return buff;
}

gboolean
srtsock_sock_start_recv(SrtSockSock *self)
{
    gboolean res;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), FALSE);
    self->priv->receiving = TRUE;
    res = srtsock_sock_update_in_src(self);
    return res;
}

void
srtsock_sock_stop_recv(SrtSockSock *self)
{
    g_return_if_fail(SRTSOCK_SOCK_IS_VALID(self));
    self->priv->receiving = FALSE;
    srtsock_sock_update_in_src(self);
}

/**
 * srtsock_sock_send:
 * @self: (transfer none) (allow-none):
 * @buff: (transfer none) (allow-none) (array length=size) (element-type guint8):
 * @size:
 **/
void
srtsock_sock_send(SrtSockSock *self, const gchar *buff, gsize size)
{
    g_return_if_fail(SRTSOCK_IS_SOCK(self));
    srtsock_buff_push(self->priv->send_buff, buff, size);
    srtsock_sock_update_out_src(self);
}

/**
 * srtsock_sock_start_send:
 * @self: (transfer none) (allow-none):
 **/
gboolean
srtsock_sock_start_send(SrtSockSock *self)
{
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), FALSE);
    self->priv->sending = TRUE;
    srtsock_sock_update_out_src(self);
    return TRUE;
}

/**
 * srtsock_sock_stop_send:
 * @self: (transfer none) (allow-none):
 **/
void
srtsock_sock_stop_send(SrtSockSock *self)
{
    g_return_if_fail(SRTSOCK_SOCK_IS_VALID(self));
    self->priv->sending = FALSE;
    srtsock_sock_update_out_src(self);
}

/**
 * srtsock_sock_wait_send:
 * @self: (transfer none) (allow-none):
 *
 * Returns:
 **/
gboolean
srtsock_sock_wait_send(SrtSockSock *self, GError **error)
{
    gssize rsize;
    guint size = 0;
    gchar *buff = NULL;
    gboolean res = TRUE;
    SrtSockSockPrivate *priv;

    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), FALSE);

    priv = self->priv;
    priv->sync_sending = TRUE;
    srtsock_sock_update_out_src(self);
#if __EMBED_GMUTEX
    g_mutex_lock(&priv->send_lock);
#else
    g_mutex_lock(priv->send_lock);
#endif
    do {
        buff = srtsock_buff_get(priv->send_buff, &size);
        if (!buff) {
            res = TRUE;
            break;
        }
        rsize = g_socket_send_with_blocking(priv->sock, buff, size, TRUE,
                                            NULL, error);
        if (rsize > 0) {
            srtsock_buff_pop(priv->send_buff, rsize);
        } else {
            srtsock_buff_pop(priv->send_buff, 0);
            res = FALSE;
            break;
        }
    } while (1);
#if __EMBED_GMUTEX
    g_mutex_unlock(&self->priv->send_lock);
#else
    g_mutex_unlock(self->priv->send_lock);
#endif
    priv->sync_sending = FALSE;
    srtsock_sock_update_out_src(self);
    return res;
}

/**
 * srtsock_sock_shutdown:
 * @self: (transfer none) (allow-none):
 * @read:
 * @write:
 * @error:
 *
 * Returns:
 **/
gboolean
srtsock_sock_shutdown(SrtSockSock *self, gboolean read, gboolean write,
                      GError **error)
{
    gboolean res;
    SrtSockSockPrivate *priv;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), TRUE);
    priv = self->priv;
    priv->listening = FALSE;
    priv->sending = FALSE;
    priv->receiving = FALSE;
    srtsock_sock_update_in_src(self);
    srtsock_sock_update_out_src(self);
    srtsock_sock_add_err_src(self, FALSE);
    if (priv->send_buff) {
        srtsock_buff_free(priv->send_buff);
        priv->send_buff = NULL;
    }
    res = g_socket_shutdown(priv->sock, read, write, error);
    g_signal_emit(self, sock_signals[SIGNAL_DISCONN], 0);
    return res;
}

/**
 * srtsock_buff_from_obj:
 * @obj: (transfer none) (allow-none):
 * @len: (out) (allow-none):
 *
 * Returns: (transfer none) (allow-none) (array length=len) (element-type guint8):
 **/
gchar*
srtsock_buff_from_obj(GObject *obj, guint *len)
{
    gchar *res;
    g_return_val_if_fail(len, NULL);
    g_return_val_if_fail(G_IS_OBJECT(obj), NULL);
    res = g_object_get_data(obj, "_buff_");
    *len = GPOINTER_TO_UINT(g_object_get_data(obj, "_length_"));
    return res;
}

/**
 * srtsock_obj_from_buff:
 * @len: (out) (allow-none):
 * @buff: (transfer none) (allow-none) (array length=len) (element-type guint8):
 *
 * Returns: (transfer none) (allow-none):
 **/
GObject*
srtsock_obj_from_buff(guint len, gchar *buff)
{
    GObject *obj;
    gchar *nbuff;
    g_return_val_if_fail(len && buff, NULL);
    obj = g_object_new(G_TYPE_OBJECT, NULL);
    g_return_val_if_fail(obj, NULL);

    nbuff = g_malloc0(len);
    memcpy(nbuff, buff, len);
    g_object_set_data_full(obj, "_buff_", nbuff, (GDestroyNotify)g_free);
    g_object_set_data(obj, "_length_", GUINT_TO_POINTER(len));
    return obj;
}
