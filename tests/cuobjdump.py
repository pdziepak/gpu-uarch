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

import subprocess
import re
import gpu_uarch.nv.source
from gpu_uarch.nv import Control


def available():
    result = subprocess.run(
        'cuobjdump --help', shell=True, capture_output=True)
    return result.returncode == 0


def disasm(cubin_file):
    result = subprocess.run(
        'cuobjdump --dump-sass {}'.format(cubin_file), shell=True, capture_output=True)
    assert result.returncode == 0

    out = result.stdout.decode().split('\n')

    lo_re = re.compile(
        r'\/\*[\da-f]+\*\/\s+([^\;]+)\;\s+\/\*\s*0x([\da-f]+)\s*\*\/')
    hi_re = re.compile(r'\s+\/\*\s*0x([\da-f]+)\s*\*\/')

    src = []
    instruction = None

    for line in out:
        hi_match = hi_re.match(line)
        if hi_match:
            src.append('{} {}'.format(
                Control(int(hi_match[1], base=16)), instruction))
            continue

        lo_match = lo_re.search(line)
        if lo_match:
            instruction = lo_match[1]
            continue

    return gpu_uarch.nv.source.SourceFile('\n'.join(src)).parse()
