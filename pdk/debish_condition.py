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

'''
This module defines a mini-language used to construct conditions.

It roughly follows Debian's language used to describe build dependencies.

Use compile_debish(string, package_type) to get a condition from a string
describing a debish condition.

The condition is marked with attribute "debish" which is filled in with
the original string.

Example conditions:

apache2 (>>2)
apache2 (=2.0.53-7) [i386 amd64]
linux [i386] { mediagen:include = 1 }
* apache2 (>=2.0.54 <<3)

Star conditions match the "complement" of the package that matches. So if
a condition matches binary packages, a star refers to the sources of those
binaries. Likewise, the complement of a source package is it's binaries.


'''

from pdk.exceptions import InputError
from pdk.rules import ac, oc, rc, relrc, starc, star2c, notc
from operator import gt, lt, ge, le, eq
from mx.TextTools import tag, whitespace, IsNotIn, AllNotIn, AllIn, Is, \
     IsIn, Table, MatchOk, EOF, Here

class PeekableIterator(object):
    '''A utility class which allows us to peek at future iterator items.

    Wraps up an iterable object and provides a peek method.

    Normally behaves as an iterator but also has a peek method which
    behaves like next, without (apparently) changing the state of the
    iterator.

    Really next() is called on the wrapped iterator and peeked items are
    buffered until our next() method is called.

    Peek optional takes an integer which specifies how deep in the iterator
    to peek.

    iterator    - The iterator to wrap and buffer.
    '''
    def __init__(self, iterator):
        self.iter = iterator
        self.buffer = []

    def __iter__(self):
        return self

    def next(self):
        '''Return the the next item from the iterator.'''
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return self.iter.next()

    def peek(self, index = 0):
        '''Peek at the next item from the iterator.

        index   - peek at the index-th item in the iterator
        '''
        for dummy in xrange(0, index - len(self.buffer) + 1):
            self.buffer.append(self.iter.next())
        return self.buffer[index]

def compile_debish(debish, package_type, blob_id):
    '''Compile the string debish to a condition.

    package_type    - used for constructing version objects and arch
                      fields.
    blob_id         - work a match on this blob_id into the condition such
                      that it is check "early" in the match process.
    '''
    lex = DebishLex(debish)
    parser = DebishParser(package_type, blob_id)
    condition = parser.parse(lex)
    condition.debish = debish
    return condition

# taglists for mx.TextTools

not_word = '()[]{}=<>|*!%'

word = (('a', IsNotIn, whitespace + not_word),
        ('b', AllNotIn, whitespace + not_word, MatchOk))

op = ((None, Is, '%', +1),
      (None, Is, '=', +1, MatchOk),
      (None, IsIn, '<>'),
      (None, IsIn, '<=>', MatchOk))

tags = (('word', Table, word, +1),
        ('(', Is, '(', +1),
        ('op', Table, op, +1),
        (')', Is, ')', +1),
        ('[', Is, '[', +1),
        (']', Is, ']', +1),
        ('{', Is, '{', +1),
        ('}', Is, '}', +1),
        ('|', Is, '|', +1),
        ('*', Is, '*', +1),
        ('!', Is, '!', +1),
        (None, AllIn, whitespace, +1),
        (None, EOF, Here, -12))

def raw_debish_lex(input_string):
    '''Used internally to generate a series of lexer states.'''
    end = 0
    yield 'start', None, 0
    result = tag(input_string, tags)
    taglist = result[1]
    for tag_type, start, end, dummy in taglist:
        yield tag_type, input_string[start:end], start
    yield 'end', None, end

class DebishLex(object):
    '''Do lexical analysis on a debish condition.

    Iterates over states of type (token_type, token).

    input_string    - debish condition to do lexical analysis on

    self.index      - Current position in the input_string.
    '''
    def __init__(self, input_string):
        self.input_string = input_string
        # Making the lexer peekable seems to expand the capabilities of
        # recursive decent tremendously.
        self.iterator = PeekableIterator(raw_debish_lex(input_string))
        self.index = None

    def __iter__(self):
        return self

    def next(self):
        '''Returns (token_type, token) and updates self.index'''
        tag_type, token, index = self.iterator.next()
        self.index = index
        return tag_type, token

    def peek(self, index = 0):
        '''Peeks at the next lexer state; does not update index.'''
        token_tuple = self.iterator.peek(index)
        return token_tuple[0], token_tuple[1]

op_map = {'=' : (rc, eq),
          '>>': (rc, gt),
          '>=': (rc, ge),
          '<<': (rc, lt),
          '<=': (rc, le),
          '%=' : (relrc, eq),
          '%>>': (relrc, gt),
          '%>=': (relrc, ge),
          '%<<': (relrc, lt),
          '%<=': (relrc, le) }

def format_error_messaage(lex, message):
    '''Create a useful error message regarding a debish condition.

    Given that lex.next() has produced an unexpeced token, show the current
    position of the lexer in a visual way and include the message.
    '''
    return '%s>>>%s\n%s' \
           % (lex.input_string[:lex.index], lex.input_string[lex.index:],
              message)

class DebishParser(object):
    '''Do actual parsing and translation of a debish lexer to a condition.

    package_type    - used for constructing version strings and arch
                      conditions.
    '''
    def __init__(self, package_type, blob_id):
        self.package_type = package_type
        if self.package_type:
            self.version_class = self.package_type.version_class
        else:
            self.version_class = str
        self.blob_id = blob_id


    def assert_type(self, lex, expected):
        '''Insist that the lexer produce a token of an expected type.

        Returns the token value.
        '''
        actual, token = lex.next()
        if expected != actual:
            message = 'Expected %s, got %s at character %d' \
                      % (expected, actual, lex.index)
            raise InputError, format_error_messaage(lex, message)

        return token

    def parse(self, lex):
        '''Entry point to the parser.

        lex     - A freshly constructed DebishLexer.
        '''
        try:
            self.assert_type(lex, 'start')
            name = self.parse_star(lex)
            self.assert_type(lex, 'end')
        except StopIteration:
            message = 'Premature lexer end. Should not happen'
            raise AssertionError, \
                  format_error_messaage(lex, message)

        return name

    def wrap_condition(self, condition):
        '''Wrap the condition to verify the package_type and blob_id.

        Return the original condition of neither are given.
        '''
        if self.blob_id or self.package_type:
            wrapper = ac([])
            conditions = wrapper.conditions
            if self.blob_id:
                conditions.append(rc(eq, 'pdk', 'blob-id', self.blob_id))
            conditions.append(condition)
            if self.package_type:
                if self.package_type.format_string == 'unknown':
                    role_string = self.package_type.role_string
                    conditions.append(rc(eq, 'pdk', 'role', role_string))
                else:
                    type_string = self.package_type.type_string
                    conditions.append(rc(eq, 'pdk', 'type', type_string))
            return wrapper
        else:
            return condition

    def parse_star(self, lex):
        token_type, dummy = lex.peek()
        if token_type == '*':
            self.assert_type(lex, '*')
            token_type, dummy = lex.peek()
            if token_type == '*':
                self.assert_type(lex, '*')
                star = 2
            else:
                star = 1
        else:
            star = 0

        condition = self.wrap_condition(self.parse_or(lex))

        # here is where we plug in the blob_id and package_type
        if star == 1:
            return starc(condition)
        elif star == 2:
            return star2c(condition)
        else:
            return condition

    def parse_or(self, lex):
        terms = []
        while 1:
            term = self.parse_term(lex)
            terms.append(term)
            token_type, dummy = lex.peek()
            if token_type == '|':
                self.assert_type(lex, '|')
            else:
                break

        if len(terms) == 1:
            return terms[0]
        else:
            return oc(terms)

    def parse_term(self, lex):
        # this method does most of the heavy listing.
        condition = ac([])
        conditions = condition.conditions

        # optional first word is a package name
        token_type, dummy = lex.peek()
        if token_type == 'word':
            dummy, name = lex.next()
            conditions.append(rc(eq, 'pdk', 'name', name))

        # followed by an optional () containing 1 or more version relations
        token_type, dummy = lex.peek()
        if token_type == '(':
            self.assert_type(lex, '(')
            while 1:
                rel_type, op_func = self.parse_op(lex)
                version_str = self.assert_type(lex, 'word')
                version = self.version_class(version_str)
                conditions.append(rel_type(op_func, 'pdk', 'version',
                                           version))
                token_type, dummy = lex.peek()
                if token_type == ')':
                    self.assert_type(lex, ')')
                    break

        # followed by an optional [] containing 1 or more arch conditions
        # These can be marked with ! meaning not. They must all be marked
        # or unmarked with !.
        token_type, dummy = lex.peek()
        if token_type == '[':
            self.assert_type(lex, '[')
            or_condition = oc([])
            or_conditions = or_condition.conditions
            token_type, dummy = lex.peek()
            if token_type == '!':
                invert_mode = True
            else:
                invert_mode = False
            while 1:
                if invert_mode:
                    self.assert_type(lex, '!')
                arch = self.assert_type(lex, 'word')
                domain = self.package_type.type_string
                or_conditions.append(rc(eq, domain, 'arch', arch))
                token_type, dummy = lex.peek()
                if token_type == ']':
                    self.assert_type(lex, ']')
                    break
            if invert_mode:
                arch_condition = notc(or_condition)
            else:
                arch_condition = or_condition
            conditions.append(arch_condition)

        # followed by an optional {} containing 0 or more arbitrary
        # relations.
        token_type, dummy = lex.peek()
        if token_type == '{':
            self.assert_type(lex, '{')
            and_condition = ac([])
            and_conditions = and_condition.conditions
            while 1:
                pred_str = self.assert_type(lex, 'word')

                if ':' in pred_str:
                    domain, predicate = pred_str.split(':', 1)
                else:
                    domain = 'pdk'
                    predicate = pred_str

                rel_type, op_func = self.parse_op(lex)
                target = self.assert_type(lex, 'word')

                and_conditions.append(rel_type(op_func, domain, predicate,
                                               target))
                token_type, dummy = lex.peek()
                if token_type == '}':
                    self.assert_type(lex, '}')
                    break
            conditions.append(and_condition)

        return condition

    def parse_op(self, lex):
        op_str = self.assert_type(lex, 'op')
        return op_map[op_str]

# vim:set ai et sw=4 ts=4 tw=75:
