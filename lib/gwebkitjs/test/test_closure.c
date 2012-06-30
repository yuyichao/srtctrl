#include <gwebkitjs_closure.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int i;
    gchar *str;
    int j;
} m_struct;

typedef struct {
    int i;
    gchar *str;
    char c1;
    int j;
    char c2;
    m_struct ms1;
    char c3;
    int k;
    m_struct ms2;
} m_struct2;

void
print_str(char *str)
{
    if (str)
        printf("%s\n", str);
    else
        printf("(null)\n");
}

void
print_ms(m_struct ms)
{
    printf("ms.str: ");
    print_str(ms.str);
    printf("ms.i: %d, ms.j: %d\n", ms.i, ms.j);
}

void
print_ms2(m_struct2 ms2)
{
    printf("ms2.i: %d, ms2.j: %d, ms2.k: %d\n", ms2.i, ms2.j, ms2.k);
    printf("ms2.str: ");
    print_str(ms2.str);
    printf("ms2.ms1:\n");
    print_ms(ms2.ms1);
    printf("ms2.ms2:\n");
    print_ms(ms2.ms2);
    printf("ms2.c1: %c, ms2.c2: %c, ms2.c3: %c\n", ms2.c1, ms2.c1, ms2.c3);
}

int
test_func(gchar *str1, m_struct ms, m_struct2 ms2)
{
    printf("str1: ");
    print_str(str1);
    print_ms(ms);
    print_ms2(ms2);
    return 11234;
}

typedef int (*m_func)(m_struct ms, m_struct2 ms2);

int
main()
{
    GWebKitJSClosureType type;
    ffi_type *ms_type;
    ffi_type *ms2_type;
    m_struct ms = {
        .i = 20,
        .j = 40,
        .str = "kkk"
    };
    m_struct2 ms2 = {
        .i = 12,
        .j = 13,
        .k = 17,
        .c1 = 'y',
        .c2 = 'y',
        .c3 = 'c',
        .str = "test",
        .ms1 = {
            .i = 100,
            .j = 110,
            .str = "ms2.ms1"
        },
        .ms2 = {
            .i = 200,
            .j = 220,
            .str = "ms2.ms2"
        },
    };

    printf("start\n");
    ms_type = gwebkitjs_closure_type_create(3, &ffi_type_sint,
                                            &ffi_type_pointer, &ffi_type_sint);
    ms2_type = gwebkitjs_closure_type_create(9, &ffi_type_sint,
                                             &ffi_type_pointer,
                                             &ffi_type_schar, &ffi_type_sint,
                                             &ffi_type_schar, ms_type,
                                             &ffi_type_schar, &ffi_type_sint,
                                             ms_type);
    type = gwebkitjs_closure_new_type(&ffi_type_sint, 2, ms_type, ms2_type);
    g_free(ms_type);
    g_free(ms2_type);
    GWebKitJSClosure *clsr = gwebkitjs_closure_create(type,
                                                      G_CALLBACK(test_func),
                                                      ";;;;");
    printf("before call\n");
    ((m_func)clsr->func)(ms, ms2);
    gwebkitjs_closure_free(clsr);
    g_free(type);
    return 0;
}
