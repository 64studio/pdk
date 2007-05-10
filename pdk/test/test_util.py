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

from StringIO import StringIO as stringio
from pdk.test.utest_util import Test
from cElementTree import ElementTree, Element, SubElement, Comment, \
     ProcessingInstruction

from pdk.util import split_pipe, gen_fragments, default_block_size, \
     write_pretty_xml, parse_xml, NullTerminated, parse_domain, \
     string_domain

__revision__ = "$Progeny$"

class TestParseDomain(Test):
    def test_parse_domain(self):
        pd = parse_domain
        self.assert_equal(('pdk', 'zz'), pd('zz'))
        self.assert_equal(('deb', 'name'), pd('deb.name'))
        self.assert_equal(('deb', 'deb.name'), pd('deb.deb.name'))

    def test_string_domain(self):
        sd = string_domain
        self.assert_equal('zz', sd('', 'zz'))
        self.assert_equal('zz', sd('pdk', 'zz'))
        self.assert_equal('a.b', sd('a', 'b'))

class TestNullTerminated(Test):
    def test_null_terminated(self):
        underlying = 'abc\ndef\0fgh\0ijk\0'
        handle = stringio(underlying)
        self.assert_equal(['abc\ndef', 'fgh', 'ijk'],
                          list(NullTerminated(handle)))

    def test_null_terminated_missing_last(self):
        underlying = 'abc\ndef\0fgh\0ijk'
        handle = stringio(underlying)
        self.assert_equal(['abc\ndef', 'fgh', 'ijk'],
                          list(NullTerminated(handle)))

    def test_over_block_size(self):
        underlying = 'abc\ndef\0fgh\0ijk'
        handle = stringio(underlying)
        self.assert_equal(['abc\ndef', 'fgh', 'ijk'],
                          list(NullTerminated(handle, 5)))

    def test_terminator_at_block_end(self):
        underlying = 'abc\ndef\0fgh\0ijk'
        handle = stringio(underlying)
        self.assert_equal(['abc\ndef', 'fgh', 'ijk'],
                          list(NullTerminated(handle, 8)))

    def test_zero_length(self):
        underlying = 'abc\ndef\0\0fgh\0ijk'
        handle = stringio(underlying)
        self.assert_equal(['abc\ndef', '', 'fgh', 'ijk'],
                          list(NullTerminated(handle)))


class TestSplitPipe(Test):
    def test_split(self):
        data = '''a|b
a|c
b|b
b|c

b|d
c|zaa
a|z
local:/z|asdfjkl;
local:/z|qwerty
'''
        handle = stringio(data)
        expected = {'a': ['b', 'c', 'z'],
                    'b': ['b', 'c', 'd'],
                    'c': ['zaa'],
                    'local:/z': ['asdfjkl;', 'qwerty'] }
        self.assert_equal(expected, split_pipe(handle))

class TestGenFragments(Test):
    def test_size(self):
        data = default_block_size * 2 * '.'
        self.assert_equal(['....'], list(gen_fragments(stringio(data), 4)))

        expected = [ default_block_size * '.', '..' ]
        actual = list(gen_fragments(stringio(data),
                                    default_block_size + 2))
        assert expected == actual

    def test_nosize(self):
        block = default_block_size * '.'
        data = block + block
        actual = list(gen_fragments(stringio(data)))
        assert [block, block] == actual

        data = block + '...'
        actual = list(gen_fragments(stringio(data)))
        assert [block, '...'] == actual

expected_xml_output = '''<?xml version="1.0" encoding="utf-8"?>
<a>
  <b>
    <!--a comment-->
    <c d="e">
      <f>g</f>
      <h><![CDATA[i << >> << &&]]></h>
    </c>
    <?pdk processing instruction?>
  </b>
</a>
'''

class TestXML(Test):
    def test_writer(self):
        a = Element('a')
        b = SubElement(a, 'b')
        b.append(Comment('a comment'))
        c = SubElement(b, 'c', d = 'e')
        f = SubElement(c, 'f')
        f.text = 'g'
        h = SubElement(c, 'h')
        h.text = 'i << >> << &&'
        b.append(ProcessingInstruction('pdk', 'processing instruction'))
        tree = ElementTree(a)
        output = stringio()
        write_pretty_xml(tree, output)
        self.assert_equals_long(expected_xml_output, output.getvalue())

    def test_xml_read_then_write(self):
        tree = parse_xml(stringio(expected_xml_output))
        output = stringio()
        write_pretty_xml(tree, output)
        self.assert_equals_long(expected_xml_output, output.getvalue())

# vim:set ai et sw=4 ts=4 tw=75:
