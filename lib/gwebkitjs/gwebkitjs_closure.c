#include <gwebkitjs_closure.h>
#include <gwebkitjs_util.h>
#include <stdlib.h>
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
gwebkitjs_closure_cif_prep_arg(ffi_type *ret_t, ffi_type **argv,
                               guint argc, va_list ap)
{
    guint i;
    guint size;

    size = sizeof(ffi_cif);
    size += gwebkitjs_closure_type_total_size(ret_t);
    size += argc * sizeof(ffi_type*);

    for (i = 0;i < argc;i++) {
        argv[i] = va_arg(ap, ffi_type*);
        size += gwebkitjs_closure_type_total_size(argv[i]);
    }
    return size;
}

static void*
gwebkitjs_closure_cif_alloc(guint argc, ffi_type *ret_t, va_list ap,
                            void **ret_p, void **argv_p)
{
    guint i;
    ffi_cif *res;
    void *arg_p;
    ffi_type *argv[argc];
    guint size;

    size = gwebkitjs_closure_cif_prep_arg(ret_t, argv, argc, ap);

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
 * gwebkitjs_closure_cif_create: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create(ffi_type *ret_t, guint argc, ...)
{
    ffi_cif *res;
    va_list ap;

    void *ret_p;
    void *argv_p;

    if (!ret_t)
        ret_t = &ffi_type_void;
    va_start(ap, argc);
    res = gwebkitjs_closure_cif_alloc(argc, ret_t, ap, &ret_p, &argv_p);
    va_end(ap);

    if (!res)
        return NULL;
    if (ffi_prep_cif(res, FFI_DEFAULT_ABI, argc, ret_p, argv_p) == FFI_OK)
        return res;
    g_free(res);
    return NULL;
}

/**
 * gwebkitjs_closure_cif_create_var: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create_var(ffi_type *ret_t, guint fixc, guint argc, ...)
{
    ffi_cif *res;
    va_list ap;

    void *ret_p;
    void *argv_p;

    if (!ret_t)
        ret_t = &ffi_type_void;
    va_start(ap, argc);
    res = gwebkitjs_closure_cif_alloc(argc, ret_t, ap, &ret_p, &argv_p);
    va_end(ap);

    if (!res)
        return NULL;
    if (ffi_prep_cif_var(res, FFI_DEFAULT_ABI, fixc,
                         argc, ret_p, argv_p) == FFI_OK)
        return res;
    g_free(res);
    return NULL;
}
