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

from gpu_uarch.nv import Control, Register, Instruction, Immediate, ConstantMemory, Memory, Predicate
from lark import Lark, Visitor
import importlib.resources as pkg_resources

_grammar = Lark(pkg_resources.read_text(
    'gpu_uarch.nv', 'asm.lark'), start='instruction')


class SourceFile:
    def __init__(self, source):
        self.lines = []
        for line in source.split('\n'):
            line = line.strip()
            if line.startswith('#') or len(line) == 0:
                continue
            self.lines.append(line)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return SourceFile(f.read())

    class _InstructionBuilder(Visitor):
        def __init__(self):
            self.operands = []
            self.predicate_object = None

        def control(self, tree):
            self.control_object = Control.parse(
                [str(value) for value in tree.children])

        def _register(self, tree):
            assert tree.data == 'register'
            assert len(tree.children) == 1
            tree = tree.children[0]
            uniform = tree.data == 'uniform_register'
            idx = str(tree.children[0])
            return Register.parse(idx, uniform)

        def _immediate(self, tree):
            assert tree.data == 'immediate'
            token = tree.children[0]
            return Immediate(int(str(token), base=10 if token.type == 'DECIMAL' else 16))

        def _register_or_immediate(self, tree):
            if tree.data == 'register':
                return self._register(tree)
            else:
                return self._immediate(tree)

        def _predicate(self, tree, negated=False):
            idx = str(tree.children[0])
            return Predicate.parse(idx, negated)

        def predicate_neg_opt(self, tree):
            tree = tree.children[0]
            negated = False
            if tree.data == 'predicate_negated':
                tree = tree.children[0]
                negated = True
            self.predicate_object = self._predicate(tree, negated)

        def operand(self, tree):
            for op in tree.children:
                if op.data == 'register':
                    self.operands.append(self._register(op))
                elif op.data == 'immediate':
                    self.operands.append(self._immediate(op))
                elif op.data == 'constant_memory':
                    cbank = self._immediate(op.children[0])
                    caddr = self._register_or_immediate(op.children[1])
                    self.operands.append(ConstantMemory(cbank, caddr))
                elif op.data == 'memory':
                    base = self._register_or_immediate(op.children[0])
                    offset = Immediate(0)
                    if len(op.children) > 1:
                        offset = self._immediate(op.children[1])
                    self.operands.append(Memory(base, offset))
                else:
                    raise Exception('invalid subtree: {}'.format(tree))

        def opcode(self, tree):
            self.opcode_str = str(tree.children[0])

        def build(self, offset):
            return Instruction(offset, self.control_object, self.predicate_object, self.opcode_str, self.operands)

    def parse(self):
        # FIXME: verify sm_75
        offset = 0
        instructions = []
        for line in self.lines:
            tree = _grammar.parse(line)

            builder = self._InstructionBuilder()
            builder.visit(tree)
            instructions.append(builder.build(offset))
            offset += 16
        return instructions
