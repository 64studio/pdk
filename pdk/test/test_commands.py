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
from pdk.command_base import Commands, CommandInvoker, HelpInvoker, \
     CommandArgs, HelpMultiInvoker, DirectCommand, gescape, gbold, \
     gitalic, make_invokable, CommandAlias

__revision__ = "$Progeny$"

def dummy_function1():
    '''test doc 1'''
    pass

dummy_function1 = make_invokable(dummy_function1)

def dummy_function2():
    '''test doc 2'''
    pass

dummy_function2 = make_invokable(dummy_function2)

def dummy_function3():
    '''test doc 3'''
    pass

dummy_function3 = make_invokable(dummy_function3)

local_module = __name__

class TestCommands(Test):
    def test_find(self):
        com = Commands('aaa')
        com.easy_map('a', local_module, 'dummy_function1')
        com.map_direct(['d'], dummy_function2)
        com.map(['g', 'h'], DirectCommand(dummy_function3))
        com.alias(['z', 'y'], ['g', 'h'])

        def ci(function, args):
            return CommandInvoker('aaa', function, CommandArgs(None, args))
        hi = HelpInvoker
        hmi = HelpMultiInvoker

        self.assert_equal(ci(dummy_function1, ['1', '2', '3']),
                          com.find(['a', '1', '2', '3']))
        self.assert_equal(ci(dummy_function3, ['1', '2', '3']),
                          com.find(['g', 'h', '1', '2', '3']))
        self.assert_equal(ci(dummy_function3, ['1', '2', '3']),
                          com.find(['z', 'y', '1', '2', '3']))
        self.assert_equal(hi(['aaa', 'a'], dummy_function1),
                          com.find(['help', 'a', '1', '2', '3']))
        self.assert_equal(hi(['aaa', 'g', 'h'], dummy_function3),
                          com.find(['g', 'help', 'h', '1', '2', '3']))
        self.assert_equal(hmi(['aaa', 'g'], com.commands['g']),
                          com.find(['help', 'g', '1', '2', '3']))
        self.assert_equal(hmi(['aaa', 'g'], com.commands['g']),
                          com.find(['g']))
        self.assert_equal(ci(dummy_function2, ['1', '2', '3']),
                          com.find(['d', '1', '2', '3']))

        try:
            com.find(['zzzzzz'])
        except InputError:
            pass
        else:
            self.fail('Should have thrown InputError!')

    def test_iterate(self):
        commands = Commands('base')
        command = DirectCommand(dummy_function2)
        commands.map(['a'], command)
        commands.map(['b', 'c'], command)
        commands.map(['d'], command)
        commands.map(['e', 'f', 'g'], command)
        commands.alias(['zz', 'yy'], ['a'])

        expected = [
            (('base', 'a'), DirectCommand(dummy_function2)),
            (('base', 'b', 'c'), DirectCommand(dummy_function2)),
            (('base', 'd'), DirectCommand(dummy_function2)),
            (('base', 'e', 'f', 'g'), DirectCommand(dummy_function2)),
            (('base', 'zz', 'yy'), CommandAlias(commands, ['a'])) ]

        self.assert_equals_long(expected, list(commands))

    def test_groff(self):
        self.assert_equals(r'\"hello.\\.\-\-', gescape(r'"hello.\\.--'))
        self.assert_equals(r'\fBhello \-\fP', gbold('hello -'))
        self.assert_equals(r'\fIhello \-\fP', gitalic('hello -'))

# vim:set ai et sw=4 ts=4 tw=75:
