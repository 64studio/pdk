# $Progeny$
#
#   Copyright 2005 Progeny Linux Systems, Inc.
#
#   This file is part of PDK.
#
#   PDK is free software; you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   PDK is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
#   License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PDK; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from cStringIO import StringIO
from pdk.test.utest_util import Test

from pdk.progress import ConsoleProgress, CurlAdapter, SizeCallbackAdapter

class MockProgress(object):
    def __init__(self):
        self.__data = []
        self.__active = False

    def __getattr__(self, attribute):
        if self.__active:
            def _cmp(*args):
                given = self.__data.pop(0)
                other = (attribute, args)
                assert given == other, \
                    'expected %r, got %r' % (given, other)
            return _cmp
        else:
            def _note(*args):
                self.__data.append((attribute, args))
            return _note

    def activate(self):
        self.__active = True

    def verify(self):
        assert len(self.__data) == 0, \
            'some calls were not made, %r' % self.__data

class TestSizeCallbackAdapter(Test):
    def test_multicall(self):
        progress = MockProgress()
        progress.write_bar(20, 10)
        progress.write_bar(20, 20)
        progress.activate()

        handler = SizeCallbackAdapter(progress, 20)
        handler(10)
        handler(10)
        progress.verify()

class TestCurlAdapter(Test):
    def test_multicall(self):
        progress = MockProgress()
        progress.write_bar(2.0, 1.0)
        progress.write_bar(2.0, 2.0)
        progress.activate()

        handler = CurlAdapter(progress)
        handler.callback(0.0, 0.0, 2.0, 1.0)
        handler.callback(0.0, 0.0, 2.0, 2.0)
        progress.verify()

    def test_unbounded(self):
        progress = MockProgress()
        progress.write_spin()
        progress.write_spin()
        progress.write_spin()
        progress.activate()

        handler = CurlAdapter(progress)
        handler.callback(0.0, 0.0, 0.0, 1.0)
        handler.callback(0.0, 0.0, 0.0, 2.0)
        handler.callback(0.0, 0.0, 0.0, 3.0)
        progress.verify()


class TestConsoleProgress(Test):
    def test_start(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.start()
        expected = 'some name\n'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_no_name(self):
        output = StringIO()
        progress = ConsoleProgress(None, output)
        progress.start()
        expected = ''
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_done(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.done()
        expected = '\n'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_update(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.write_bar(2, 1)
        expected = '|' + (30 * '=') + (30 * ' ' ) + '|\r'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_zero(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.write_bar(2, 0)
        expected = '|' + (60 * ' ' ) + '|\r'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_full(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.write_bar(2, 2)
        expected = '|' + (60 * '=') + '|\r'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_underflow(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.write_bar(2, -1)
        expected = '|' + (60 * ' ' ) + '|\r'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_overflow(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.write_bar(2, 4)
        expected = '|' + (60 * '=') + '|\r'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

    def test_spin(self):
        output = StringIO()
        progress = ConsoleProgress('some name', output)
        progress.write_spin()
        progress.write_spin()
        expected = ''
        expected += '|' + (60 * '-') + '|\r'
        expected += '|' + (60 * '+') + '|\r'
        self.assert_equals_long(repr(expected), repr(output.getvalue()))

# vim:set ai et sw=4 ts=4 tw=75:
