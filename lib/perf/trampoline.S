/*
 * Copyright (c) 2024 Axoflow
 * Copyright (c) 2024 Balázs Scheidler <balazs.scheidler@axoflow.com>
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * As an additional exemption you are allowed to compile & link against the
 * OpenSSL libraries as published by the OpenSSL project. See the file
 * COPYING for details.
 *
 */
    .text
    .global      _perf_trampoline_func_start
    .align 16
_perf_trampoline_func_start:
#ifdef __x86_64__
    push    %rbp
    mov     _perf_trampoline_target_address(%rip), %r11
    call    *%r11
    pop	    %rbp
    ret
    .align 8
_perf_trampoline_target_address:
    .quad 0x0
#endif // __x86_64__

    .global      _perf_trampoline_func_end
_perf_trampoline_func_end:
    .section .note.GNU-stack,"",@progbits
