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

from operator import eq
from cElementTree import XML, Element
from pdk.rules import Rule, AndCondition, OneMatchMetacondition
from pdk import rules
from pdk.test.utest_util import Test

from pdk.component import ComponentDescriptor, ActionMetaSet, \
     ActionLinkEntities

class TestComponentTreeBuilder(Test):
    def assert_rule_matches(self, expected_fields, expected_predicates,
                            expected_links, rule):
        assert rule.__class__ == Rule
        assert rule.condition.__class__ == AndCondition
        actual_fields = []
        for condition in rule.condition.conditions:
            self.assert_equal(condition.__class__, rules.rc)
            assert condition.condition == eq
            actual_fields.append((condition.domain,
                                  condition.predicate,
                                  condition.target))
        self.assert_equals_long(expected_fields, actual_fields)

        actual_predicates = []
        actual_links = []
        for action in rule.action.actions:
            if isinstance(action, ActionMetaSet):
                actual_predicates.append((action.domain, action.predicate,
                                          action.target))
            if isinstance(action, ActionLinkEntities):
                actual_links.append((action.ent_type,
                                     action.ent_id))
        self.assert_equals_long(expected_predicates, actual_predicates,
                                'predicate mismatch')
        self.assert_equals_long(expected_links, actual_links,
                                'link mismatch')
        self.assert_equals(rule.metacondition.__class__,
                           OneMatchMetacondition)

    def test_build_ref(self):
        builder = ComponentDescriptor(None)
        element = XML('''
<deb>
  <name>hello</name>
  <meta>
    <ice>cube</ice>
  </meta>
</deb>
''')
        ref = builder.build_package_ref(element)
        assert not ref.reference.blob_id
        self.assert_equal('deb', ref.reference.package_type.type_string)
        self.assert_rule_matches([('pdk', 'name', 'hello'),
                                  ('pdk', 'type', 'deb')],
                                 [('pdk', 'ice', 'cube')], [], ref.rule)

    def test_build_concrete_ref(self):
        builder = ComponentDescriptor(None)
        element = XML('''
<deb ref="md5:aaa">
  <name>hello</name>
  <meta>
    <ice>cube</ice>
  </meta>
</deb>
''')
        ref = builder.build_package_ref(element)
        self.assert_equal('deb', ref.reference.package_type.type_string)
        self.assert_equal('md5:aaa', ref.reference.blob_id)
        self.assert_rule_matches([('pdk', 'blob-id', 'md5:aaa'),
                                  ('pdk', 'name', 'hello'),
                                  ('pdk', 'type', 'deb')],
                                 [('pdk', 'ice', 'cube')], [], ref.rule)

    def test_build_bare_name_rule(self):
        '''rules like <deb>name</deb> should have name conditions.
        No metadata should be present.
        '''
        builder = ComponentDescriptor(None)
        name_element = XML('<deb>some-name</deb>')
        ref = builder.build_package_ref(name_element)
        assert not ref.reference.blob_id
        self.assert_equal('deb', ref.reference.package_type.type_string)
        self.assert_rule_matches([('pdk', 'name', 'some-name'),
                                  ('pdk', 'type', 'deb')],
                                 [], [], ref.rule)

    def test_build_with_links(self):
        builder = ComponentDescriptor(None)
        element = XML('''
<deb>
  <name>hello</name>
  <meta>
    <ice>cube</ice>
    <pdk.link><vuln>can-do</vuln></pdk.link>
  </meta>
</deb>
''')
        ref = builder.build_package_ref(element)
        assert not ref.reference.blob_id
        self.assert_equal('deb', ref.reference.package_type.type_string)
        self.assert_rule_matches([('pdk', 'name', 'hello'),
                                  ('pdk', 'type', 'deb')],
                                 [('pdk', 'ice', 'cube')],
                                 [('vuln', 'can-do')], ref.rule)

    def test_build_general_ref(self):
        builder = ComponentDescriptor(None)
        element = XML('''
<src>
  <name>hello</name>
  <meta>
    <ice>cube</ice>
  </meta>
</src>
''')
        ref = builder.build_package_ref(element)
        assert not ref.reference.blob_id
        self.assert_equal('src', ref.reference.package_type.type_string)
        self.assert_rule_matches([('pdk', 'name', 'hello'),
                                  ('pdk', 'role', 'source')],
                                 [('pdk', 'ice', 'cube')], [], ref.rule)

    def test_is_package_ref(self):
        builder = ComponentDescriptor(None)

        deb_rule = Element('deb')
        udeb_rule = Element('udeb')
        dsc_rule = Element('dsc')
        rpm_rule = Element('rpm')
        srpm_rule = Element('srpm')
        component_rule = Element('component')

        assert builder.is_package_ref(deb_rule)
        assert builder.is_package_ref(udeb_rule)
        assert builder.is_package_ref(dsc_rule)
        assert builder.is_package_ref(rpm_rule)
        assert builder.is_package_ref(srpm_rule)
        assert not builder.is_package_ref(component_rule)

# vim:set ai et sw=4 ts=4 tw=75:
