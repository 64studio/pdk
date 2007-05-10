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

"""Unit test for component operations"""
import os
from cStringIO import StringIO as stringio
from pdk.exceptions import InputError
from pdk.test.utest_util import Test, TempDirTest, ShamCache, MockPackage
from pdk.package import udeb, deb, dsc, rpm, srpm, RPMVersion, \
     DebianVersion
from pdk.meta import Entity
from pdk.cache import Cache
from pdk import rules
from operator import lt, le, gt, ge, eq

from pdk.component import \
     ComponentDescriptor, Component, PackageStanza, \
     get_child_condition_fn, \
     get_general_condition, \
     get_child_condition, \
     get_deb_child_condition, \
     get_dsc_child_condition, \
     get_rpm_child_condition, \
     get_srpm_child_condition, \
     ActionLinkEntities, \
     ActionUnlinkEntities, \
     ActionMetaSet, \
     PhantomConditionWrapper

__revision__ = "$Progeny$"

class MockUriHelper(dict):
    def __getattr__(self, name):
        return self[name]

class MockCache(object):
    def __init__(self):
        self.packages = []

    def load_package(self, blob_id, format):
        ref = (blob_id, format)
        if ref not in self.packages:
            self.packages.append(ref)
        return ref

class TestActions(Test):
    def test_link_ent_str(self):
        action = ActionLinkEntities('a', 'b')
        self.assert_equals("link ('a', 'b')", str(action))

    def test_link_exe(self):
        ent = Entity('c', 'd')
        action = ActionLinkEntities('a', 'b')
        action.execute(ent)
        self.assert_equal([('a', 'b')], ent.links)

    def test_unlink_ent_str(self):
        action = ActionUnlinkEntities('a', 'b')
        self.assert_equals("unlink ('a', 'b')", str(action))

    def test_unlink_exe(self):
        ent = Entity('c', 'd')
        action = ActionUnlinkEntities('a', 'b')
        ent.links.append(('a', 'b'))
        action.execute(ent)
        self.assert_equal([], ent.links)

    def test_link_twice_then_unlink(self):
        ent = Entity('c', 'd')
        link_action = ActionLinkEntities('a', 'b')
        link_action.execute(ent)
        link_action.execute(ent)
        self.assert_equal([('a', 'b')], ent.links)
        unlink_action = ActionUnlinkEntities('a', 'b')
        unlink_action.execute(ent)
        self.assert_equal([], ent.links)

    def test_action_meta_set(self):
        action = ActionMetaSet('a', 'b', 'c')
        actual = {}
        action.execute(actual)
        self.assert_equals({('a', 'b'): 'c'}, actual)

class TestCompDesc(TempDirTest):
    def test_static_create(self):
        desc = ComponentDescriptor.create('a.xml')
        # As part of this test, make sure we call write, as the black magic
        # might get fooled.
        desc.write()
        actual = open('a.xml').read()
        expected = '''<?xml version="1.0" encoding="utf-8"?>
<component>
</component>
'''
        self.assert_equals_long(expected, actual)

    def test_self_reference(self):
        os.system('''
cat >a.xml <<EOF
<component/>
''')

        desc = ComponentDescriptor('a.xml')
        ref = desc.get_self_reference()
        self.assert_equal('a.xml', ref.filename)
        self.assert_equal(rules.tc, ref.condition.__class__)

    def test_read_write_and_or(self):
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <or>
        <and>
          <name>a</name>
          <arch>b</arch>
        </and>
        <name>c</name>
      </or>
      <my.some>value</my.some>
    </deb>
  </contents>
</component>
EOF
cp a.xml b.xml
''')
        desc = ComponentDescriptor('a.xml')

        deb_ref = desc.contents[0]
        expected = rules.ac([
            rules.oc([ rules.ac([ rules.rc(eq, 'pdk', 'name', 'a'),
                                  rules.rc(eq, 'pdk', 'arch', 'b') ]),
                       rules.rc(eq, 'pdk', 'name', 'c') ]),
            rules.rc(eq, 'my', 'some', 'value') ])
        expected = PhantomConditionWrapper(expected, deb, None)
        self.assert_equals_long(expected, deb_ref.reference.condition)

        desc.write()
        self.assert_equals_long(open('b.xml').read(), open('a.xml').read())

    def test_write_relation(self):
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <version>2.0.53</version>
      <version-lt>2.0.53</version-lt>
      <version-lt-eq>2.0.53</version-lt-eq>
      <version-gt>2.0.53</version-gt>
      <version-gt-eq>2.0.53</version-gt-eq>
    </deb>
    <dsc>
      <version>2.0.53</version>
      <version-lt>2.0.53</version-lt>
    </dsc>
    <rpm>
      <version>2.0.53-0</version>
      <version-lt>2.0.53-0</version-lt>
    </rpm>
    <srpm>
      <version>2.0.53-0</version>
      <version-lt>2.0.53-0</version-lt>
    </srpm>
  </contents>
</component>
EOF
cp a.xml b.xml
''')
        desc = ComponentDescriptor('a.xml')
        desc.write()
        self.assert_equals_long(open('b.xml').read(), open('a.xml').read())

    def test_read_relation_condition(self):
        os.system('''
cat >a.xml <<EOF
<component>
  <contents>
    <deb>
      <version>2.0.53</version>
      <version-lt>2.0.53</version-lt>
      <version-lt-eq>2.0.53</version-lt-eq>
      <version-gt>2.0.53</version-gt>
      <version-gt-eq>2.0.53</version-gt-eq>
    </deb>
    <dsc>
      <version>2.0.53</version>
      <version-lt>2.0.53</version-lt>
    </dsc>
    <rpm>
      <version>2.0.53</version>
      <version-lt>2.0.53</version-lt>
    </rpm>
    <srpm>
      <version>2.0.53</version>
      <version-lt>2.0.53</version-lt>
    </srpm>
  </contents>
</component>
EOF
''')
        desc = ComponentDescriptor('a.xml')
        deb_conditions = desc.contents[0].reference.condition.conditions
        dv = DebianVersion
        self.assert_equal(rules.rc(eq, 'pdk', 'version', dv('2.0.53')),
                          deb_conditions[0])
        assert isinstance(deb_conditions[0].target, DebianVersion)
        self.assert_equal(rules.rc(lt, 'pdk', 'version', dv('2.0.53')),
                          deb_conditions[1])
        assert isinstance(deb_conditions[1].target, DebianVersion)
        self.assert_equal(rules.rc(le, 'pdk', 'version', dv('2.0.53')),
                          deb_conditions[2])
        assert isinstance(deb_conditions[2].target, DebianVersion)
        self.assert_equal(rules.rc(gt, 'pdk', 'version', dv('2.0.53')),
                          deb_conditions[3])
        assert isinstance(deb_conditions[3].target, DebianVersion)
        self.assert_equal(rules.rc(ge, 'pdk', 'version', dv('2.0.53')),
                          deb_conditions[4])
        assert isinstance(deb_conditions[4].target, DebianVersion)

        dsc_conditions = desc.contents[1].reference.condition.conditions
        self.assert_equal(rules.rc(eq, 'pdk', 'version', dv('2.0.53')),
                          dsc_conditions[0])
        assert isinstance(dsc_conditions[0].target, DebianVersion)
        self.assert_equal(rules.rc(lt, 'pdk', 'version', dv('2.0.53')),
                          dsc_conditions[1])
        assert isinstance(dsc_conditions[1].target, DebianVersion)

        def rv(version):
            return RPMVersion(version_string = version)

        rpm_conditions = desc.contents[2].reference.condition.conditions
        self.assert_equal(rules.rc(eq, 'pdk', 'version', rv('2.0.53')),
                          rpm_conditions[0])
        assert isinstance(rpm_conditions[0].target, RPMVersion)
        self.assert_equal(rules.rc(lt, 'pdk', 'version', rv('2.0.53')),
                          rpm_conditions[1])
        assert isinstance(rpm_conditions[1].target, RPMVersion)

        srpm_conditions = desc.contents[3].reference.condition.conditions
        self.assert_equal(rules.rc(eq, 'pdk', 'version', rv('2.0.53')),
                          srpm_conditions[0])
        assert isinstance(srpm_conditions[0].target, RPMVersion)
        self.assert_equal(rules.rc(lt, 'pdk', 'version', rv('2.0.53')),
                          srpm_conditions[1])
        assert isinstance(srpm_conditions[1].target, RPMVersion)

    def test_load_empty(self):
        """compdesc.load returns an empty component"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component/>
EOF
''')
        desc = ComponentDescriptor('a.xml')
        descriptor = desc.load(None)
        assert isinstance(descriptor, Component)

    def test_complement(self):
        """compdesc.load returns a component with packages"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <deb ref="sha-1:aaa"/>
      <deb ref="sha-1:bbb"/>
      <dsc ref="sha-1:ccc"/>
    </deb>
    <dsc>
      <dsc ref="sha-1:ccc"/>
      <deb ref="sha-1:aaa"/>
      <deb ref="sha-1:bbb"/>
      <deb ref="sha-1:ddd"/>
    </dsc>
  </contents>
</component>
EOF
''')
        desc = ComponentDescriptor('a.xml')
        cache = ShamCache(make_copies = True)
        a = MockPackage('a', '1', deb, 'sha-1:aaa', arch='i386')
        b = MockPackage('b', '1', deb, 'sha-1:bbb', arch='i386')
        c = MockPackage('c', '1', dsc, 'sha-1:ccc', arch='any')
        d = MockPackage('b', '1', deb, 'sha-1:ddd', arch='i386')
        cache.add(a)
        cache.add(b)
        cache.add(c)
        cache.add(d)
        component = desc.load(cache)
        packages = list(component.iter_packages())
        self.assert_equal([c], packages[0].complement)
        self.assert_equal([c], packages[1].complement)
        self.assert_equal([a, b], packages[2].complement)
        self.assert_equal([a, b, d], packages[3].complement)
        self.assert_equal([c], packages[4].complement)
        self.assert_equal([c], packages[5].complement)
        self.assert_equal([c], packages[6].complement)

    def test_load(self):
        """compdesc.load returns a component with packages"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb ref="sha-1:aaa"/>
  </contents>
</component>
EOF
''')
        desc = ComponentDescriptor('a.xml')
        cache = ShamCache()
        cache.add(MockPackage('a', '1', deb, 'sha-1:aaa'))
        component = desc.load(cache)
        assert isinstance(component, Component)
        self.assert_equal(1, len(list(component.iter_packages())))
        self.assert_equal(1, len(list(component.iter_direct_packages())))
        self.assert_equal(['sha-1:aaa'],
                          [ p.blob_id for p in component.iter_packages() ])
        self.assert_equal(0, len(list(component.iter_direct_components())))
        self.assert_equal(0, len(list(component.iter_components())))

    def test_load_and_write_cond(self):
        """compdesc.load returns a component with packages"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <cond><![CDATA[ apache (>>2) ]]></cond>
      <deb ref="sha-1:aaa">
        <cond>apache</cond>
      </deb>
    </deb>
  </contents>
</component>
EOF
cp a.xml b.xml
''')
        desc = ComponentDescriptor('a.xml')
        desc.write()
        self.assert_equals_long(open('b.xml').read(), open('a.xml').read())
        condition = desc.contents[0].reference.condition

        a = MockPackage('apache', '2-1', deb, 'sha-1:aaa')
        b = MockPackage('apache', '1.3', deb, 'sha-1:bbb')

        assert condition.evaluate(a)
        assert not condition.evaluate(b)

    def test_load_and_use_star_cond(self):
        """compdesc.load returns a component with packages"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
      <name>apache</name>
      <dsc ref="sha-1:ccc">
        <name>apache</name>
      </dsc>
      <deb ref="sha-1:aaa">
        <name>apache</name>
      </deb>
      <deb ref="sha-1:bbb">
        <name>apache-common</name>
      </deb>
    </dsc>
    <dsc>
      <cond><![CDATA[ * apache (>=2) ]]></cond>
    </dsc>
    <src>
      <cond><![CDATA[ * apache (>=2) ]]></cond>
    </src>
    <bin>
      <cond><![CDATA[ * apache-common (>=2) ]]></cond>
    </bin>
  </contents>
</component>
EOF
cp a.xml b.xml
''')
        desc = ComponentDescriptor('a.xml')
        desc.write()
        self.assert_equals_long(open('b.xml').read(), open('a.xml').read())
        condition = desc.contents[1].rule.condition

        a = MockPackage('apache', '2', deb, 'sha-1:aaa')
        b = MockPackage('apache-commmon', '2', deb, 'sha-1:bbb')
        c = MockPackage('apache', '2', dsc, 'sha-1:ccc')
        a.complement = [c]
        b.complement = [c]
        c.complement = [a, b]

        assert condition.evaluate(a)
        assert condition.evaluate(b)
        assert not condition.evaluate(c)

        src_condition = desc.contents[2].rule.condition
        assert src_condition.evaluate(a)
        assert src_condition.evaluate(b)
        assert not src_condition.evaluate(c)


    def test_load_file_object(self):
        """compdesc.load returns a component with packages"""
        handle = stringio('''<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb ref="sha-1:aaa"/>
  </contents>
</component>
''')
        desc = ComponentDescriptor('a.xml', handle)
        cache = ShamCache()
        cache.add(MockPackage('a', '1', deb, 'sha-1:aaa'))
        component = desc.load(cache)
        assert isinstance(component, Component)
        self.assert_equal('a.xml', desc.filename)
        self.assert_equal(1, len(list(component.iter_packages())))
        self.assert_equal(1, len(list(component.iter_direct_packages())))
        self.assert_equal(['sha-1:aaa'],
                          [ p.blob_id for p in component.iter_packages() ])
        self.assert_equal(0, len(list(component.iter_direct_components())))
        self.assert_equal(0, len(list(component.iter_components())))

    def test_load_component_meta(self):
        """compdesc.load finds component metadata"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <meta>
    <necessity>optional</necessity>
  </meta>
</component>
EOF
''')
        desc = ComponentDescriptor('a.xml')
        component = desc.load(None)
        self.assert_equals(component.meta['pdk', 'necessity'], 'optional')

    def test_load_fields(self):
        """compdesc.load populates id, name, etc. fields"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0"?>
<component>
  <id>resolveme</id>
  <name>Resolve Me</name>
  <description>
    I need to be resolved
  </description>
  <requires>a</requires>
  <requires>b</requires>
  <provides>c</provides>
  <provides>d</provides>
</component>
EOF
''')
        desc = ComponentDescriptor('a.xml')
        component = desc.load(None)
        self.assert_equals('resolveme', component.id)
        self.assert_equals('Resolve Me', component.name)
        self.assert_equals('\n    I need to be resolved\n  ',
                           component.description)
        self.assert_equals(['a', 'b'], component.requires)
        self.assert_equals(['c', 'd'], component.provides)

    def test_load_multilevel(self):
        """test loading a component that refers to another"""
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <name>libc6</name>
      <meta>
        <necessity>mandatory</necessity>
      </meta>
    </deb>
    <deb>
      <name>apache</name>
      <meta>
        <necessity>default</necessity>
      </meta>
    </deb>
    <component>b.xml</component>
  </contents>
</component>
EOF
''')
        os.system('''
cat >b.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <name>libc6</name>
      <meta>
        <necessity>optional</necessity>
      </meta>
    </deb>
    <deb ref="sha-1:aaa">
      <name>apache</name>
      <meta>
        <necessity>optional</necessity>
      </meta>
    </deb>
    <component>c.xml</component>
  </contents>
</component>
EOF
''')
        os.system('''
cat >c.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb ref="sha-1:bbb">
      <name>libc6</name>
      <meta>
        <necessity>mandatory</necessity>
        <some-random-key>42</some-random-key>
      </meta>
    </deb>
  </contents>
</component>
EOF
''')

        apache = MockPackage('apache', '1', deb,'sha-1:aaa')
        libc = MockPackage('libc6', '1', deb, 'sha-1:bbb')
        cache = ShamCache()
        cache.add(apache)
        cache.add(libc)

        desc_b = ComponentDescriptor('b.xml')
        component_b = desc_b.load(cache)
        assert isinstance(component_b, Component)
        self.assert_equal('b.xml', desc_b.filename)
        self.assert_equal('b.xml', component_b.ref)
        self.assert_equal(2, len(list(component_b.iter_packages())))
        self.assert_equal(['sha-1:aaa', 'sha-1:bbb'],
                          [ p.blob_id
                            for p in component_b.iter_packages() ])
        self.assert_equal(1, len(list(component_b.iter_direct_packages())))
        self.assert_equal(1,
                          len(list(component_b.iter_direct_components())))
        self.assert_equal(1, len(list(component_b.iter_components())))
        self.assert_equal('optional',
                          libc['pdk', 'necessity'])
        self.assert_equal('optional',
                          apache['pdk', 'necessity'])

        apache = MockPackage('apache', '1', deb,'sha-1:aaa')
        libc = MockPackage('libc6', '1', deb, 'sha-1:bbb')
        cache = ShamCache()
        cache.add(apache)
        cache.add(libc)

        desc_a = ComponentDescriptor('a.xml')
        component_a = desc_a.load(cache)
        assert isinstance(component_a, Component)
        self.assert_equal(2, len(list(component_a.iter_packages())))
        self.assert_equal(['sha-1:aaa', 'sha-1:bbb'],
                          [ p.blob_id
                            for p in component_a.iter_packages() ])
        self.assert_equal(0, len(list(component_a.iter_direct_packages())))
        self.assert_equal(1,
                          len(list(component_a.iter_direct_components())))
        self.assert_equal(2, len(list(component_a.iter_components())))
        self.assert_equal('mandatory', libc['pdk', 'necessity'])
        self.assert_equal('default', apache['pdk', 'necessity'])
        self.assert_equal('42', libc['pdk', 'some-random-key'])

    def test_empty_meta_element(self):
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <meta/>
</component>
''')
        desc = ComponentDescriptor('test.xml')
        desc.write()
        expected = '''<?xml version="1.0" encoding="utf-8"?>
<component>
</component>
'''
        self.assert_equals_long(expected, open('test.xml').read())

    def test_occupied_meta_element(self):
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <meta>
    <key>value</key>
  </meta>
  <contents>
    <deb ref="sha-1:aaa">
      <meta>
        <other-key>other-value</other-key>
        <link>
          <vuln>22</vuln>
        </link>
        <unlink>
          <vuln>20</vuln>
        </unlink>
      </meta>
    </deb>
  </contents>
</component>
''')
        desc = ComponentDescriptor('test.xml')
        desc.write()
        expected = '''<?xml version="1.0" encoding="utf-8"?>
<component>
  <meta>
    <key>value</key>
  </meta>
  <contents>
    <deb ref="sha-1:aaa">
      <meta>
        <other-key>other-value</other-key>
        <link>
          <vuln>22</vuln>
        </link>
        <unlink>
          <vuln>20</vuln>
        </unlink>
      </meta>
    </deb>
  </contents>
</component>
'''
        self.assert_equals_long(expected, open('test.xml').read())

    def test_dont_lose_entities(self):
        """Make sure the write method handles entities."""
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <meta>
    <predicate>object</predicate>
  </meta>
  <contents>
    <dsc>
      <name>a</name>
      <meta>
        <c>d</c>
      </meta>
    </dsc>
    <deb ref="sha-1:aaa">
      <meta>
        <necessity>mandatory</necessity>
      </meta>
    </deb>
  </contents>
  <entities>
    <test id="1">
      <a>b</a>
      <c>d</c>
      <e>f</e>
    </test>
  </entities>
</component>
''')
        desc = ComponentDescriptor('test.xml')
        cache = ShamCache()
        cache.add(MockPackage('a', '1', deb, 'sha-1:aaa'))
        desc.load(cache)
        desc.write()
        expected = '''<?xml version="1.0" encoding="utf-8"?>
<component>
  <meta>
    <predicate>object</predicate>
  </meta>
  <contents>
    <dsc>
      <name>a</name>
      <meta>
        <c>d</c>
      </meta>
    </dsc>
    <deb ref="sha-1:aaa">
      <meta>
        <necessity>mandatory</necessity>
      </meta>
    </deb>
  </contents>
  <entities>
    <test id="1">
      <a>b</a>
      <c>d</c>
      <e>f</e>
    </test>
  </entities>
</component>
'''
        self.assert_equals_long(expected, open('test.xml').read())

    def test_dont_mutate_meta(self):
        """Make sure the load method does not mutate the meta info
        in the descriptor.
        """
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <meta>
    <predicate>object</predicate>
  </meta>
  <contents>
    <dsc>
      <name>a</name>
      <meta>
        <c>d</c>
      </meta>
    </dsc>
    <deb ref="sha-1:aaa">
      <meta>
        <necessity>mandatory</necessity>
      </meta>
    </deb>
  </contents>
</component>
''')
        desc = ComponentDescriptor('test.xml')
        cache = ShamCache()
        cache.add(MockPackage('a', '1', deb, 'sha-1:aaa'))
        desc.load(cache)
        desc.write()
        expected = '''<?xml version="1.0" encoding="utf-8"?>
<component>
  <meta>
    <predicate>object</predicate>
  </meta>
  <contents>
    <dsc>
      <name>a</name>
      <meta>
        <c>d</c>
      </meta>
    </dsc>
    <deb ref="sha-1:aaa">
      <meta>
        <necessity>mandatory</necessity>
      </meta>
    </deb>
  </contents>
</component>
'''
        self.assert_equals_long(expected, open('test.xml').read())

    def test_load_sub_component_meta(self):
        """Be sure metadata gets loaded from subcomponents even if
        the toplevel component has none.
        """
        open('test1.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <contents>
    <component>test2.xml</component>
  </contents>
</component>
''')
        open('test2.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <contents>
    <deb ref="sha-1:aaa">
      <meta>
        <necessity>mandatory</necessity>
      </meta>
    </deb>
  </contents>
</component>
''')
        cache = ShamCache()
        package = MockPackage('a', '1', deb, 'sha-1:aaa')
        cache.add(package)
        desc = ComponentDescriptor('test1.xml')
        comp = desc.load(cache)
        assert package in list(comp.iter_packages())
        self.assert_equal("mandatory", package[('pdk', 'necessity')])

    def test_meta_implicit_ref(self):
        """Check that implicit references in metadata are supported and
        correctly resolve to references to self.
        """
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <meta>
    <necessity>mandatory</necessity>
  </meta>
</component>
''')
        desc = ComponentDescriptor('test.xml')
        comp = desc.load(Cache(os.path.join(self.work_dir, 'cache')))
        self.assert_equal('mandatory', comp.meta[('pdk', 'necessity')])

    def test_iter_package_refs(self):
        class MockRef(PackageStanza):
            def __init__(self, label):
                condition = rules.ac([('pdk', 'name', 'apache')])
                PackageStanza.__init__(self, deb, None, condition, [])
                self.label = label
                self.children = []

            def __repr__(self):
                return str(self.label)

        desc = ComponentDescriptor(None)
        a = MockRef('a')
        b = MockRef('b')
        c = MockRef('c')
        a.children = [b]
        desc.contents = [ a, c ]

        self.assert_equal([a, c], list(desc.iter_package_refs()))
        self.assert_equal([a, b, c], list(desc.iter_full_package_refs()))

    def test_parse_entity(self):
        '''Check that we can parse entities at all.'''
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <entities>
    <some-ent id="can-do">
      <a.name>hello</a.name>
      <b.description>whodo whodo whodo</b.description>
    </some-ent>
  </entities>
</component>
''')

        desc = ComponentDescriptor('test.xml')
        entity1 = desc.entities[('some-ent', 'can-do')]
        self.assert_equal('hello', entity1[('a', 'name')])
        self.assert_equal('whodo whodo whodo',
                          entity1[('b', 'description')])
        cache = ShamCache()
        comp = desc.load(cache)
        entity2 = comp.entities[('some-ent', 'can-do')]
        self.assert_equal('hello', entity2[('a', 'name')])
        self.assert_equal('whodo whodo whodo',
                          entity2[('b', 'description')])

    def test_parse_link(self):
        '''Check that we can parse entities at all.'''
        open('test.xml', 'w').write('''<?xml version="1.0"?>
<component>
  <contents>
    <deb ref="sha-1:aaa">
      <meta>
        <pdk.link>
          <some-meta>can-do</some-meta>
        </pdk.link>
      </meta>
    </deb>
  </contents>
</component>
''')

        desc = ComponentDescriptor('test.xml')
        self.assert_equal([('some-meta', 'can-do')],
                          desc.contents[0].links)
        cache = ShamCache()
        package = MockPackage('a', '1', deb, 'sha-1:aaa')
        cache.add(package)
        comp = desc.load(cache)
        package = comp.iter_packages().next()
        self.assert_equals([('some-meta', 'can-do')], package.links)

    def test_conditional_include(self):
        os.system('''
cat >b.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb ref="sha-1:aaa">
      <name>apache</name>
    </deb>
    <deb ref="sha-1:bbb">
      <name>libc6</name>
    </deb>
    <deb ref="sha-1:ccc">
      <name>ls</name>
    </deb>
  </contents>
</component>
EOF
''')
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <component>
      <file>b.xml</file>
      <limit>apache</limit>
      <exclude>ls</exclude>
    </component>
  </contents>
</component>
EOF
cp a.xml c.xml
''')
        apache = MockPackage('apache', '1', deb, 'sha-1:aaa',
                             arch = 'i386')
        libc = MockPackage('libc6', '1', deb, 'sha-1:bbb', arch = 'i386')
        ls = MockPackage('ls', '1', deb, 'sha-1:ccc', arch = 'i386')
        cache = ShamCache()
        cache.add(apache)
        cache.add(libc)
        cache.add(ls)

        desc_a = ComponentDescriptor('a.xml')
        desc_a.write()
        self.assert_equals_long(open('c.xml').read(), open('a.xml').read())
        component_a = desc_a.load(cache)
        assert isinstance(component_a, Component)
        expected = [ apache ]
        actual = list(component_a.iter_packages())
        self.assert_equal(expected, actual)

    def test_bad_comp_ref(self):
        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <component>
      <limit><![CDATA[ apache ]]></limit>
    </component>
  </contents>
</component>
EOF
''')
        try:
            ComponentDescriptor('a.xml').load(ShamCache())
            self.fail('should have thrown exception')
        except InputError:
            pass

        os.system('''
cat >a.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <component>
      <zzz></zzz>
      <limit><![CDATA[ apache ]]></limit>
    </component>
  </contents>
</component>
EOF
''')
        try:
            ComponentDescriptor('a.xml').load(ShamCache())
            self.fail('should have thrown exception')
        except InputError, error:
            assert '"zzz"' in str(error)


class TestPackageRef(Test):
    def test_is_abstract(self):
        concrete_ref_a = \
            PackageStanza(deb, 'sha-1:aaa', None, None)
        assert not concrete_ref_a.is_abstract()

        concrete_ref_b = PackageStanza(deb, None, None, None)
        concrete_ref_b.children.append(concrete_ref_a)
        assert not concrete_ref_b.is_abstract()

        abstract_ref = PackageStanza(deb, None, None, None)
        assert abstract_ref.is_abstract()

    def test_field_lookups(self):
        condition = rules.ac([rules.rc(eq, 'pdk', 'name', 'apache')])
        ref = PackageStanza(deb, 'sha-1:aaa', condition, [])

        assert ('pdk', 'name') in ref
        assert ('pdk', 'version') not in ref
        self.assert_equal('apache', ref[('pdk', 'name')])
        self.assert_equal('apache', ref.name)
        self.assert_equal('', ref.version)
        self.assert_equal('', ref.arch)

    def test_comparable(self):
        fields = rules.ac([('pdk', 'name', 'apache')])
        refa1 = PackageStanza(deb, 'sha-1:aaa', fields, [])
        refa2 = PackageStanza(deb, 'sha-1:aaa', fields, [])
        refb = PackageStanza(deb, 'sha-1:aaa',
                                rules.ac([('pdk', 'name', 'xsok')]), [])

        assert refa1 == refa2
        assert refa1 < refb

    def test_get_child_condition_fn(self):
        apache_deb = MockPackage('apache', '1', deb, 'sha-1:aaa')
        apache_udeb = MockPackage('apache', '1', udeb, 'sha-1:aaa')
        apache_rpm = MockPackage('apache', '1', rpm, 'sha-1:aaa')
        apache_dsc = MockPackage('apache', '1', dsc, 'sha-1:aaa')
        apache_srpm = MockPackage('apache', '1', srpm, 'sha-1:aaa')

        self.assert_equals(get_deb_child_condition,
                           get_child_condition_fn(apache_deb))
        self.assert_equals(get_deb_child_condition,
                           get_child_condition_fn(apache_udeb))
        self.assert_equals(get_dsc_child_condition,
                           get_child_condition_fn(apache_dsc))
        self.assert_equals(get_rpm_child_condition,
                           get_child_condition_fn(apache_rpm))
        self.assert_equals(get_srpm_child_condition,
                           get_child_condition_fn(apache_srpm))

    def test_get_deb_child_condition(self):
        sp_version = DebianVersion('1-2')
        extra = {('pdk', 'sp-name'): 'one',
                 ('pdk', 'sp-version'): sp_version}
        apache_deb = MockPackage('apache', '1', deb, 'sha-1:aaa', extra)

        expected = rules.ac([ rules.rc(eq, 'pdk', 'name', 'one'),
                              rules.rc(eq, 'pdk', 'version', '1-2'),
                              rules.rc(eq, 'pdk', 'type', 'dsc') ])

        self.assert_equals(expected,
                           get_deb_child_condition(apache_deb))

    def test_get_dsc_child_condition(self):
        version = DebianVersion('1-2')
        apache_dsc = MockPackage('apache', version, dsc, 'sha-1:aaa')

        type_condition = rules.oc([ rules.rc(eq, 'pdk', 'type', 'deb'),
                                    rules.rc(eq, 'pdk', 'type', 'udeb')])
        expected = rules.ac([ rules.rc(eq, 'pdk', 'sp-name', 'apache'),
                              rules.rc(eq, 'pdk', 'sp-version', '1-2'),
                              type_condition ])

        self.assert_equals(expected,
                           get_dsc_child_condition(apache_dsc))


    def test_get_rpm_child_condition(self):
        version = RPMVersion(version_string = '1-2')
        extras = {('pdk', 'source-rpm'): 'apache.src.rpm'}
        apache_rpm = MockPackage('apache', version, rpm, 'sha-1:aaa',
                                 extras = extras)

        expected = rules.ac([ rules.rc(eq, 'pdk', 'filename',
                                        'apache.src.rpm'),
                              rules.rc(eq, 'pdk', 'type', 'srpm') ])

        self.assert_equals(expected,
                           get_rpm_child_condition(apache_rpm))

    def test_get_srpm_child_condition(self):
        version = RPMVersion(version_string = '1-2')
        apache_srpm = MockPackage('apache', version, srpm, 'sha-1:aaa')
        expected = rules.ac([ rules.rc(eq, 'pdk', 'source-rpm',
                                        'apache-1-2.src.rpm'),
                              rules.rc(eq, 'pdk', 'type', 'rpm') ])

        self.assert_equals(expected,
                           get_srpm_child_condition(apache_srpm))


    def test_get_general_condition(self):
        version = DebianVersion('1-2')
        apache_dsc = MockPackage('apache', version, dsc, 'sha-1:aaa')

        sp_version = DebianVersion('1-2')
        extra = {('pdk', 'sp-name'): 'one',
                 ('pdk', 'sp-version'): sp_version,
                 ('deb', 'arch'): 'i386'}
        apache_deb = MockPackage('apache', '1-2', deb, 'sha-1:aaa', extra)

        expected = rules.ac([ rules.rc(eq, 'pdk', 'name', 'apache'),
                              rules.rc(eq, 'pdk', 'version', version) ])
        self.assert_equals(expected, get_general_condition(apache_dsc))

        expected = rules.ac([ rules.rc(eq, 'pdk', 'name', 'apache'),
                              rules.rc(eq, 'pdk', 'version', version),
                              rules.rc(eq, 'pdk', 'arch', 'i386') ])
        self.assert_equals(expected, get_general_condition(apache_deb))

    def test_get_child_condition(self):
        sp_version = DebianVersion('1-3')
        extra = {('pdk', 'sp-name'): 'apache',
                 ('pdk', 'sp-version'): sp_version,
                 ('deb', 'arch'): 'i386'}
        apache_deb = MockPackage('apache', '1-2', deb, 'sha-1:aaa', extra)

        ref_condition = rules.ac([rules.rc(eq, 'pdk', 'name', 'apache')])
        apache_ref = PackageStanza(deb, 'sha-1:aaa', ref_condition, [])


        parent_condition = rules.ac([ apache_ref.reference.condition,
                                      rules.rc(eq, 'pdk', 'version',
                                                DebianVersion('1-2')) ])
        child_condition = get_deb_child_condition(apache_deb)
        expected_rule = rules.oc([child_condition, parent_condition])
        expected_key_info = ('pdk', 'name', 'apache')
        actual_rule, actual_key_info = get_child_condition(apache_deb,
                                                          apache_ref)
        self.assert_equals(expected_rule, actual_rule)
        self.assert_equals(expected_key_info, actual_key_info)

# vim:set ai et sw=4 ts=4 tw=75:
