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

import gpu_uarch.theme


class Immediate:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{theme.immediate}{:#x}{theme.rs}'.format(self.value, theme=theme)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value


class Register:
    def __init__(self, index, uniform=False, reuse=False):
        self.index = index
        self.uniform = uniform
        self.reuse = reuse

    @staticmethod
    def parse(index, uniform):
        if index == 'Z':
            index = 255 if not uniform else 63
        else:
            index = int(index)
        return Register(index, uniform)

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{theme.register}{}R{}{theme.rs}'.format('U' if self.uniform else '', str(
            self.index) if not self.index == (255 if not self.uniform else 63) else 'Z',
            theme=theme)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.index == other.index
                and self.uniform == other.uniform
                and self.reuse == other.reuse)


class SpecialRegister:
    NAMES = {0x2100: 'SR_TID.X', 0x2500: 'SR_CTAID.X', 0x5000: 'SR_CLOCKLO'}

    def __init__(self, index):
        self.index = index

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        try:
            return '{theme.special_register}{}{theme.rs}'.format(self.NAMES[self.index],
                                                                 theme=theme)
        except Exception:
            return '{theme.error}<unknown special register {:#x}>{theme.rs}'.format(
                self.index, theme=theme)

    def __eq__(self, other):
        return type(self) == type(other) and self.index == other.index


class ConstantMemory:
    def __init__(self, bank, address):
        self.bank = bank
        self.address = address

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{theme.constant}c{theme.symbol}[{}{theme.symbol}][{}{theme.symbol}]{theme.rs}'.format(
            self.bank, self.address, theme=theme)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.bank == other.bank
                and self.address == other.address)


class Memory:
    def __init__(self, address, offset):
        self.address = address
        self.offset = offset

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        if self.offset.value == 0:
            return '{theme.symbol}[{}{theme.symbol}]{theme.rs}'.format(self.address, theme=theme)
        else:
            return '{theme.symbol}[{}{theme.symbol}+{}{theme.symbol}]{theme.rs}'.format(
                self.address, self.offset, theme=theme)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.address == other.address
                and self.offset == other.offset)


class Control:
    def __init__(self, hi):
        ctrl = hi >> 41

        self.stall = ctrl & 0xf
        self.yield_hint = not ctrl & 0x10 == 0
        self.wr_barrier = (ctrl >> 5) & 0x7
        self.rd_barrier = (ctrl >> 8) & 0x7
        self.wait_mask = (ctrl >> 11) & 0x3f
        self.reuse_flags = (ctrl >> 17) & 0xf

    @staticmethod
    def parse(elements):
        assert len(elements) == 5
        ctrl = Control(0)
        ctrl.wait_mask = 0 if elements[0] == '--' else int(elements[0])
        ctrl.rd_barrier = 7 if elements[1] == '-' else int(elements[1])
        ctrl.wr_barrier = 7 if elements[2] == '-' else int(elements[2])
        ctrl.yield_hint = elements[3] == 'Y'
        ctrl.stall = int(elements[4], base=16)
        return ctrl

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{}{theme.symbol}:{}{theme.symbol}:{}{theme.symbol}:{}{theme.symbol}:{theme.control_active}{:x}{theme.rs}'.format(
            theme.control_inactive + '--' if self.wait_mask == 0 else theme.control_active +
            '{:02x}'.format(self.wait_mask),
            theme.control_inactive + '-' if self.rd_barrier == 7 else theme.control_active + str(
                self.rd_barrier),
            theme.control_inactive + '-' if self.wr_barrier == 7 else theme.control_active + str(
                self.wr_barrier),
            theme.control_active + 'Y' if self.yield_hint else theme.control_inactive + '-',
            self.stall, theme=theme)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.stall == other.stall
                and self.yield_hint == other.yield_hint
                and self.wr_barrier == other.wr_barrier
                and self.rd_barrier == other.rd_barrier
                and self.wait_mask == other.wait_mask
                and self.reuse_flags == other.reuse_flags)


class Predicate:
    def __init__(self, index, negated=False):
        self.index = index
        self.negated = negated

    @staticmethod
    def parse(index, negated):
        if index == 'T':
            index = 7
        else:
            index = int(index)
        return Predicate(index, negated)

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{theme.predicate}{}P{}{theme.rs}'.format('!' if self.negated else '',
                                                         self.index, theme=theme)

    def __eq__(self, other):
        return type(self) == type(other) and self.index == other.index and self.negated == other.negated


class Instruction:
    def __init__(self, offset, control, predicate, opcode, operands):
        self.offset = offset
        self.control = control
        self.predicate = predicate
        self.opcode = opcode
        self.operands = operands

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{theme.offset}{:#010x}{theme.rs}  {}  {} {theme.opcode}{}{theme.rs} {}'.format(
            self.offset, self.control, '   ' if not self.predicate else (
                ('' if self.predicate.negated else ' ') + str(self.predicate)), self.opcode,
            '{theme.symbol},{theme.rs} '.format(theme=theme).join(
                ['{}'.format(op) for op in self.operands]) if self.operands else '',
            theme=theme)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.offset == other.offset
                and self.control == other.control
                and self.predicate == other.predicate
                and self.opcode == other.opcode
                and self.operands == other.operands)


class UnknownInstruction:
    def __init__(self, offset, control, error):
        self.offset = offset
        self.control = control
        self.error = error

    def __repr__(self):
        theme = gpu_uarch.theme.get_theme()
        return '{theme.offset}{:#010x}{theme.rs}  {}      {theme.error}<unknown instruction: {}>{theme.rs}'.format(
            self.offset, self.control, self.error, theme=theme)
