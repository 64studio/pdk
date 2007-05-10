#!/usr/bin/python
#
# $Progeny$
#
# Run tests.
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

"Test runner for the picax unit tests."

import sys
import os
import imp
import unittest

import picax.test

# Import the tests.  This is not a function for namespace reasons.

top_suite = unittest.TestSuite()
test_path = picax.test.__path__[0]

for module_fn in os.listdir(test_path):
    if not os.path.isfile("%s/%s" % (test_path, module_fn)):
        continue
    if module_fn[-3:] != ".py" or module_fn[:5] != "test_":
        continue

    module_name = module_fn[:-3]

    (mod_file, mod_fn, mod_desc) = imp.find_module(module_name,
                                                   picax.test.__path__)
    try:
        mod = imp.load_module(module_name, mod_file, mod_fn, mod_desc)
    finally:
        if mod_file is not None:
            mod_file.close()

    for identifier in mod.__dict__.keys():
        try:
            if issubclass(mod.__dict__[identifier], unittest.TestCase):
                top_suite.addTest(
                    unittest.makeSuite(mod.__dict__[identifier],
                                       "test"))
        except TypeError:
            continue

# Run the tests

if __name__ == "__main__":
    result = unittest.TextTestRunner().run(top_suite)
    sys.exit(not result.wasSuccessful())

# vim:set ai et sw=4 ts=4 tw=75:
