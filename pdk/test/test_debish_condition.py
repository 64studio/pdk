# $Progeny$
#
#   Copyright 2006 Progeny Linux Systems, Inc.
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

from pdk.test.utest_util import Test

from pdk.exceptions import InputError
from pdk.rules import ac, oc, rc, relrc, starc, star2c, notc
from pdk.debish_condition import compile_debish, DebishLex, \
     PeekableIterator
from pdk.package import deb, DebianVersion, src
from operator import eq, ge, lt

class TestPeekableIterator(Test):
    def test_peek(self):
        raw = iter([1, 2, 3])
        peekable = PeekableIterator(raw)
        self.assert_equal(1, peekable.next())
        self.assert_equal(2, peekable.peek())
        self.assert_equal(2, peekable.next())
        self.assert_equal(3, peekable.next())

    def test_peek_n(self):
        raw = iter([1, 2, 3])
        peekable = PeekableIterator(raw)
        self.assert_equal(1, peekable.peek(0))
        self.assert_equal(2, peekable.peek(1))
        self.assert_equal(1, peekable.next())
        self.assert_equal(2, peekable.peek(0))
        self.assert_equal(3, peekable.peek(1))
        self.assert_equal(2, peekable.next())
        self.assert_equal(3, peekable.next())


class TestDebishLex(Test):
    def test_lex(self):
        lex = DebishLex('name')
        self.assert_equal(('start', None), lex.next())
        self.assert_equal(0, lex.index)
        self.assert_equal(('word', 'name'), lex.next())
        self.assert_equal(0, lex.index)
        self.assert_equal(('end', None), lex.next())
        self.assert_equal(4, lex.index)

        lex = DebishLex(' name ')
        self.assert_equal(('start', None), lex.next())
        self.assert_equal(0, lex.index)
        self.assert_equal(('word', 'name'), lex.next())
        self.assert_equal(1, lex.index)
        self.assert_equal(('end', None), lex.next())
        self.assert_equal(5, lex.index)

class TestDebishCondition(Test):
    def test_assert_error(self):
        try:
            compile_debish('apache )', None, None)
            self.fail('error should happen on invalid expressions')
        except InputError, error:
            message = str(error)
            expected_message = '''apache >>>)
Expected end, got ) at character 7'''
            self.assert_equals(expected_message, message)

    def test_marked_condition(self):
        debish = 'apache (=3) [i386]'
        condition = compile_debish(debish, deb, None)
        self.assert_equals(debish, condition.debish)

    def test_name_only(self):
        actual = compile_debish('apache', None, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache')])
        self.assert_equals(expected, actual)

    def test_name_version(self):
        actual = compile_debish('apache (=2.0-1)', deb, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       rc(eq, 'pdk', 'version', DebianVersion('2.0-1'))])
        wrapper = ac([expected,
                      rc(eq, 'pdk', 'type', 'deb')])
        self.assert_equals(wrapper, actual)

    def test_untyped_version(self):
        actual = compile_debish('apache (=2.0-1)', None, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       rc(eq, 'pdk', 'version', '2.0-1')])
        self.assert_equals(expected, actual)

    def test_name_arch(self):
        actual = compile_debish('apache [i386 amd64]', deb, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       oc([rc(eq, 'deb', 'arch', 'i386'),
                           rc(eq, 'deb', 'arch', 'amd64')])])
        wrapper = ac([expected,
                      rc(eq, 'pdk', 'type', 'deb')])
        self.assert_equals(wrapper, actual)

    def test_name_other(self):
        actual = compile_debish('apache {a:b = c dd:ee>=fgh i=j}', deb,
                                None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       ac([rc(eq, 'a', 'b', 'c'),
                           rc(ge, 'dd', 'ee', 'fgh'),
                           rc(eq, 'pdk', 'i', 'j')])])
        wrapper = ac([expected,
                      rc(eq, 'pdk', 'type', 'deb')])
        self.assert_equals(wrapper, actual)

    def test_relaxed_relation(self):
        actual = compile_debish('apache {a:b %= c}', None, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       ac([relrc(eq, 'a', 'b', 'c')])])
        self.assert_equals(expected, actual)

    def test_or(self):
        actual = compile_debish('apache | apache2', None, None)
        expected = oc([ac([rc(eq, 'pdk', 'name', 'apache')]),
                       ac([rc(eq, 'pdk', 'name', 'apache2')])])
        self.assert_equals(expected, actual)

    def test_version_range(self):
        actual = compile_debish('apache (>=2.0-1 << 3)', deb, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       rc(ge, 'pdk', 'version', DebianVersion('2.0-1')),
                       rc(lt, 'pdk', 'version', DebianVersion('3'))])
        wrapper = ac([expected,
                      rc(eq, 'pdk', 'type', 'deb')])
        self.assert_equals(wrapper, actual)

    def test_star(self):
        actual = compile_debish('* apache | apache2', None, None)
        expected = starc(oc([ac([rc(eq, 'pdk', 'name', 'apache')]),
                             ac([rc(eq, 'pdk', 'name', 'apache2')])]))
        self.assert_equals(expected, actual)

    def test_star2(self):
        actual = compile_debish('** apache | apache2', None, None)
        expected = star2c(oc([ac([rc(eq, 'pdk', 'name', 'apache')]),
                             ac([rc(eq, 'pdk', 'name', 'apache2')])]))
        self.assert_equals(expected, actual)


    def test_not_arch(self):
        actual = compile_debish('apache [!i386 !amd64]', deb, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       notc(oc([rc(eq, 'deb', 'arch', 'i386'),
                                rc(eq, 'deb', 'arch', 'amd64')]))])
        wrapper = ac([expected,
                      rc(eq, 'pdk', 'type', 'deb')])
        self.assert_equals(wrapper, actual)

    def test_term_with_blob_id(self):
        actual = compile_debish('apache (=2.0-1)', deb, 'sha-1:aaa')
        expected = ac([rc(eq, 'pdk', 'name', 'apache'),
                       rc(eq, 'pdk', 'version', DebianVersion('2.0-1'))])
        wrapper = ac([rc(eq, 'pdk', 'blob-id', 'sha-1:aaa'),
                      expected,
                      rc(eq, 'pdk', 'type', 'deb')])
        self.assert_equals(wrapper, actual)

    def test_build_general_debish_ref(self):
        actual = compile_debish('apache', src, None)
        expected = ac([rc(eq, 'pdk', 'name', 'apache')])
        wrapper = ac([expected,
                      rc(eq, 'pdk', 'role', 'source')])
        self.assert_equals(wrapper, actual)

# vim:set ai et sw=4 ts=4 tw=75:
