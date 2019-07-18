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

import gpu_uarch.nv.source as source
from gpu_uarch.nv import (Instruction, Register, Control, ConstantMemory,
                          Immediate, Predicate, Memory)
import unittest


class TestNvTuringAssembly(unittest.TestCase):
    pass


test_cases = [
    ('mov_r_r', '--:-:-:-:4 MOV R0, RZ', [Instruction(0, Control.parse(
        ['--', '-', '-', '-', '4']), None, 'MOV', [Register(0), Register(255)])]),
    ('mov_r_c', '--:-:0:-:f MOV R1, c[0][0x123]', [Instruction(0, Control.parse(
                ['--', '-', '0', '-', 'f']), None, 'MOV', [Register(1), ConstantMemory(Immediate(0), Immediate(0x123))])]),
    ('p0_mov_r_c', '--:-:-:Y:1 P0 MOV R0, c[0x0][0x16c]', [Instruction(0, Control.parse(
        ['--', '-', '-', 'Y', '1']), Predicate(0), 'MOV', [Register(0), ConstantMemory(Immediate(0), Immediate(0x16c))])]),
    ('np0_mov_r_c', '--:-:-:Y:1 !P0 MOV R0, c[0x0][0x168]', [Instruction(0, Control.parse(
        ['--', '-', '-', 'Y', '1']), Predicate(0, negated=True), 'MOV', [Register(0), ConstantMemory(Immediate(0), Immediate(0x168))])]),
    ('stg_ro_r', '--:-:0:Y:1 STG.E.SYS [R1+4], R0', [Instruction(0, Control.parse(
        ['--', '-', '0', 'Y', '1']), None, 'STG.E.SYS', [Memory(Register(1), Immediate(4)), Register(0)])]),
    ('exit', '01:-:-:Y:5 EXIT',
     [Instruction(0, Control.parse(['01', '-', '-', 'Y', '5']), None, 'EXIT', [])]),
    ('mov_r_i', '03:-:-:-:f MOV R2, 0x160', [Instruction(0, Control.parse(
        ['03', '-', '-', '-', 'f']), None, 'MOV', [Register(2), Immediate(0x160)])])
]


def make_test(input, output):
    def test(self):
        actual = source.SourceFile(input).parse()
        expected = output
        self.assertEqual(actual, expected)
    return test


for (name, input, output) in test_cases:
    setattr(TestNvTuringAssembly, 'test_{}'.format(
        name), make_test(input, output))

if __name__ == '__main__':
    unittest.main()
