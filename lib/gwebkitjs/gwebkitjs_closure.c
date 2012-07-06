#include <gwebkitjs_closure.h>
#include <gwebkitjs_util.h>
#include <stdlib.h>
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

typedef struct {
    GWebKitJSClosure pub;
    GWebKitJSClosureType type;
    GCallback user_func;
    gpointer p;
    ffi_closure *clsr;
} GWebKitJSClosureInter;

static guint
gwebkitjs_closure_type_total_size(ffi_type *type)
{
    int i;
    guint size;
    if (!type)
        return 0;
    if (!type->elements)
        return sizeof(ffi_type);
    size = sizeof(ffi_type);
    for (i = 0;type->elements[i];i++)
        size += gwebkitjs_closure_type_total_size(type->elements[i]);
    size += (i + 1) * sizeof(ffi_type*);
    return size;
}

static guint
gwebkitjs_closure_type_fill_buff(void *buff, const ffi_type *type)
{
    int i;
    void *p;
    ffi_type *tmp_type;
    ffi_type **eles_type;
    guint size = 0;
    guint tmp_size;

    if (!buff || !type)
        return 0;

    memcpy(buff, type, sizeof(ffi_type));

    if (!type->elements)
        return sizeof(ffi_type);

    tmp_type = buff;
    p = buff + sizeof(ffi_type);
    size += sizeof(ffi_type);

    tmp_type->elements = eles_type = p;

    for (i = 0;type->elements[i];i++) {
    }

    tmp_size = (i + 1) * sizeof(ffi_type*);
    p += tmp_size;
    size += tmp_size;
    eles_type[i] = NULL;

    for (i = 0;type->elements[i];i++) {
        tmp_size = gwebkitjs_closure_type_fill_buff(p, type->elements[i]);
        eles_type[i] = p;
        p += tmp_size;
        size += tmp_size;
    }
    return size;
}

static ffi_type*
gwebkitjs_closure_type_copy(ffi_type *type)
{
    guint size;
    void *buff;
    size = gwebkitjs_closure_type_total_size(type);
    if (!size)
        return NULL;
    buff = g_malloc0(size);
    if (!buff)
        return NULL;
    size = gwebkitjs_closure_type_fill_buff(buff, type);
    return buff;
}

/**
 * gwebkitjs_closure_type_create: (skip)
 **/
ffi_type*
gwebkitjs_closure_type_create(guint argc, ...)
{
    if (!argc)
        return NULL;
    guint i;
    va_list ap;
    ffi_type *eles[argc + 1];
    ffi_type tmpres = {
        .size = 0,
        .alignment = 0,
        .elements = eles
    };
    va_start(ap, argc);
    for (i = 0;i < argc;i++) {
        eles[i] = va_arg(ap, ffi_type*);
    }
    va_end(ap);
    eles[i] = NULL;
    return gwebkitjs_closure_type_copy(&tmpres);
}

static guint
gwebkitjs_closure_cif_prep_size(ffi_type *ret_t, ffi_type **argv, guint argc)
{
    guint i;
    guint size;

    size = sizeof(ffi_cif);
    size += gwebkitjs_closure_type_total_size(ret_t);
    size += argc * sizeof(ffi_type*);

    for (i = 0;i < argc;i++) {
        size += gwebkitjs_closure_type_total_size(argv[i]);
    }
    return size;
}

static void*
gwebkitjs_closure_cif_alloc(guint argc, ffi_type *ret_t, ffi_type **argv,
                            void **ret_p, void **argv_p)
{
    guint i;
    ffi_cif *res;
    void *arg_p;
    guint size;

    size = gwebkitjs_closure_cif_prep_size(ret_t, argv, argc);

    res = g_malloc0(size);
    if (!res)
        return NULL;
    *ret_p = res + sizeof(ffi_cif);
    *argv_p = *ret_p + gwebkitjs_closure_type_fill_buff(*ret_p, ret_t);
    arg_p = *argv_p + argc * sizeof(ffi_type*);
    for (i = 0;i < argc;i++) {
        ((ffi_cif**)*argv_p)[i] = arg_p;
        arg_p += gwebkitjs_closure_type_fill_buff(arg_p, argv[i]);
    }
    if (!argc)
        *argv_p = NULL;
    return res;
}

/**
 * gwebkitjs_closure_cif_create_lst: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create_lst(ffi_type *ret_t, guint argc, ffi_type **argv)
{
    ffi_cif *res;

    void *ret_p;
    void *argv_p;

    if (!ret_t)
        ret_t = &ffi_type_void;
    res = gwebkitjs_closure_cif_alloc(argc, ret_t, argv, &ret_p, &argv_p);

    if (!res)
        return NULL;
    if (ffi_prep_cif(res, FFI_DEFAULT_ABI, argc, ret_p, argv_p) == FFI_OK)
        return res;
    g_free(res);
    return NULL;
}

/**
 * gwebkitjs_closure_cif_create_va: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create_va(ffi_type *ret_t, guint argc, va_list ap)
{
    guint i;
    ffi_type *argv[argc];
    for (i = 0;i < argc;i++)
        argv[i] = va_arg(ap, ffi_type*);
    return gwebkitjs_closure_cif_create_lst(ret_t, argc, argv);
}

/**
 * gwebkitjs_closure_cif_create: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create(ffi_type *ret_t, guint argc, ...)
{
    va_list ap;
    ffi_cif *res;
    va_start(ap, argc);
    res = gwebkitjs_closure_cif_create_va(ret_t, argc, ap);
    va_end(ap);
    return res;
}

/**
 * gwebkitjs_closure_cif_create_var_lst: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create_var_lst(ffi_type *ret_t, guint fixc, guint argc,
                                     ffi_type **argv)
{
    ffi_cif *res;

    void *ret_p;
    void *argv_p;

    if (!ret_t)
        ret_t = &ffi_type_void;
    res = gwebkitjs_closure_cif_alloc(argc, ret_t, argv, &ret_p, &argv_p);

    if (!res)
        return NULL;
    if (ffi_prep_cif_var(res, FFI_DEFAULT_ABI, fixc,
                         argc, ret_p, argv_p) == FFI_OK)
        return res;
    g_free(res);
    return NULL;
}

/**
 * gwebkitjs_closure_cif_create_var_va: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create_var_va(ffi_type *ret_t, guint fixc,
                                    guint argc, va_list ap)
{
    guint i;
    ffi_type *argv[argc];
    for (i = 0;i < argc;i++)
        argv[i] = va_arg(ap, ffi_type*);
    return gwebkitjs_closure_cif_create_var_lst(ret_t, fixc, argc, argv);
}

/**
 * gwebkitjs_closure_cif_create_var: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create_var(ffi_type *ret_t, guint fixc, guint argc, ...)
{
    va_list ap;
    ffi_cif *res;
    va_start(ap, argc);
    res = gwebkitjs_closure_cif_create_var_va(ret_t, fixc, argc, ap);
    va_end(ap);
    return res;
}

static ffi_cif*
gwebkitjs_closure_type_get_clsr_cif(GWebKitJSClosureType type)
{
    if (!type)
        return NULL;
    return type;
}

static ffi_cif*
gwebkitjs_closure_type_get_user_cif(GWebKitJSClosureType type)
{
    if (!type)
        return NULL;
    return type + sizeof(ffi_cif);
}

/**
 * gwebkitjs_closure_new_type_lst: (skip)
 **/
GWebKitJSClosureType
gwebkitjs_closure_new_type_lst(ffi_type *ret_t, guint argc, ffi_type **argv)
{
    guint size;
    guint i;

    gpointer res;
    gpointer p;
    ffi_cif *clsr_cif;
    ffi_cif *user_cif;
    gpointer ret_p;
    ffi_type **arg_lst;
    gpointer args_p;

    if (!ret_t)
        ret_t = &ffi_type_void;

    size = gwebkitjs_closure_cif_prep_size(ret_t, argv, argc);
    size += sizeof(ffi_cif) + sizeof(ffi_type*);
    size += gwebkitjs_closure_type_total_size(&ffi_type_pointer);

    res = g_malloc0(size);
    ret_p = res + 2 * sizeof(ffi_cif);
    arg_lst = p = ret_p + gwebkitjs_closure_type_fill_buff(ret_p, ret_t);;
    args_p = p + (argc + 1) * sizeof(ffi_type*);

    arg_lst[0] = args_p;
    args_p += gwebkitjs_closure_type_fill_buff(args_p, &ffi_type_pointer);
    for (i = 1;i <= argc;i++) {
        arg_lst[i] = args_p;
        args_p += gwebkitjs_closure_type_fill_buff(args_p, argv[i - 1]);
    }

    clsr_cif = gwebkitjs_closure_type_get_clsr_cif(res);
    user_cif = gwebkitjs_closure_type_get_user_cif(res);
    if (ffi_prep_cif(clsr_cif, FFI_DEFAULT_ABI, argc, ret_p, arg_lst + 1)
        != FFI_OK) {
        g_free(res);
        return NULL;
    }
    if (ffi_prep_cif(user_cif, FFI_DEFAULT_ABI, argc + 1, ret_p, arg_lst)
        != FFI_OK) {
        g_free(res);
        return NULL;
    }
    return res;
}

/**
 * gwebkitjs_closure_new_type_va: (skip)
 **/
GWebKitJSClosureType
gwebkitjs_closure_new_type_va(ffi_type *ret_t, guint argc, va_list ap)
{
    guint i;
    ffi_type *argv[argc];
    for (i = 0;i < argc;i++)
        argv[i] = va_arg(ap, ffi_type*);
    return gwebkitjs_closure_new_type_lst(ret_t, argc, argv);
}

/**
 * gwebkitjs_closure_new_type: (skip)
 **/
GWebKitJSClosureType
gwebkitjs_closure_new_type(ffi_type *ret_t, guint argc, ...)
{
    va_list ap;
    GWebKitJSClosureType res;
    va_start(ap, argc);
    res = gwebkitjs_closure_new_type_va(ret_t, argc, ap);
    va_end(ap);
    return res;
}

static void
gwebkitjs_closure_cb(ffi_cif *cif, gpointer ret, void *args[],
                     gpointer data)
{
    GWebKitJSClosureInter *self;
    guint i;
    ffi_cif *user_cif;
    self = data;
    if (!self->pub.func)
        return;
    user_cif = gwebkitjs_closure_type_get_user_cif(self->type);
    void *nargs[user_cif->nargs];
    nargs[0] = &self->p;
    for (i = 1;i <= user_cif->nargs;i++) {
        nargs[i] = args[i - 1];
    }
    ffi_call(user_cif, self->user_func, ret, nargs);
}

/**
 * gwebkitjs_closure_create: (skip)
 **/
GWebKitJSClosure*
gwebkitjs_closure_create(GWebKitJSClosureType type,
                         GCallback user_func, gpointer p)
{
    GWebKitJSClosureInter *res;
    ffi_cif *clsr_cif;

    if (!type)
        goto fail;
    clsr_cif = gwebkitjs_closure_type_get_clsr_cif(type);
    res = g_new0(GWebKitJSClosureInter, 1);
    if (!res)
        goto fail;
    res->type = type;
    res->user_func = user_func;
    res->p = p;
    res->clsr = ffi_closure_alloc(sizeof(ffi_closure),
                                  (void**)&(res->pub.func));
    if (!res->clsr)
        goto free_res;
    if (ffi_prep_closure_loc(res->clsr, clsr_cif, gwebkitjs_closure_cb, res,
                             res->pub.func) != FFI_OK)
        goto free_clsr;
    return (GWebKitJSClosure*)res;

free_clsr:
    ffi_closure_free(res->clsr);
free_res:
    g_free(res);
fail:
    return NULL;
}

/**
 * gwebkitjs_closure_free: (skip)
 **/
void
gwebkitjs_closure_free(GWebKitJSClosure *self)
{
    if (!self)
        return;
    ffi_closure_free(((GWebKitJSClosureInter*)self)->clsr);
    g_free(self);
}
