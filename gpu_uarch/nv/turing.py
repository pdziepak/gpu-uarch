#
# Copyright © 2019 Paweł Dziepak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import struct

from gpu_uarch.nv import (Immediate, Register, SpecialRegister, ConstantMemory,
                          Memory, Control, Predicate, Instruction, UnknownInstruction)


def _as_signed32(v):
    return struct.unpack('=l', struct.pack('=L', v))[0]


def _parse_instruction(offset, lo, hi):
    ctrl = Control(hi)

    predicate_idx = (lo >> 12) & 0x7
    predicate_neg = (lo >> 15) & 0x1
    predicate = None if predicate_idx == 7 else Predicate(
        predicate_idx, predicate_neg == 1)

    imm = lo >> 32
    imm_s32 = _as_signed32(imm)
    imm_hi = imm >> 8

    cbank = imm & 0xff
    cval = imm_hi << 2

    dst = (lo >> 16) & 0xff

    src0 = (lo >> 24) & 0xff
    src1 = (lo >> 32) & 0xff
    src2 = hi & 0xff

    special_src = hi & 0xffff

    is64 = hi & 0x200

    def get_operands4(all_uniform=False):
        operand_pattern = lo & 0xf00

        if operand_pattern == 0x200:
            return [Register(dst, uniform=all_uniform), Register(
                src0, uniform=all_uniform), Register(src1, uniform=all_uniform), Register(src2, uniform=all_uniform)]
        elif operand_pattern == 0x600:
            return [Register(dst, uniform=all_uniform), Register(src0, uniform=all_uniform), Register(
                src2, uniform=all_uniform), ConstantMemory(Immediate(cbank), Immediate(cval))]
        elif operand_pattern == 0x800:
            return [Register(dst, uniform=all_uniform), Register(
                src0, uniform=all_uniform), Immediate(imm), Register(src2, uniform=all_uniform)]
        elif operand_pattern == 0xa00:
            return [Register(dst, uniform=all_uniform), Register(src0, uniform=all_uniform), ConstantMemory(
                Immediate(cbank), Immediate(cval)), Register(src2, uniform=all_uniform)]
        else:
            raise Exception(
                'Unknown operand pattern: {:#x}'.format(operand_pattern))

    def get_operands2():
        operand_pattern = lo & 0xf00
        if operand_pattern == 0x200:
            return [Register(dst), Register(src1)]
        elif operand_pattern == 0x300:
            return [Memory(Register(src0), Immediate(imm_hi)), Register(src1)]
        elif operand_pattern == 0x800:
            return [Register(dst), Immediate(imm)]
        elif operand_pattern == 0x900:
            return [Memory(Register(src2, uniform=True), Immediate(imm_hi)), Register(src1)]
        elif operand_pattern == 0xa00:
            return [Register(dst), ConstantMemory(Immediate(cbank), Immediate(cval))]
        elif operand_pattern == 0xb00:
            return [Register(dst), ConstantMemory(Immediate(cbank), Register(src0))]
        else:
            raise Exception(
                'Unknown operand pattern: {:#x}'.format(operand_pattern))

    # FIXME: This is actually not enough to identify an opcode. Looks like some bits in hi are also needed.
    opcode = lo & 0xff
    # FIXME: This is not enough to identify the operand pattern. Some bits from hi are also needed.
    operand_pattern = lo & 0xf00

    opcode_name = ''
    operands = []
    try:
        if opcode == 0x02:
            opcode_name = 'MOV'
            operands = get_operands2()
        elif opcode == 0x05:
            opcode_name = 'CS2R'
            operands = [Register(dst), SpecialRegister(special_src)]
        elif opcode == 0x10:
            opcode_name = 'IADD3'
            operands = get_operands4()
        elif opcode == 0x18:
            opcode_name = 'NOP'
        elif opcode == 0x19:
            opcode_name = 'S2R'
            operands = [Register(dst), SpecialRegister(special_src)]
        elif opcode == 0x24:
            opcode_name = 'IMAD'  # FIXME: variants of IMAD: IMAD.MOV, IMAD.IADD, etc
            operands = get_operands4()
        elif opcode == 0x47:
            opcode_name = 'BRA'
            operands = [Immediate(offset + 16 + imm_s32)]
        elif opcode == 0x4d:
            opcode_name = 'EXIT'
        elif opcode == 0x82:
            operands = get_operands2()
            if operand_pattern == 0x800:
                opcode_name = 'UMOV'
                operands[0].uniform = True
            else:
                opcode_name = 'LDC{}'.format('.64' if is64 else '')
        elif opcode == 0x86:
            opcode_name = 'STG.E.SYS'
            operands = get_operands2()
        elif opcode == 0x90:
            opcode_name = 'UIADD3'
            operands = get_operands4(all_uniform=True)
        elif opcode == 0xb9:
            opcode_name = 'ULDC{}'.format('.64' if is64 else '')
            operands = get_operands2()
            operands[0].uniform = True
        elif opcode == 0xc3:
            opcode_name = 'S2UR'
            operands = [Register(dst, uniform=True),
                        SpecialRegister(special_src)]
        else:
            raise Exception('Unknown opcode: {:#x}'.format(opcode))
    except Exception as err:
        return UnknownInstruction(offset, ctrl, err)

    return Instruction(offset, ctrl, predicate, opcode_name, operands)


def disasm(data):
    assert len(data) % 16 == 0

    instructions = []

    offset = 0
    for (lo, hi) in struct.iter_unpack('<QQ', data):
        instructions.append(_parse_instruction(offset, lo, hi))
        offset += 16

    return instructions
