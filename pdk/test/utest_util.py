# $Progeny$
#
#   Copyright 2005, 2006 Progeny Linux Systems, Inc.
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

import sys
import os
import re
import tempfile
import shutil
import difflib
import md5
from pprint import pformat
from unittest import TestCase
from pdk.package import Package, DebianVersion, srpm

__revision__ = '$Progeny$'

def fix_camel(camel_case):
    def _lower(match):
        return '_' + match.group(0).lower()
    return re.sub('[A-Z]', _lower, camel_case)

def uncamel_class(cls):
    for attribute in dir(cls):
        if attribute.startswith('__'):
            continue
        if not re.match('assert|fail', attribute):
            continue

        fixed_attribute = fix_camel(attribute)
        if fixed_attribute != attribute \
               and not hasattr(cls, fixed_attribute):
            setattr(cls, fixed_attribute, getattr(cls, attribute))

class Test(TestCase, object):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def setUp(self):
        self.set_up()

    def tearDown(self):
        self.tear_down()

    def break_long(self, raw):
        if isinstance(raw, basestring):
            return raw.splitlines()
        else:
            return pformat(raw).splitlines()

    def assert_equals_long(self, raw_expected, raw_actual,
                           user_message=''):
        if raw_expected != raw_actual:
            expected = self.break_long(raw_expected)
            actual = self.break_long(raw_actual)

            differ = difflib.ndiff(expected, actual)
            message = "Diff:\n" + '\n'.join(differ)
            if user_message:
                message += '\n' + user_message
            self.fail(message)

    def split_file(self, path):
        return self.read_file(path).splitlines()

    def read_file(self, path):
        return open(str(path)).read()

uncamel_class(Test)

class TempDirTest(Test):
    def set_up(self):
        prefix = os.path.basename(sys.argv[0] + '-')
        self.work_dir = tempfile.mkdtemp('', prefix)
        self.old_dir = os.getcwd()
        os.chdir(self.work_dir)

    def tear_down(self):
        os.chdir(self.old_dir)
        shutil.rmtree(self.work_dir)

class ShamCache(object):
    def __init__(self, make_copies = False):
        self.expected_packages = {}
        self.make_copies = make_copies

    def copy(self, package):
        if self.make_copies:
            package_copy = Package(package.package_type, package.ent_id)
            package_copy.update(package)
            return package_copy
        else:
            return package

    def load_package(self, ref, package_type):
        key = (ref, package_type)
        assert key in self.expected_packages, '%s missing' % str(key)
        return self.copy(self.expected_packages[key])

    def add(self, package):
        self.expected_packages[(package.blob_id, package.type)] = \
            package

class MockPackage(Package):
    def __init__(self, name, raw_version, package_type, blob_id = None,
                 extras = None, **kw):
        if extras == None:
            extras = {}

        if blob_id is None:
            ident_string = '%s %r %s %r' \
                           % (name, raw_version, package_type, kw)
            digest = md5.md5(ident_string).hexdigest()
            blob_id = 'md5:' + digest

        super(MockPackage, self).__init__(package_type, blob_id)

        if isinstance(raw_version, basestring):
            version = DebianVersion(raw_version)
        else:
            version = raw_version
        if package_type == srpm:
            self['pdk', 'nosrc'] = False
        domain = package_type.format_string

        self[('pdk', 'name')] = name
        self[('pdk', 'version')] = version
        for key, value in extras.iteritems():
            self[key] = value

        for key, value in kw.iteritems():
            self[(domain, key)] = value

# vim:set ai et sw=4 ts=4 tw=75:
