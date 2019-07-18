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
import tests.cuobjdump


class TestNvTuringDisassemblyCuObjDump(unittest.TestCase):
    pass


def make_test(name):
    @unittest.skipUnless(tests.cuobjdump.available(), 'cuobjdump not available')
    def test(self):
        pkg = __package__ + '.nv_turing'
        cubin = '{}.cubin'.format(name)
        with pkg_resources.path(pkg, cubin) as bin:
            bin_out = gpu_uarch.nv.cubin.CuBin(bin).functions[0].disasm()
            cuobjdump_out = tests.cuobjdump.disasm(bin)
            self.assertEqual(bin_out, cuobjdump_out)
    return test


test_cases = [
    'simple_o0',
    #'simple_o3', #FIXME: suffix differences
]
for name in test_cases:
    setattr(TestNvTuringDisassemblyCuObjDump,
            'test_{}'.format(name), make_test(name))

if __name__ == '__main__':
    unittest.main()
