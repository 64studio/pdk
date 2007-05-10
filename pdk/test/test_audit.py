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

from sets import Set
from pdk.test.utest_util import Test

from pdk.audit import Arbiter

__revision__ = "$Progeny$"

class TestAudit(Test):
    def test_meet_expectations_prediction_first(self):
        arbiter = Arbiter(None)
        arbiter.predict(('check_name',), 'right', 'p_basis')
        arbiter.warrant(('check_name',), 'right', 'w_basis')

    def test_meet_expectations_warrant_first(self):
        arbiter = Arbiter(None)
        arbiter.warrant(('check_name',), 'right', 'w_basis')
        arbiter.predict(('check_name',), 'right', 'p_basis')

    def test_violate_expectations_prediction_first(self):
        found = []
        def _note_mismatch(*params):
            found.append(params)
        arbiter = Arbiter(_note_mismatch)
        arbiter.predict(('check_name',), 'right', 'p_basis')
        arbiter.warrant(('check_name',), 'wrong', 'w_basis')

    def test_violate_expectations_warrant_first(self):
        found = []
        def _note_mismatch(*params):
            found.append(params)
        arbiter = Arbiter(_note_mismatch)
        arbiter.warrant(('check_name',), 'wrong', 'w_basis')
        arbiter.predict(('check_name',), 'right', 'p_basis')
        self.assert_equal([(('check_name',), 'right', 'p_basis',
                            'wrong', 'w_basis')],
                          found)

    def test_note_leftovers(self):
        found = Set([])
        def _note_mismatch(*params):
            found.add(params)
        arbiter = Arbiter(_note_mismatch)
        arbiter.warrant(('check_name1',), 'wrong', 'w_basis')
        arbiter.predict(('check_name2',), 'right', 'p_basis')
        arbiter.note_leftovers()
        self.assert_equal(Set([(('check_name2',), 'right', 'p_basis',
                                None, 'no warrant')]),
                          found)

# vim:set ai et sw=4 ts=4 tw=75:
