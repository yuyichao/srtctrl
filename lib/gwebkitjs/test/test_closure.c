#include <gwebkitjs_closure.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int i;
    gchar *str;
    int j;
} m_struct;

int
test_func(gchar *str1, m_struct ms)
{
    if (str1)
        printf("str1: %s\n", str1);
    else
        printf("str1: (null)\n");
    if (ms.str)
        printf("ms.str: %s\n", ms.str);
    else
        printf("ms.str: (null)\n");
    printf("ms.i: %d, ms.j: %d\n", ms.i, ms.j);
    return 11234;
}

typedef int (*m_func)(m_struct ms);

int
main()
{
    GWebKitJSClosureType type;
    ffi_type *ftype;
    m_struct ms = {
        .i = 20,
        .j = 40,
        .str = "kkk"
    };
    printf("start\n");
    ftype = gwebkitjs_closure_type_create(3, &ffi_type_sint, &ffi_type_pointer,
                                          &ffi_type_sint);
    type = gwebkitjs_closure_new_type(&ffi_type_sint, 1, ftype);
    g_free(ftype);
    GWebKitJSClosure *clsr = gwebkitjs_closure_create(type,
                                                      G_CALLBACK(test_func),
                                                      ";;;;");
    printf("before call\n");
    printf("%lx\n", (unsigned long)clsr->func);
    ((m_func)clsr->func)(ms);
    gwebkitjs_closure_free(clsr);
    g_free(type);
    return 0;
}
