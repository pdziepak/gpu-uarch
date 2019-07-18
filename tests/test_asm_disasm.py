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

import gpu_uarch.nv.cubin
import gpu_uarch.nv.source
import unittest
import importlib.resources as pkg_resources


class TestNvTuringAssemblyDisassembly(unittest.TestCase):
    pass


def make_test(name):
    def test(self):
        pkg = __package__ + '.nv_turing'
        cubin = '{}.cubin'.format(name)
        txt = '{}.txt'.format(name)
        with pkg_resources.path(pkg, cubin) as bin, pkg_resources.path(pkg, txt) as src:
            bin_out = gpu_uarch.nv.cubin.CuBin(bin).functions[0].disasm()
            src_out = gpu_uarch.nv.source.SourceFile.load(src).parse()
            self.assertEqual(src_out, bin_out)
    return test


test_cases = [
    'simple_o0',
    'simple_o3',
]
for name in test_cases:
    setattr(TestNvTuringAssemblyDisassembly,
            'test_{}'.format(name), make_test(name))

if __name__ == '__main__':
    unittest.main()
