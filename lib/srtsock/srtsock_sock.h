#ifndef __SRTSOCK_SOCK_H__
#define __SRTSOCK_SOCK_H__

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
#include <gio/gio.h>

#define SRTSOCK_TYPE_SOCK (srtsock_sock_get_type())
#define SRTSOCK_SOCK(obj)                                  \
    (G_TYPE_CHECK_INSTANCE_CAST((obj), SRTSOCK_TYPE_SOCK,  \
                                SrtSockSock))
#define SRTSOCK_IS_SOCK(obj)                                    \
    (G_TYPE_CHECK_INSTANCE_TYPE((obj), SRTSOCK_TYPE_SOCK))
#define SRTSOCK_SOCK_CLASS(klass)                          \
    (G_TYPE_CHECK_CLASS_CAST((klass), SRTSOCK_TYPE_SOCK,   \
                             SrtSockSockClass))
#define SRTSOCK_IS_SOCK_CLASS(klass)                            \
    (G_TYPE_CHECK_CLASS_TYPE((klass), SRTSOCK_TYPE_SOCK))
#define SRTSOCK_SOCK_GET_CLASS(obj)                        \
    (G_TYPE_INSTANCE_GET_CLASS((obj), SRTSOCK_TYPE_SOCK,   \
                               SrtSockSockClass))

typedef struct _SrtSockSock SrtSockSock;
typedef struct _SrtSockSockPrivate SrtSockSockPrivate;
typedef struct _SrtSockSockClass SrtSockSockClass;

struct _SrtSockSock {
    GObject parent;
    SrtSockSockPrivate *priv;
};

struct _SrtSockSockClass {
    GObjectClass parent_class;
};

#ifdef __cplusplus
extern "C" {
#endif
    GType srtsock_sock_get_type();
    SrtSockSock *srtsock_sock_new(GSocketFamily family, GSocketType type,
                                  GSocketProtocol protocol, GError **error);
    SrtSockSock *srtsock_sock_new_from_fd(int fd, GError **error);
    // SrtSockSock *srtsock_sock_new_from_sock(GSocket *sock);
    gboolean srtsock_sock_init(SrtSockSock *self, GSocketFamily family,
                               GSocketType type, GSocketProtocol protocol,
                               GError **error);
    gboolean srtsock_sock_init_from_fd(SrtSockSock *self, int fd, GError **error);

    SrtSockSock *srtsock_sock_accept(SrtSockSock *self, GError **error);
    gboolean srtsock_sock_start_accept(SrtSockSock *self);
    void srtsock_sock_stop_accept(SrtSockSock *self);
    gboolean srtsock_sock_bind(SrtSockSock *self, GSocketAddress *addr,
                               gboolean allow_reuse, GError **error);

    gboolean srtsock_sock_conn(SrtSockSock *self, GSocketAddress *addr,
                               GError **error);
    gboolean srtsock_sock_conn_async(SrtSockSock *self,
                                     GSocketAddress *addr,
                                     GAsyncReadyCallback callback,
                                     gpointer user_data);
    gboolean srtsock_sock_conn_finish(SrtSockSock *self,
                                      GAsyncResult *result, GError **error);
    GSocketFamily srtsock_sock_get_family(SrtSockSock *self);
    GSocketAddress *srtsock_sock_get_local_address(SrtSockSock *self,
                                                   GError **error);
    GSocketAddress *srtsock_sock_get_remote_address(SrtSockSock *self,
                                                    GError **error);

    gboolean srtsock_sock_start_recv(SrtSockSock *self);
    void srtsock_sock_stop_recv(SrtSockSock *self);
    gchar *srtsock_sock_recv(SrtSockSock *self, gsize size, gssize *rsize,
                             GError **error);
    void srtsock_sock_send(SrtSockSock *self, const gchar *buff, gsize size);
    gboolean srtsock_sock_start_send(SrtSockSock *self);
    void srtsock_sock_stop_send(SrtSockSock *self);
    gboolean srtsock_sock_wait_send(SrtSockSock *self, GError **error);

    gboolean srtsock_sock_close(SrtSockSock *self, GError **error);
    gboolean srtsock_sock_shutdown(SrtSockSock *self, gboolean read,
                                   gboolean write, GError **error);
    gchar *srtsock_buff_from_obj(GObject *obj, guint *len);
    GObject *srtsock_obj_from_buff(guint len, gchar *buff);
#ifdef __cplusplus
}
#endif

#endif /* __SRTSOCK_SOCK_H__ */
