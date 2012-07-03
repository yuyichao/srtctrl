#include <srtsock_sock.h>
#include <srtsock_buff.h>
#include <string.h>

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

struct _SrtSockSockPrivate {
    GSocket *sock;

    GSocketConnection *conn;
    GSocketListener *listener;
    GSource *send_src;
    SrtSockBuff *send_buff;
    GMutex send_lock;
    GMutex src_lock;
    gboolean sending :1;
    gboolean listening :1;
};

#define SRTSOCK_SOCK_IS_VALID(_ctx)                     \
    ({                                                  \
        SrtSockSock *ctx = (_ctx);                      \
        ctx && SRTSOCK_IS_SOCK(ctx) && ctx->priv->sock; \
    })

enum {
    SIGNAL_ACCEPT,
    SIGNAL_RECEIVE,
    SIGNAL_DISCONN,
    SIGNAL_LAST,
};

static guint sock_signals[SIGNAL_LAST] = { 0 };

/**
 * Declarations
 **/
static void srtsock_sock_init(SrtSockSock *self,
                              SrtSockSockClass *klass);
static void srtsock_sock_class_init(SrtSockSockClass *klass,
                                    gpointer data);
static void srtsock_sock_dispose(GObject *obj);
static void srtsock_sock_finalize(GObject *obj);
static void srtsock_sock_free_connection(SrtSockSock *self);
static void srtsock_sock_free_listener(SrtSockSock *self);
static inline void
srtsock_clear_error(GError **error)
{
    if (error)
        *error = NULL;
}

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
            .instance_init = (GInstanceInitFunc)srtsock_sock_init,
            .value_table = NULL,
        };
        sock_type = g_type_register_static(G_TYPE_OBJECT,
                                           "SrtSockSock",
                                           &sock_info, 0);
    }
    return sock_type;
}

static void
srtsock_sock_init(SrtSockSock *self, SrtSockSockClass *klass)
{
    SrtSockSockPrivate *priv;
    priv = self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                                    SRTSOCK_TYPE_SOCK,
                                                    SrtSockSockPrivate);
    priv->sock = NULL;
    priv->conn = NULL;
    priv->listener = NULL;
    priv->send_buff = srtsock_buff_new();
    g_mutex_init(&priv->send_lock);
    g_mutex_init(&priv->src_lock);
    priv->sending = FALSE;
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
srtsock_sock_class_init(SrtSockSockClass *klass, gpointer data)
{
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    g_type_class_add_private(klass, sizeof(SrtSockSockPrivate));
    gobject_class->dispose = srtsock_sock_dispose;
    gobject_class->finalize = srtsock_sock_finalize;
    /**
     * SrtSockSock::accept:
     * @sock: (transfer none) (allow-none):
     * @conn: (transfer none) (allow-none):
     *
     * Return Value:
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
     * @size:
     * @data: (transfer none) (allow-none) (array length=size) (element-type gchar):
     *
     * Return Value:
     **/
    sock_signals[SIGNAL_RECEIVE] = g_signal_new("receive", SRTSOCK_TYPE_SOCK,
                                                G_SIGNAL_RUN_LAST, 0,
                                                srtsock_sock_break_accum,
                                                NULL,
                                                g_cclosure_marshal_generic,
                                                G_TYPE_BOOLEAN, 2,
                                                G_TYPE_INT, G_TYPE_POINTER);
    /**
     * SrtSockSock::disconn:
     * @sock: (transfer none) (allow-none):
     *
     * Return Value:
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
        g_object_unref(priv->sock);
        priv->sock = NULL;
    }
    srtsock_sock_free_connection(self);
    srtsock_sock_free_listener(self);
    if (priv->send_buff) {
        srtsock_buff_free(priv->send_buff);
        priv->send_buff = NULL;
    }
}

static void
srtsock_sock_finalize(GObject *obj)
{
    SrtSockSock *self = SRTSOCK_SOCK(obj);
    g_mutex_clear(&self->priv->send_lock);
    g_mutex_clear(&self->priv->src_lock);
}

/**
 * _srtsock_sock_new:
 * Return Value: (transfer full):
 **/
static SrtSockSock*
_srtsock_sock_new()
{
    return g_object_new(SRTSOCK_TYPE_SOCK, NULL);
}

/**
 * srtsock_sock_new:
 * @family:
 * @type:
 * @protocol:
 * @error:
 *
 * Return Value: (transfer full) (allow-none):
 **/
SrtSockSock*
srtsock_sock_new(GSocketFamily family, GSocketType type,
                 GSocketProtocol protocol, GError **error)
{
    SrtSockSock *self;
    GSocket *sock = g_socket_new(family, type, protocol, error);
    if (!sock)
        return NULL;
    self = srtsock_sock_new_from_sock(sock);
    g_object_unref(sock);
    return self;
}

/**
 * srtsock_sock_new_from_fd:
 * @fd:
 * @error:
 *
 * Return Value: (transfer full):
 **/
SrtSockSock*
srtsock_sock_new_from_fd(int fd, GError **error)
{
    SrtSockSock *self;
    GSocket *sock = g_socket_new_from_fd(fd, error);
    if (G_UNLIKELY(!sock))
        return NULL;
    self = srtsock_sock_new_from_sock(sock);
    g_object_unref(sock);
    return self;
}

/**
 * srtsock_sock_new_from_sock:
 * @sock: (transfer none):
 *
 * Return Value: (transfer full):
 **/
SrtSockSock*
srtsock_sock_new_from_sock(GSocket *sock)
{
    SrtSockSock *self;
    g_return_val_if_fail(G_IS_SOCKET(sock), NULL);
    self = _srtsock_sock_new();
    g_object_ref(sock);
    self->priv->sock = sock;
    return self;
}

/**
 * srtsock_sock_new_from_conn:
 * @conn: (transfer none):
 *
 * Return Value: (transfer full):
 **/
SrtSockSock*
srtsock_sock_new_from_conn(GSocketConnection *conn)
{
    SrtSockSock *self;
    g_return_val_if_fail(G_IS_SOCKET_CONNECTION(conn), NULL);
    GSocket *sock = g_socket_connection_get_socket(conn);
    self = srtsock_sock_new_from_sock(sock);
    self->priv->conn = g_object_ref(conn);
    return self;
}

static GSocketConnection*
srtsock_sock_get_connection(SrtSockSock *self)
{
    SrtSockSockPrivate *priv;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    priv = self->priv;
    if (priv->conn)
        return priv->conn;
    priv->conn = g_socket_connection_factory_create_connection(priv->sock);
    return priv->conn;
}

static void
srtsock_sock_free_connection(SrtSockSock *self)
{
    if (self->priv->conn) {
        g_object_unref(self->priv->conn);
        self->priv->conn = NULL;
    }
}

static gboolean
srtsock_sock_check_connect(SrtSockSock *self)
{
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), FALSE);
    if (!g_socket_is_connected(self->priv->sock)) {
        srtsock_sock_close(self, NULL);
        return FALSE;
    }
    return TRUE;
}

static GSocketListener*
srtsock_sock_get_listener(SrtSockSock *self)
{
    SrtSockSockPrivate *priv;
    gboolean res;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    priv = self->priv;
    if (priv->listener)
        return priv->listener;
    priv->listener = g_socket_listener_new();
    if (!priv->listener)
        return NULL;
    res = g_socket_listener_add_socket(priv->listener, priv->sock,
                                       G_OBJECT(self), NULL);
    if (!res)
        srtsock_sock_free_listener(self);
    return priv->listener;
}

static void
srtsock_sock_free_listener(SrtSockSock *self)
{
    SrtSockSockPrivate *priv = self->priv;
    if (priv->listener) {
        g_object_unref(priv->listener);
        priv->listener = NULL;
    }
}

/**
 * srtsock_sock_accept:
 * @self: (transfer none) (allow-none):
 * @error: (allow-none):
 *
 * Return Value: (allow-none) (transfer full):
 **/
SrtSockSock*
srtsock_sock_accept(SrtSockSock *self, GError **error)
{
    GSocketConnection *nconn;
    SrtSockSock *nsock;
    GSocketListener *listener;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    listener = srtsock_sock_get_listener(self);
    if (!listener)
        return NULL;
    nconn = g_socket_listener_accept(listener, NULL, NULL, error);
    if (!nconn) {
        srtsock_sock_check_connect(self);
        return NULL;
    }
    srtsock_clear_error(error);
    nsock = srtsock_sock_new_from_conn(nconn);
    g_object_unref(nconn);
    return nsock;
}

static void
srtsock_sock_accept_cb(GSocketListener *listener, GAsyncResult *async_res,
                       gpointer p)
{
    GSocketConnection *conn;
    SrtSockSock *self;
    SrtSockSock *nsock;
    GError *error;
    gboolean res;
    conn = g_socket_listener_accept_finish(listener, async_res,
                                           (GObject**)&self, &error);
    if (!conn) {
        srtsock_sock_check_connect(self);
        if (error)
            g_error_free(error);
        return;
    }
    nsock = srtsock_sock_new_from_conn(conn);
    g_object_unref(conn);
    g_signal_emit(self, sock_signals[SIGNAL_ACCEPT], 0, nsock, &res);
    g_object_unref(nsock);
    srtsock_sock_start_accept(self);
}

/** srtsock_sock_start_accept:
 * @self: (transfer none) (allow-none):
 **/
gboolean
srtsock_sock_start_accept(SrtSockSock *self)
{
    GSocketListener *listener;
    listener = srtsock_sock_get_listener(self);
    if (!listener) {
        srtsock_sock_check_connect(self);
        return FALSE;
    }
    g_socket_listener_accept_async(listener, NULL,
                                   (GAsyncReadyCallback)srtsock_sock_accept_cb,
                                   NULL);
    return TRUE;
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
    SrtSockSockPrivate *priv;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    priv = self->priv;
    if (!priv->sock)
        return FALSE;
    return g_socket_bind(priv->sock, addr, allow_reuse, error);
}

/**
 * srtsock_sock_close:
 * @self: (transfer none) (allow-none):
 * @error:
 *
 * Return Value:
 **/
gboolean
srtsock_sock_close(SrtSockSock *self, GError **error)
{
    gboolean res;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), TRUE);
    if (!self->priv->sock)
        return TRUE;
    res = g_socket_close(self->priv->sock, error);
    self->priv->sending = FALSE;
    srtsock_sock_free_connection(self);
    srtsock_sock_free_listener(self);
    g_signal_emit(self, sock_signals[SIGNAL_DISCONN], 0);
    return res;
}

/**
 * srtsock_sock_connect:
 * @self: (transfer none) (allow-none):
 * @addr: (transfer none) (allow-none):
 * @error: (allow-none):
 *
 * Return Value:
 **/
gboolean
srtsock_sock_connect(SrtSockSock *self, GSocketAddress *addr, GError **error)
{
    GSocketConnection *conn;
    gboolean res;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    conn = srtsock_sock_get_connection(self);
    if (G_UNLIKELY(!conn))
        return FALSE;
    res = g_socket_connection_connect(conn, addr, NULL, error);
    return res;
}

/**
 * srtsock_sock_connect_async:
 * @self: (transfer none) (allow-none):
 * @addr: (transfer none) (allow-none):
 * @cb: (scope async):
 * @p: (closure):
 **/
gboolean
srtsock_sock_connect_async(SrtSockSock *self, GSocketAddress *addr,
                           GAsyncReadyCallback cb, gpointer p)
{
    GSocketConnection *conn;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    conn = srtsock_sock_get_connection(self);
    if (G_UNLIKELY(!conn))
        return FALSE;
    g_socket_connection_connect_async(conn, addr, NULL, cb, p);
    return TRUE;
}

/**
 * srtsock_sock_connect_finish:
 * @self: (transfer none) (allow-none):
 * @result: (transfer none) (allow-none):
 * @error:
 *
 * Return Value:
 **/
gboolean
srtsock_sock_connect_finish(SrtSockSock *self, GAsyncResult *result,
                            GError **error)
{
    GSocketConnection *conn;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    conn = srtsock_sock_get_connection(self);
    if (G_UNLIKELY(!conn))
        return FALSE;
    return g_socket_connection_connect_finish(conn, result, error);
}

/**
 * srtsock_sock_get_local_address:
 * @self: (transfer none) (allow-none):
 * @error:
 *
 * Return Value: (transfer full) (allow-none):
 **/
GSocketAddress*
srtsock_sock_get_local_address(SrtSockSock *self, GError **error)
{
    GSocket *sock;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), NULL);

    sock = self->priv->sock;
    if (G_UNLIKELY(!sock))
        return NULL;
    return g_socket_get_local_address(sock, error);
}

/**
 * srtsock_sock_get_remote_address:
 * @self: (transfer none) (allow-none):
 * @error:
 *
 * Return Value: (transfer full) (allow-none):
 **/
GSocketAddress*
srtsock_sock_get_remote_address(SrtSockSock *self, GError **error)
{
    GSocket *sock;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), NULL);

    sock = self->priv->sock;
    if (G_UNLIKELY(!sock))
        return NULL;
    return g_socket_get_remote_address(sock, error);
}

/**
 * srtsock_sock_recv:
 * @self: (transfer none) (allow-none):
 * @size:
 * @rsize: (out):
 * @error:
 *
 * Return Value: (array length=rsize) (element-type gchar) (allow-none) (transfer full):
 **/
gchar*
srtsock_sock_recv(SrtSockSock *self, gsize size, gssize *rsize, GError **error)
{
    GSocketConnection *conn;
    GInputStream *istm;
    gchar *buff;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), NULL);
    g_return_val_if_fail(rsize, NULL);

    conn = srtsock_sock_get_connection(self);
    if (G_UNLIKELY(!conn))
        return NULL;
    istm = g_io_stream_get_input_stream(G_IO_STREAM(conn));

    buff = g_malloc0(size);
    *rsize = g_input_stream_read(istm, buff, size, NULL, error);
    if (*rsize < 0) {
        g_free(buff);
        srtsock_sock_check_connect(self);
        return NULL;
    }
    buff = g_realloc(buff, *rsize);
    return buff;
}

gboolean
srtsock_sock_start_recv(SrtSockSock *self, GError **error)
{
    /* TODO */
}

static void srtsock_sock_check_source(SrtSockSock *self);

static gboolean
srtsock_sock_send_cb(GSocket *gsock, GIOCondition cond, SrtSockSock *self)
{
    if (cond || (G_IO_ERR && G_IO_HUP && G_IO_NVAL)) {
        self->priv->sending = FALSE;
        srtsock_sock_check_source(self);
        srtsock_sock_close(self, NULL);
        return TRUE;
    }
    if (cond || G_IO_OUT) {
        if (!self->priv->sending) {
            srtsock_sock_check_source(self);
            return TRUE;
        }
        if (g_mutex_trylock(&self->priv->send_lock)) {
            gssize rsize;
            guint size = 0;
            gchar *buff = NULL;
            GError *error = NULL;
            buff = srtsock_buff_get(self->priv->send_buff, &size);
            g_socket_set_blocking(gsock, FALSE);
            rsize = g_socket_send(gsock, buff, size, NULL, &error);
            if (rsize >= 0) {
                srtsock_buff_pop(self->priv->send_buff, rsize);
            } else {
                srtsock_buff_pop(self->priv->send_buff, 0);
                if (error) {
                    g_error_free(error);
                }
            }
            srtsock_sock_check_connect(self);
            srtsock_sock_check_source(self);
            g_mutex_unlock(&self->priv->send_lock);
        }
        return TRUE;
    }
    return FALSE;
}

static void
srtsock_sock_check_source(SrtSockSock *self)
{
    SrtSockSockPrivate *priv;
    priv = self->priv;
    if (!priv->sock)
        return;
    g_mutex_lock(&priv->src_lock);
    if (priv->sending && !srtsock_buff_empty(priv->send_buff)) {
        if (!priv->send_src) {
            priv->send_src = g_socket_create_source(priv->sock,
                                                    G_IO_OUT, NULL);
            g_source_set_callback(priv->send_src,
                                  (GSourceFunc)srtsock_sock_send_cb,
                                  g_object_ref(self), g_object_unref);
            g_source_attach(priv->send_src, NULL);
            g_source_unref(priv->send_src);
        }
    } else {
        if (priv->send_src) {
            GSource *old_src;
            old_src = priv->send_src;
            priv->send_src = NULL;
            g_source_destroy(old_src);
        }
    }
    g_mutex_unlock(&self->priv->src_lock);
}

/**
 * srtsock_sock_send:
 * @self: (transfer none) (allow-none):
 * @buff: (transfer none) (allow-none) (array length=size) (element-type gchar):
 * @size:
 **/
void
srtsock_sock_send(SrtSockSock *self, const gchar *buff, gsize size)
{
    g_return_if_fail(SRTSOCK_IS_SOCK(self));
    srtsock_buff_push(self->priv->send_buff, buff, size);
}

/**
 * srtsock_sock_start_send:
 * @self: (transfer none) (allow-none):
 **/
void
srtsock_sock_start_send(SrtSockSock *self)
{
    g_return_if_fail(SRTSOCK_IS_SOCK(self));
    self->priv->sending = TRUE;
    srtsock_sock_check_source(self);
}

/**
 * srtsock_sock_stop_send:
 * @self: (transfer none) (allow-none):
 **/
void
srtsock_sock_stop_send(SrtSockSock *self)
{
    g_return_if_fail(SRTSOCK_IS_SOCK(self));
    self->priv->sending = FALSE;
    srtsock_sock_check_source(self);
}

/**
 * srtsock_sock_wait_send:
 * @self: (transfer none) (allow-none):
 *
 * Return Value:
 **/
gboolean
srtsock_sock_wait_send(SrtSockSock *self)
{
    gssize rsize;
    guint size = 0;
    gchar *buff = NULL;
    GError *error = NULL;
    gboolean res = TRUE;
    g_return_val_if_fail(SRTSOCK_IS_SOCK(self), FALSE);
    if (G_UNLIKELY(!self->priv->sock))
        return FALSE;
    g_mutex_lock(&self->priv->send_lock);
    do {
        buff = srtsock_buff_get(self->priv->send_buff, &size);
        if (!buff) {
            res = TRUE;
            break;
        }
        g_socket_set_blocking(self->priv->sock, TRUE);
        rsize = g_socket_send(self->priv->sock, buff, size, NULL, &error);
        if (rsize >= 0) {
            srtsock_buff_pop(self->priv->send_buff, rsize);
        } else {
            srtsock_buff_pop(self->priv->send_buff, 0);
            if (error) {
                g_error_free(error);
            }
        }
        if (!srtsock_sock_check_connect(self)) {
            res = FALSE;
            break;
        }
    } while (1);
    g_mutex_unlock(&self->priv->send_lock);
    srtsock_sock_check_source(self);
    return res;
}

/**
 * srtsock_sock_shutdown:
 * @self: (transfer none) (allow-none):
 * @read:
 * @write:
 * @error:
 *
 * Return Value:
 **/
gboolean
srtsock_sock_shutdown(SrtSockSock *self, gboolean read, gboolean write,
                      GError **error)
{
    gboolean res;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), TRUE);
    res = g_socket_shutdown(self->priv->sock, read, write, error);
    self->priv->sending = FALSE;
    srtsock_sock_free_connection(self);
    srtsock_sock_free_listener(self);
    g_signal_emit(self, sock_signals[SIGNAL_DISCONN], 0);
    return res;
}
