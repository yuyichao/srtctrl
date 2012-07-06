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

struct _SrtSockSockPrivate {
    GSocket *sock;

    GSocketConnection *conn;

    GSource *out_src;
    GMutex out_src_lock;
    GSource *in_src;
    GMutex in_src_lock;
    GSource *err_src;

    SrtSockBuff *send_buff;
    GMutex send_lock;

    gboolean sending :1;
    gboolean sync_sending :1;
    gboolean listening :1;
    gboolean receiving :1;
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
static void _srtsock_sock_init(SrtSockSock *self,
                              SrtSockSockClass *klass);
static void srtsock_sock_class_init(SrtSockSockClass *klass,
                                    gpointer data);
static void srtsock_sock_dispose(GObject *obj);
static void srtsock_sock_finalize(GObject *obj);
static gboolean srtsock_sock_update_in_src(SrtSockSock *self);
static gboolean srtsock_sock_update_out_src(SrtSockSock *self);
static gboolean srtsock_sock_add_err_src(SrtSockSock *self, gboolean on);

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
    g_mutex_init(&priv->send_lock);
    g_mutex_init(&priv->in_src_lock);
    g_mutex_init(&priv->out_src_lock);
    priv->sending = FALSE;
    priv->sync_sending = FALSE;
    priv->listening = FALSE;
    priv->receiving = FALSE;
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
    g_mutex_clear(&self->priv->send_lock);
    g_mutex_clear(&self->priv->in_src_lock);
    g_mutex_clear(&self->priv->out_src_lock);
}

/**
 * _srtsock_sock_new:
 * Returns: (transfer full):
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
 * Returns: (transfer full) (allow-none):
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
 * srtsock_sock_init:
 * @self: (transfer none) (allow-none):
 * @family:
 * @type:
 * @protocol:
 * @error:
 **/
void
srtsock_sock_init(SrtSockSock *self, GSocketFamily family, GSocketType type,
                  GSocketProtocol protocol, GError **error)
{
    GSocket *sock;
    sock = g_socket_new(family, type, protocol, error);
    if (!sock)
        return;
    srtsock_sock_init_from_sock(self, sock);
    g_object_unref(sock);
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
    GSocket *sock = g_socket_new_from_fd(fd, error);
    if (G_UNLIKELY(!sock))
        return NULL;
    self = srtsock_sock_new_from_sock(sock);
    srtsock_sock_add_err_src(self, TRUE);
    g_object_unref(sock);
    return self;
}

/**
 * srtsock_sock_init_from_fd:
 * @self: (transfer none) (allow-none):
 * @fd:
 * @error:
 **/
void
srtsock_sock_init_from_fd(SrtSockSock *self, int fd, GError **error)
{
    GSocket *sock = g_socket_new_from_fd(fd, error);
    if (G_UNLIKELY(!sock))
        return;
    srtsock_sock_init_from_sock(self, sock);
    srtsock_sock_add_err_src(self, TRUE);
    g_object_unref(sock);
}

/**
 * srtsock_sock_new_from_sock:
 * @sock: (transfer none) (allow-none):
 *
 * Returns: (transfer full) (allow-none):
 **/
SrtSockSock*
srtsock_sock_new_from_sock(GSocket *sock)
{
    SrtSockSock *self;
    g_return_val_if_fail(G_IS_SOCKET(sock), NULL);
    self = _srtsock_sock_new();
    srtsock_sock_init_from_sock(self, sock);
    return self;
}

/**
 * srtsock_sock_init_from_sock:
 * @self: (transfer none) (allow-none):
 * @sock: (transfer none) (allow-none):
 **/
void
srtsock_sock_init_from_sock(SrtSockSock *self, GSocket *sock)
{
    g_return_if_fail(SRTSOCK_IS_SOCK(self));
    g_return_if_fail(G_IS_SOCKET(sock));
    g_return_if_fail(!self->priv->sock);
    g_object_ref(sock);
    self->priv->sock = sock;
    if (g_socket_is_connected(sock))
        srtsock_sock_add_err_src(self, TRUE);
}

/**
 * srtsock_sock_new_from_conn:
 * @conn: (transfer none) (allow-none):
 *
 * Returns: (transfer full) (allow-none):
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

/**
 * srtsock_sock_init_from_conn:
 * @self: (transfer none) (allow-none):
 * @conn: (transfer none) (allow-none):
 **/
void
srtsock_sock_init_from_conn(SrtSockSock *self, GSocketConnection *conn)
{
    GSocket *sock;
    g_return_if_fail(G_IS_SOCKET_CONNECTION(conn));
    g_return_if_fail(!self->priv->conn);
    sock = g_socket_connection_get_socket(conn);
    srtsock_sock_init_from_sock(self, sock);
    self->priv->conn = g_object_ref(conn);
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
                nsock = srtsock_sock_new_from_sock(ngsock);
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
            rsize = g_socket_receive_with_blocking(self->priv->sock, buff,
                                                   65536, FALSE, NULL, NULL);
            if (rsize > 0) {
                GObject *obj;
                obj = srtsock_obj_from_buff(rsize, buff);
                if (obj) {
                    gboolean handled;
                    g_signal_emit(self, sock_signals[SIGNAL_RECEIVE], 0,
                                  obj, &handled);
                    g_object_unref(obj);
                }
            } else {
                srtsock_sock_close(self, NULL);
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
    g_mutex_lock(&self->priv->in_src_lock);
    res = _srtsock_sock_update_in_src(self, self->priv->listening ||
                                      self->priv->receiving);
    g_mutex_unlock(&self->priv->in_src_lock);
    return res;
}

static gboolean
srtsock_sock_out_cb(GSocket *gsock, GIOCondition cond, SrtSockSock *self)
{
    if (cond & (G_IO_ERR | G_IO_HUP | G_IO_NVAL)) {
        srtsock_sock_on_poll_err(self, cond, _POLL_OUT);
        return TRUE;
    } else if (cond & (G_IO_OUT)) {
        if (!g_mutex_trylock(&self->priv->send_lock)) {
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
        g_mutex_unlock(&self->priv->send_lock);
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
    priv = self->priv;
    g_mutex_lock(&priv->out_src_lock);
    res = _srtsock_sock_update_out_src(self, priv->sending &&
                                       !priv->sync_sending &&
                                       !srtsock_buff_empty(priv->send_buff));
    g_mutex_unlock(&priv->out_src_lock);
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
    SrtSockSockPrivate *priv;
    GSocket *ngsock;
    GError *ierror = NULL;

    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    priv = self->priv;
    if (!g_socket_listen(priv->sock, &ierror)) {
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
    g_socket_set_blocking(priv->sock, TRUE);
    ngsock = g_socket_accept(priv->sock, NULL, &ierror);
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
    nsock = srtsock_sock_new_from_sock(ngsock);
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
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), FALSE);
    if (!g_socket_listen(self->priv->sock, NULL))
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
    SrtSockSockPrivate *priv;
    gboolean res;
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), FALSE);
    priv = self->priv;
    res = g_socket_bind(priv->sock, addr, allow_reuse, error);
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
    if (G_UNLIKELY(!conn))
        return FALSE;
    res = g_socket_connection_connect(conn, addr, NULL, error);
    if (res)
        srtsock_sock_add_err_src(self, TRUE);
    return res;
}

/**
 * srtsock_sock_conn_async:
 * @self: (transfer none) (allow-none):
 * @addr: (transfer none) (allow-none):
 * @cb: (scope async):
 * @p: (closure):
 **/
gboolean
srtsock_sock_conn_async(SrtSockSock *self, GSocketAddress *addr,
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
    if (G_UNLIKELY(!conn))
        return FALSE;
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
    g_return_val_if_fail(SRTSOCK_SOCK_IS_VALID(self), NULL);
    g_return_val_if_fail(rsize, NULL);
    buff = g_malloc0(size);
    *rsize = g_socket_receive_with_blocking(self->priv->sock, buff, size,
                                            TRUE, NULL, error);
    if (*rsize < 0) {
        *rsize = 0;
        g_free(buff);
        srtsock_sock_close(self, NULL);
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
    g_mutex_lock(&priv->send_lock);
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
    g_mutex_unlock(&self->priv->send_lock);
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
