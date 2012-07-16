#include <srtsock_buff.h>
#include <stdio.h>
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

#if GLIB_CHECK_VERSION(2, 32, 0)
#  define EMBED_GMUTEX 1
#else
#  define EMBED_GMUTEX 0
#endif

/**
 * SrtSockBuff: (skip)
 **/
struct _SrtSockBuff {
    guint len1;
    guint len2;
    guint offset;
    gchar *buff1;
    gchar *buff2;
#if EMBED_GMUTEX
    GMutex push_lock;
#else
    GMutex *push_lock;
#endif
};

/**
 * EMBED_GMUTEX: (skip)
 **/

/**
 * srtsock_buff_new: (skip)
 **/
SrtSockBuff*
srtsock_buff_new()
{
    SrtSockBuff *self;
    self = g_new0(SrtSockBuff, 1);
    if (G_UNLIKELY(!self))
        return NULL;
#if EMBED_GMUTEX
    g_mutex_init(&self->push_lock);
#else
    self->push_lock = g_mutex_new();
#endif
    return self;
}

/**
 * srtsock_buff_push: (skip)
 **/
void
srtsock_buff_push(SrtSockBuff *self, const gchar *buff, guint len)
{
    if (G_UNLIKELY(!self || !buff || !len))
        return;
#if EMBED_GMUTEX
    g_mutex_lock(&self->push_lock);
#else
    g_mutex_lock(self->push_lock);
#endif
    self->buff2 = g_realloc(self->buff2, self->len2 + len);
    memcpy(self->buff2 + self->len2, buff, len);
    self->len2 += len;
#if EMBED_GMUTEX
    g_mutex_unlock(&self->push_lock);
#else
    g_mutex_unlock(self->push_lock);
#endif
}

static void
srtsock_buff_update(SrtSockBuff *self)
{
    if (!self->len2 || !self->buff2) {
        self->len2 = 0;
        self->buff2 = NULL;
        return;
    } else if (!self->len1 || !self->buff1) {
        self->offset = 0;
        self->len1 = self->len2;
        self->buff1 = self->buff2;
        self->buff2 = NULL;
        self->len2 = 0;
        return;
    } else if (self->len1 <= self->offset) {
        g_free(self->buff1);
        self->offset = 0;
        self->len1 = self->len2;
        self->buff1 = self->buff2;
        self->buff2 = NULL;
        self->len2 = 0;
        return;
    } else {
        guint rsize1 = self->len1 - self->offset;
        self->buff2 = g_realloc(self->buff2, self->len2 + rsize1);
        memmove(self->buff2 + rsize1, self->buff2, self->len2);
        memcpy(self->buff2, self->buff1 + self->offset, rsize1);
        g_free(self->buff1);
        self->buff1 = self->buff2;
        self->len1 = self->len2 + rsize1;
        self->len2 = 0;
        self->offset = 0;
        self->buff2 = NULL;
    }
}

/**
 * srtsock_buff_get: (skip)
 **/
gchar*
srtsock_buff_get(SrtSockBuff *self, guint *len)
{
    gchar *res;
    if (G_UNLIKELY(!self || !len))
        return NULL;
#if EMBED_GMUTEX
    g_mutex_lock(&self->push_lock);
#else
    g_mutex_lock(self->push_lock);
#endif
    srtsock_buff_update(self);
    *len = self->len1 - self->offset;
    res = self->buff1 + self->offset;
#if EMBED_GMUTEX
    g_mutex_unlock(&self->push_lock);
#else
    g_mutex_unlock(self->push_lock);
#endif
    return res;
}

/**
 * srtsock_buff_pop: (skip)
 **/
void
srtsock_buff_pop(SrtSockBuff *self, guint len)
{
    if (G_UNLIKELY(!self))
        return;
#if EMBED_GMUTEX
    g_mutex_lock(&self->push_lock);
#else
    g_mutex_lock(self->push_lock);
#endif
    self->offset += len;
    srtsock_buff_update(self);
#if EMBED_GMUTEX
    g_mutex_unlock(&self->push_lock);
#else
    g_mutex_unlock(self->push_lock);
#endif
}

/**
 * srtsock_buff_free: (skip)
 **/
void
srtsock_buff_free(SrtSockBuff *self)
{
    if (G_UNLIKELY(!self))
        return;
    g_free(self->buff1);
    g_free(self->buff2);
#if EMBED_GMUTEX
    g_mutex_clear(&self->push_lock);
#else
    g_mutex_free(self->push_lock);
#endif
    g_free(self);
}

/**
 * srtsock_buff_free: (skip)
 **/
gboolean
srtsock_buff_empty(SrtSockBuff *self)
{
    gboolean res = FALSE;
    if (G_UNLIKELY(!self))
        return FALSE;
#if EMBED_GMUTEX
    g_mutex_lock(&self->push_lock);
#else
    g_mutex_lock(self->push_lock);
#endif
    srtsock_buff_update(self);
    if ((!self->buff1 || self->offset >= self->len1) &&
        (!self->buff2 || !self->len2))
        res = TRUE;
#if EMBED_GMUTEX
    g_mutex_unlock(&self->push_lock);
#else
    g_mutex_unlock(self->push_lock);
#endif
    return res;
}
