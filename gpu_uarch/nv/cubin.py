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

import cxxfilt
from elftools.elf.elffile import ELFFile

import gpu_uarch.nv.turing as turing


class Function:
    def __init__(self, symbol, data):
        self.symbol = symbol
        self.name = cxxfilt.demangle(symbol)
        self.data = data

    def disasm(self):
        # FIXME: verify sm_75
        return turing.disasm(self.data)


class CuBin:
    def __init__(self, filename):
        self.functions = []
        with open(filename, 'rb') as f:
            e = ELFFile(f)
            for section in e.iter_sections():
                if section.name.startswith('.text.'):
                    self.functions.append(
                        Function(section.name[6:], section.data()))
