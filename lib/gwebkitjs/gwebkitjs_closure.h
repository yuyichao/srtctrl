#ifndef __GWEBKITJS_CLOSURE_H__
#define __GWEBKITJS_CLOSURE_H__

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

#include <ffi.h>
#include <glib.h>

#ifdef __cplusplus
extern "C" {
#endif

    ffi_type *gwebkitjs_closure_type_create(guint argc, ...);
    ffi_cif *gwebkitjs_closure_cif_create(ffi_type *ret_t, guint argc, ...);

#ifdef __cplusplus
}
#endif

#endif /* __GWEBKITJS_CLOSURE_H__ */
