#ifndef __SRTSOCK_BUFF_H__
#define __SRTSOCK_BUFF_H__

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

#include <glib.h>

typedef struct _SrtSockBuff SrtSockBuff;

#ifdef __cplusplus
extern "C" {
#endif

    SrtSockBuff *srtsock_buff_new();
    void srtsock_buff_push(SrtSockBuff *self, const gchar *buff, guint len);
    gchar *srtsock_buff_get(SrtSockBuff *self, guint *len);
    void srtsock_buff_pop(SrtSockBuff *self, guint len);
    gboolean srtsock_buff_empty(SrtSockBuff *self);
    void srtsock_buff_free(SrtSockBuff *self);

#ifdef __cplusplus
}
#endif

#endif /* __SRTSOCK_BUFF_H__ */
