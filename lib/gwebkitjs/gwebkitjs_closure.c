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

/**
 * GWebKitJSClosureType: (skip):
 **/

/**
 * GWebKitJSClosure: (skip):
 **/

static void _bin_array(void *dest, size_t s1, void *p1, size_t s2, void *p2)
{
        memcpy(dest, p1, s1);
        memcpy(dest + s1, p2, s2);
}

#define bin_array(dest, n1, p1, n2, p2)                 \
    _bin_array((dest), (n1) * sizeof(*(dest)), (p1),    \
               (n2) * sizeof(*(dest)), (p2))

static void
gwebkitjs_closure_cb(ffi_cif *cif, void *ret, void **argv, void *p)
{
    GWebKitJSClosureType *cls_type = p;
    if (cls_type->front) {
        //bin_array(fullargtypes, extraargc, extraargtypes, cbargc, cbargtypes);
    } else {
        //bin_array(fullargtypes, cbargc, cbargtypes, extraargc, extraargtypes);
    }
}

/**
 * gwebkitjs_closure_type_new: (skip):
 **/
GWebKitJSClosureType*
gwebkitjs_closure_type_new(ffi_type *rtype, gboolean front,
                           guint cbargc, ffi_type **cbargtypes,
                           guint extraargc, ffi_type **extraargtypes)
{
    GWebKitJSClosureType *res;
    ffi_status status;
    guint fullargc = cbargc + extraargc;
    ffi_type *fullargtypes[fullargc];
    res = g_new0(GWebKitJSClosureType, 1);
    gwj_return_val_if_false(res, NULL);

    res->front = front;
    res->cbargc = cbargc;
    res->extraargc = extraargc;

    if (front) {
        bin_array(fullargtypes, extraargc, extraargtypes, cbargc, cbargtypes);
    } else {
        bin_array(fullargtypes, cbargc, cbargtypes, extraargc, extraargtypes);
    }

    status = ffi_prep_cif(&res->cbcif, FFI_DEFAULT_ABI, cbargc,
                          rtype, cbargtypes);
    if (status == FFI_OK)
        goto free;
    status = ffi_prep_cif(&res->extracif, FFI_DEFAULT_ABI, extraargc,
                          &ffi_type_pointer, extraargtypes);
    if (status == FFI_OK)
        goto free;
    status = ffi_prep_cif(&res->fullcif, FFI_DEFAULT_ABI, fullargc,
                          rtype, fullargtypes);
    if (status == FFI_OK)
        goto free;

    res->closure = ffi_closure_alloc(sizeof(ffi_closure), (void**)&res->create);
    if (res->closure)
        goto free;
    status = ffi_prep_closure_loc(res->closure, &res->extracif,
                                  gwebkitjs_closure_cb, res, res->create);

    return res;
free:
    g_free(res);
    return NULL;
}

GWebKitJSClosure*
gwebkitjs_closure_new(GWebKitJSClosureType *type, ...)
{
    void *res;
    void *args;
    gwj_return_val_if_false(type, NULL);
    gwj_return_val_if_false(type->create, NULL);
}

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

/**
 * gwebkitjs_closure_cif_create: (skip)
 **/
ffi_cif*
gwebkitjs_closure_cif_create(ffi_type *ret_t, guint argc, ...)
{
    guint i;
    guint size;
    ffi_cif *res;
    va_list ap;

    ffi_type *argv[argc];
    void *ret_p;
    void *argv_p;
    void *arg_p;

    size = sizeof(ffi_cif);
    if (!ret_t)
        ret_t = &ffi_type_void;
    size += gwebkitjs_closure_type_total_size(ret_t) + sizeof(argv);

    va_start(ap, argc);
    for (i = 0;i < argc;i++) {
        argv[i] = va_arg(ap, ffi_type*);
        size += gwebkitjs_closure_type_total_size(argv[i]);
    }
    va_end(ap);

    res = g_malloc0(size);
    if (!res)
        return NULL;
    ret_p = res + sizeof(ffi_cif);
    argv_p = ret_p + gwebkitjs_closure_type_fill_buff(ret_p, ret_t);
    arg_p = argv_p + sizeof(argv);
    for (i = 0;i < argc;i++) {
        ((ffi_cif**)argv_p)[i] = arg_p;
        arg_p += gwebkitjs_closure_type_fill_buff(arg_p, argv[i]);
    }
    if (!argc)
        argv_p = NULL;
    if (ffi_prep_cif(res, FFI_DEFAULT_ABI, argc, ret_p, argv_p) == FFI_OK)
        return res;
    g_free(res);
    return NULL;
}
