#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import time

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.skip_test('PharLap is only available on Windows; skipping test.\n')

if not test.detect_tool('linkloc'):
    test.skip_test("Could not find 'linkloc', skipping test.\n")

if not test.detect_tool('386asm'):
    test.skip_test("Could not find '386asm', skipping test.\n")

# From the Phar Lap minasm example program...
test.write("minasm.asm", r"""
; 
; MINASM.ASM - A minimal assembly language program which runs
;       under ToolSuite.  You can use this program as a framework
;       for large assembly language programs.
;
.386

;
; Segmentation and segment ordering.
;
; First comes the code segment.
;
_TEXT	segment use32 byte public 'CODE'
_TEXT	ends

;
; The data segment contains initialized RAM based data.  It will automatically
; be placed in the ROM at link time and unpacked into RAM at run-time
; by the __pl_unpackrom function.
;
; If you do not need any initialized data in your assembly language program,
; you can leave this segment empty and remove the call to __pl_unpackrom.
;
;
_DATA	segment use32 dword public 'DATA'

loopcount	dd 10d
rammessage	db 'This message is in RAM memory',0dh,0ah,0

_DATA	ends

;
; The BSS segment contains RAM based variables which
; are initialized to zero at run-time.  Putting unitialized
; variables which should start at zero here saves space in
; the ROM.
;
; If you do not need any zero-initialized data in your assembly language
; program, you can leave this segment empty (and optionally remove the
; instructions below which initialize it).
;
; The segment name must be lower case for compatibility with the linker
;
_bss	segment use32 dword public 'BSS'
dummy_bss db 32 dup(?)	; Use a little bit of BSS just to test it
_bss	ends

;
; The const segment contains constants which will never
; change.  It is put in the ROM and never copied to RAM.
;
; If you do not need any ROM based constants in your assembly language
; program, you can leave this segment empty.
;
_CONST	segment use32 dword public 'CONST'
rommessage	db 'This message is in ROM memory',0dh,0ah,0
_CONST	ends

;
; We're in flat model, so we'll put all the read-only segments we know about
; in a code group, and the writeable segments in a data group, so that
; we can use assume to easily get addressability to the segments.
;
CGROUP group _TEXT, _CONST
DGROUP group _DATA, _bss

        assume cs:CGROUP,ds:DGROUP
_TEXT	segment

;
; _main - the main routine of this program.
;
; We will display the RAM and ROM messages the number of times
; specified in the loopcount variable.  This proves that we can
; initialize RAM data out of ROM and the fact that we can
; modify the loop count in memory verifies that it actually ends
; up in RAM.
;
        public _main
_main proc near

        mov	cl,0ah			; Skip a line before we start
        call	PutCharTarget		;
main_loop:
        cmp	loopcount,0		; Are we at the end of our loop?
        je	short done_main		;  yes.
        lea	edx,rommessage		; EDX -> ROM message
        call	WriteStringTarget	; Display it
        lea	edx,rammessage		; EDX -> RAM message
        call	WriteStringTarget	; Display it
        dec	loopcount		;
        jmp	main_loop		; Branch back for next loop iteration
done_main:
        ret				; That's it!

_main endp

;
; WriteStringTarget - Display a string on the target console
;
; Inputs:
;       EDX -> Null terminated ASCII string to display
;
; Outputs:
;       All registers preserved
;
WriteStringTarget proc near

        push	ecx			; Save registers
        push	edx			;

write_loop:
        movzx	ecx,byte ptr [edx]	; Get a character
        jecxz	done_str		; Branch if end of string
        call	PutCharTarget		; Display this character
        inc	edx			; Bump scan pointer
        jmp	write_loop		; And loop back for next character

done_str:
        pop	edx			; Restore registers
        pop	ecx			;
        ret				;  and return

WriteStringTarget endp

;
; PutCharTarget - Write a character on the target console
;
; This routine displays a character on the target console by using
; the PutChar kernel service available through int 254.
;
; Inputs:
;       CL = character to display
;
; Outputs:
;       All registers preserved
;
PutCharTarget proc near

        push	eax		; Save registers
        push	ebx		;
        push	edx		;

        mov     ax,254Ah	; Request Kernel Service
        mov     bx,1		; service code 1 = PutChar
        movzx   edx,cl		; EDX = character to display
        int     0FEh		; Int 254 is for kernel services

        pop	edx		; Restore registers
        pop	ebx		;
        pop	eax		;
        ret			;  and return

PutCharTarget endp

;
; The __pl_unpackrom unpacks initialized RAM based data variables
; out of the ROMINIT segment into their RAM area.  They are put
; in the ROMINIT segment with the -ROMINIT switch in the link file.
;
extrn __pl_unpackrom:near

;
; The _EtsExitProcess function is used to terminate our program
;
extrn _EtsExitProcess:near

;
; The linker will define symbols for the beginning and end of the
; BSS segment.
;
extrn   __p_SEG__bss_BEGIN:dword
extrn   __p_SEG__bss_END:dword

;
; __p_start -- The entry point for our assembly language program.
; We unpack the RAM based variables out of the ROM and clear the
; BSS to zero, then call _main where the real work happens.  When
; _main returns, we call EtsExitProcess(0) to terminate.
;
public __p_start
__p_start proc near
        pushad				; save initial regs
        push	es				;
        call	__pl_unpackrom		; Call the unpacker 
        cld				; Clear direction flag

        lea 	eax,__p_SEG__bss_END	; load end address and 
        lea	ebx,__p_SEG__bss_BEGIN	; subtract start to get size
        sub 	eax,ebx
        mov 	ecx,eax			; This is size
        inc	ecx
        lea	edi,__p_SEG__bss_BEGIN	; Zero from start address
        mov 	al,0			;Zero out BSS and C_COMMON	
        rep     stosb

        pop	es			; restore initial regs
        popad
        call	_main			; go do some work
stopme:
 	xor	eax,eax			; Call _EtsExitProcess(0)
        push	eax			;
        call	_EtsExitProcess		;
        pop	eax			;
        jmp	stopme			;  .. in a loop just in case it ever
        				;  comes back

__p_start endp

TD_hack:
        mov	eax, __p_tdhack		; force reference to TD-hack symbol

_TEXT	ends

;
;       Hack for Turbo Debugger/TDEMB - TD will fault if the .exe being
;       debugged doesn't have an import table.  (TD looks for the address of
;       the table, then dereferences that address wihtout checking for NULL).
;
;       This symbol, __p_tdhack, must be declared as an import in all the
;       .emb files shipped.  IE:
;
;               -implib embkern.lib
;               -import __p_tdhack
;
;       This forces the creation of an import table within the .EXE.
_DATA	segment
extrn	__p_tdhack:dword
_DATA	ends
        end	__p_start
""")

test.write("foo.lnk","""
@baz\\bar.lnk
""")

test.subdir("baz")
test.write([ "baz", "bar.lnk"],"""
@asm.emb
""")

test.write("SConstruct", """
env=Environment(tools = [ 'linkloc', '386asm' ],
                ASFLAGS='-twocase -cvsym',
                LINKFLAGS='@foo.lnk')
env.Program(target='minasm', source='minasm.asm')
""")

test.run(arguments='.')

# Assume .exe extension...this test is for Windows only.
test.fail_test(not os.path.exists('minasm.exe'))
test.up_to_date(arguments='.')

# Updating a linker command file should cause a rebuild!
test.write([ "baz", "bar.lnk"],"""
-cvsym
@asm.emb
""")

oldtime = os.path.getmtime(test.workpath('minasm.exe'))
time.sleep(2) # Give the time stamp time to change
test.run(arguments = '.')
test.fail_test(oldtime == os.path.getmtime(test.workpath('minasm.exe')))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
