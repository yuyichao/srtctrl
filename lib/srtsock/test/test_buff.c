#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <srtsock_buff.h>
#include <glib.h>

#define COUNTN 1000000

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

static gboolean done = FALSE;

gpointer
push_thread(gpointer data)
{
    SrtSockBuff *buff;
    /* gchar *c; */
    guint n;
    int j;
    int acc = 0;
    buff = data;
    while (TRUE) {
        /* c = srtsock_buff_get(buff, &n); */
        srtsock_buff_get(buff, &n);
        j = rand() % (n > 98 ? 100 : (n + 2));
        j = j > n ? n : j;
        if (j > 0) {
            /* printf("%d\n", j); */
            /* j = write(1, c, j); */
            /* printf("\n\n"); */
            srtsock_buff_pop(buff, j);
            acc += j;
        }
        if (srtsock_buff_empty(buff) && done)
            break;
    }
    printf("%d\n", acc);
    return NULL;
}

int
main()
{
    GThread *thread;
    SrtSockBuff *buff;
    int i;
    char *c = "0123456789";
    srand(time(NULL));
    buff = srtsock_buff_new();
    thread = g_thread_new("push", push_thread, buff);
    for (i = 0;i < COUNTN;i++) {
        srtsock_buff_push(buff, c, 10);
    }
    done = TRUE;
    g_thread_join(thread);
    return 0;
}
