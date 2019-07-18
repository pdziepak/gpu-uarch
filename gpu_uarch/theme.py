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

from sty import fg, ef, rs


class NoTheme:
    def __init__(self):
        self.control_active = ''
        self.control_inactive = ''
        self.constant = ''
        self.error = ''
        self.function = ''
        self.immediate = ''
        self.offset = ''
        self.opcode = ''
        self.predicate = ''
        self.register = ''
        self.rs = ''
        self.special_register = ''
        self.symbol = ''


class SolarizedTheme:
    def __init__(self):
        self.control_active = fg(0xb5, 0x89, 0x00)
        self.control_inactive = fg(0x58, 0x6e, 0x75)
        self.constant = fg(0xb5, 0x89, 0x00)
        self.error = fg(0xdc, 0x32, 0x2f)
        self.function = ef.underl
        self.immediate = fg(0xcb, 0x4b, 0x16)
        self.offset = fg(0x58, 0x6e, 0x75)
        self.opcode = fg(0xd3, 0x36, 0x82)
        self.predicate = fg(0x2a, 0xa1, 0x98)
        self.register = fg(0x6c, 0x71, 0xc4)
        self.rs = rs.all
        self.special_register = fg(0x85, 0x99, 0x00)
        self.symbol = fg(0x26, 0x8b, 0xd2)


_theme = NoTheme()


def set_theme(t):
    global _theme
    _theme = t


def get_theme():
    return _theme
