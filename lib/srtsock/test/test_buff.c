#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <srtsock_buff.h>
#include <glib.h>

#define COUNTN 1000000

static gboolean done = FALSE;

gpointer
push_thread(gpointer data)
{
    SrtSockBuff *buff;
    gchar *c;
    guint n;
    int j;
    int acc = 0;
    buff = data;
    while (TRUE) {
        c = srtsock_buff_get(buff, &n);
        j = rand() % (n > 98 ? 100 : (n + 2));
        j = j > n ? n : j;
        if (j > 0) {
            printf("%d\n", j);
            j = write(1, c, j);
            write(1, "\n\n", 2);
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
