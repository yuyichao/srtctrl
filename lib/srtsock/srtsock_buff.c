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

/**
 * SrtSockBuff: (skip)
 **/
struct _SrtSockBuff {
    guint len1;
    guint len2;
    guint offset;
    gchar *buff1;
    gchar *buff2;
    GMutex push_lock;
};

/**
 * srtsock_buff_new: (skip)
 **/
SrtSockBuff*
srtsock_buff_new()
{
    SrtSockBuff *self;
    self = g_new0(SrtSockBuff, 1);
    if (G_UNLIKELY(self))
        return NULL;
    g_mutex_init(&self->push_lock);
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
    g_mutex_lock(&self->push_lock);
    self->buff2 = g_realloc(self->buff2, self->len2 + len);
    memcpy(self->buff2 + self->len2, buff, len);
    self->buff2 += len;
    g_mutex_unlock(&self->push_lock);
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
    if (G_UNLIKELY(!self || !len))
        return NULL;
    g_mutex_lock(&self->push_lock);
    srtsock_buff_update(self);
    *len = self->len1;
    g_mutex_unlock(&self->push_lock);
    return self->buff1;
}

/**
 * srtsock_buff_pop: (skip)
 **/
void
srtsock_buff_pop(SrtSockBuff *self, guint len)
{
    if (G_UNLIKELY(!self))
        return;
    g_mutex_lock(&self->push_lock);
    self->offset += len;
    srtsock_buff_update(self);
    g_mutex_unlock(&self->push_lock);
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
    g_mutex_clear(&self->push_lock);
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
    g_mutex_lock(&self->push_lock);
    srtsock_buff_update(self);
    if ((!self->buff1 || self->offset >= self->len1) &&
        (!self->buff2 || !self->len2))
        res = TRUE;
    g_mutex_unlock(&self->push_lock);
    return res;
}
