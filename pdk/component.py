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

"""
component.py

This module houses functionality related to using, creating, and
machine modifying components.

"""
import os
from operator import lt, le, gt, ge, eq
from itertools import chain
from sets import Set
from pdk.util import write_pretty_xml, parse_xml, parse_domain, \
     string_domain
from cElementTree import ElementTree, Element, SubElement
from pdk.rules import Rule, RuleSystem, CompositeAction, make_comparable
from pdk import rules
from pdk.package import get_package_type, Package
from pdk.exceptions import PdkException, InputError, SemanticError
from pdk.meta import Entity, Entities
from xml.parsers.expat import ExpatError
from pdk.log import get_logger
from pdk.semdiff import print_report
from pdk.channels import PackageNotFoundError
from pdk.debish_condition import compile_debish

class ComponentDescriptor(object):
    """Represents a component descriptor object.

    This class is for looking at a convenient abstraction of the raw
    contents of a descriptor.

    Use the meta and contents properties to change the descriptor.

    Use load(cache) to instantiate trees of Component objects.
    """
    def __init__(self, filename, handle = None, get_desc = None):
        self.filename = filename

        if get_desc:
            self.get_desc = get_desc
        else:
            self.get_desc = ComponentDescriptor

        if filename is None:
            tree = ElementTree(element = Element('component'))
        elif handle:
            try:
                tree = parse_xml(handle)
            except ExpatError, message:
                raise InputError(filename, str(message))

        else:
            if os.path.exists(filename):
                try:
                    tree = parse_xml(filename)
                except ExpatError, message:
                    raise InputError(filename, str(message))
            else:
                message = 'Component descriptor "%s" does not exist.' \
                          % filename
                raise InputError(message)

        self.id = ''
        self.name = ''
        self.description = ''
        self.requires = []
        self.provides = []

        self.meta = []
        self.links = []
        self.unlinks = []
        self.entities = Entities()
        self.contents = []

        self.build_component_descriptor(tree.getroot())

    def create(filename):
        '''Create an empty component descriptor from scratch.'''
        # This is ugly black magic, but happens to work right now.
        # Perhaps in the future we can make the constructor smarter yet.
        desc = ComponentDescriptor(None)
        desc.filename = filename
        return desc
    create = staticmethod(create)

    def get_self_reference(self):
        '''Return a ComponentReference referring to this descriptor.'''
        return ComponentReference(self.filename)

    def load_raw(self, cache, package_condition):
        """Build the raw component/package tree but don't fire any rules.
        """
        component = Component(self.filename, cache, package_condition)
        field_names = ('id', 'name', 'description', 'requires', 'provides')
        for field_name in field_names:
            value = getattr(self, field_name)
            setattr(component, field_name, value)

        group_message = ""
        local_rules = []
        all_rules = []
        for stanza in self.contents:
            try:
                if isinstance(stanza, PackageStanza):
                    children = []
                    # Prescan the stanza looking for abstract children.
                    # These are ignored.
                    for concrete_stanza in stanza.children:
                        if concrete_stanza.is_abstract():
                            condition = concrete_stanza.reference.condition
                            message = \
                                'Child reference is abstract: %s %s' \
                                % (self.filename, str(condition))
                            logger = get_logger()
                            logger.warn(message)
                            continue
                        children.append(concrete_stanza)

                    if stanza.reference.blob_id:
                        stanzas = [stanza] + children
                    else:
                        local_rules.append(stanza.rule)
                        stanzas = children

                    # calculate complement information
                    comp_filler = {'binary': [], 'source': []}
                    for concrete_stanza in stanzas:
                        reference = concrete_stanza.reference
                        if reference.package_type.role_string == 'source':
                            comp_filler['binary'].append(reference)
                        else:
                            comp_filler['source'].append(reference)

                    for concrete_stanza in stanzas:
                        local_rules.append(concrete_stanza.rule)
                        contents = component.ordered_contents
                        reference = concrete_stanza.reference
                        role = reference.package_type.role_string
                        reference.complement = comp_filler[role]
                        contents.append(reference)
                elif isinstance(stanza, ComponentReference):
                    child_descriptor = stanza.load(self.get_desc)
                    loader = child_descriptor.load_raw
                    child_component = loader(cache, stanza.condition)
                    component.ordered_contents.append(child_component)
                    all_rules.extend(child_component.system.rules)
                    component.entities.update(child_component.entities)

            except PdkException, local_message:
                if group_message:
                    group_message = group_message + "\n"
                group_message = group_message + \
                    "Problems found in %s:\n%s" % (self.filename,
                                                   local_message)

        if group_message:
            raise SemanticError(group_message)

        all_rules.extend(local_rules)
        component.system = RuleSystem(all_rules)
        component.entities.update(self.entities)
        return component

    def load(self, cache, package_condition = rules.tc()):
        """Instantiate a component object tree for this descriptor."""
        component = self.load_raw(cache, package_condition)
        system = component.system

        # fire rule on all components
        for decendent_component in component.iter_components():
            system.fire(decendent_component)

        # add local metadata last
        for domain, predicate, target in self.meta:
            component.meta[(domain, predicate)] = target

        return component


    def write(self):
        '''Write the potentially modified descriptor back to xml.

        The original filename is overwritten.
        '''
        tree = ElementTree(element = Element('component'))
        root = tree.getroot()

        # construct the simple fields first.
        simple_fields = [ ('id', self.id),
                          ('name', self.name),
                          ('description', self.description) ]
        for multifield_name in ('requires', 'provides'):
            values = getattr(self, multifield_name)
            for value in values:
                simple_fields.append((multifield_name, value))

        for name, value in simple_fields:
            if value:
                element = SubElement(root, name)
                element.text = value

        # create and populate meta element if we have metadata.
        if len(self.meta) > 0:
            meta_element = SubElement(root, 'meta')
            for domain, predicate, target in self.meta:
                tag = string_domain(domain, predicate)
                meta_child = SubElement(meta_element, tag)
                meta_child.text = target

        if self.contents:
            contents_element = SubElement(root, 'contents')

        # next, write the contents element
        for reference in self.contents:
            if isinstance(reference, PackageStanza):
                self.write_package_reference(contents_element, reference)
            elif isinstance(reference, ComponentReference):
                self.write_component_reference(contents_element, reference)

        # last, write the entities element
        if self.entities:
            entities_element = SubElement(root, 'entities')
            self.write_entities(entities_element, self.entities)

        # actually write the xml to a file
        dirname = os.path.dirname(self.filename) or "."
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        write_pretty_xml(tree, self.filename)

    def write_component_reference(self, parent, reference):
        '''Build elements from a component reference.'''
        component_element = SubElement(parent, 'component')
        if isinstance(reference.condition, rules.tc):
            component_element.text = reference.filename
        else:
            file_element = SubElement(component_element, 'file')
            file_element.text = reference.filename
            for ref_condition in reference.condition.conditions:
                if isinstance(ref_condition, rules.notc):
                    tag_name = 'exclude'
                    condition = ref_condition.condition
                else:
                    tag_name = 'limit'
                    condition = ref_condition
                cond_element = SubElement(component_element, tag_name)
                cond_element.text = condition.debish

    def write_condition_fields(self, parent, outer_condition):
        '''Build elements out of condition fields.'''
        if hasattr(outer_condition, 'debish'):
            cond_element = SubElement(parent, 'cond')
            cond_element.text = outer_condition.debish
            return

        for condition in outer_condition.conditions:

            if isinstance(condition, rules.rc) \
                    and condition.condition == eq:
                tag_name = string_domain(condition.domain,
                                         condition.predicate)
                condition_element = SubElement(parent, tag_name)
                condition_element.text = str(condition.target)
            elif isinstance(condition, rules.rc):
                relation_map = { 'eq': 'version',
                                 'lt': 'version-lt',
                                 'le': 'version-lt-eq',
                                 'gt': 'version-gt',
                                 'ge': 'version-gt-eq' }
                tag_name = relation_map[condition.condition.__name__]
                condition_element = SubElement(parent, tag_name)
                condition_element.text = condition.target.full_version
            elif isinstance(condition, (rules.ac, rules.oc)):
                if isinstance(condition, rules.oc):
                    nested_element = SubElement(parent, 'or')
                elif isinstance(condition, rules.ac):
                    nested_element = SubElement(parent, 'and')
                self.write_condition_fields(nested_element,
                                            condition)

    def write_package_reference(self, parent, stanza):
        """Build elements for a single package stanza."""
        attributes = {}
        if stanza.reference.blob_id:
            attributes['ref'] = stanza.reference.blob_id
        name = stanza.reference.package_type.type_string
        ref_element = SubElement(parent, name, attributes)

        self.write_condition_fields(ref_element,
                                    stanza.reference.condition)
        predicates = stanza.predicates
        links = stanza.links
        unlinks = stanza.unlinks
        if predicates or links or unlinks:
            meta_element = SubElement(ref_element, 'meta')
            for domain, predicate, target in predicates:
                tag = string_domain(domain, predicate)
                predicate_element = SubElement(meta_element, tag)
                predicate_element.text = target

        if links:
            link_element = SubElement(meta_element, 'link')
            for ent_type, ent_id in links:
                ent_element = SubElement(link_element, ent_type)
                ent_element.text = ent_id

        if unlinks:
            unlink_element = SubElement(meta_element, 'unlink')
            for ent_type, ent_id in unlinks:
                ent_element = SubElement(unlink_element, ent_type)
                ent_element.text = ent_id

        for inner_ref in stanza.children:
            self.write_package_reference(ref_element, inner_ref)


    def write_entities(self, component_element, entities):
        '''Write out an entities element with all entities.'''
        entity_order = self.entities.keys()
        entity_order.sort()
        for entity_key in entity_order:
            ent_type, ent_id = entity_key
            entity_element = SubElement(component_element, ent_type,
                                        {'id': ent_id})
            entity = entities[entity_key]
            keys = entity.keys()
            keys.sort()
            for key in keys:
                key_name = string_domain(*key)
                key_element = SubElement(entity_element, key_name)
                key_element.text = entity[key]

    def _assert_resolved(self):
        """
        Assert that the descriptor has no abstract references.
        """
        logger = get_logger()
        unresolved = [r for r in self.contents
                       if isinstance(r,PackageStanza)
                         and r.is_abstract()
                      ]
        if unresolved:
            logger.warn(
                'Unresolved references remain in %s' \
                % self.filename
                )
            for stanza in unresolved:
                pkgtype = stanza.reference.package_type.type_string
                condition = str(stanza.rule)
                logger.warn(
                    "No %s %s" % (pkgtype, condition)
                )

    def resolve(self, find_package, cache, world_index,
                abstract_constraint):
        """Resolve abstract references by searching the given package list.

        find_package - a function we can call to pick the right package
                       out of a world_items iterator.
        cache        - a workspace cache
        world_index  - a world index we will use to search for candidate
                       packages.
        abstract_constraint -
                       whether stanzas must be resolved or unresolved.
        """
        if ('pdk', 'no-resolve', '1') in self.meta:
            return
        for stanza in self.iter_package_refs(abstract_constraint):
            stanza.resolve(find_package, cache, world_index)

    def note_download_info(self, acquirer, extended_cache):
        '''Recursively traverse and note blob ids in the acquirer.'''
        for stanza in self.iter_full_package_refs():
            if not stanza.reference.blob_id:
                continue
            blob_id = stanza.reference.blob_id
            acquirer.add_blob(blob_id)
            try:
                package = stanza.load(extended_cache)
            except PackageNotFoundError:
                continue
            for extra_blob_id, dummy, dummy in package.extra_files:
                acquirer.add_blob(extra_blob_id)

        for stanza in self.iter_component_refs():
            child_desc = stanza.load(self.get_desc)
            child_desc.note_download_info(acquirer, extended_cache)

    def iter_component_refs(self):
        '''Iterate over all component refs.'''
        for ref in self.contents:
            if isinstance(ref, ComponentReference):
                yield ref

    def iter_package_refs(self, abstract_constraint = None):
        '''Yield all base package references in order.

        If abstract_constraint is provided (and not None) then that
        value will be a constraint on the is_abstract() method of the
        refs. If a reference does no match the constraint, it is skipped.
        '''
        for dummy, ref in self.enumerate_package_refs():
            if abstract_constraint is not None:
                if bool(abstract_constraint) != bool(ref.is_abstract()):
                    continue
            yield ref


    def iter_full_package_refs(self):
        '''Yield all base and child package references.

        The search is pre-order depth first.
        '''
        for ref in self.iter_package_refs():
            yield ref
            for child_ref in ref.children:
                yield child_ref

    def enumerate_package_refs(self):
        '''Yield all index, package_reference pairs in self.contents.'''
        for index, ref in enumerate(self.contents):
            if isinstance(ref, PackageStanza):
                yield index, ref


    # These functions are only used when reading a descriptor in from
    # an xml handle. They roughly represent a recursive descent parser
    # except they operate on a pre-existing xml tree.
    #
    # The entry point is build_component_descriptor

    def build_links(self, link_element):
        '''Build up a list of tuples (link_type, link_id) for links.'''
        return [ (e.tag, e.text) for e in link_element ]

    def build_meta(self, meta_element):
        '''Return a list of tuples (predicate, object) for a "meta" tag.'''
        metas = []
        links = []
        unlinks = []
        for element in meta_element:
            domain, name = parse_domain(element.tag)
            if (domain, name) == ('pdk', 'link'):
                links.extend(self.build_links(element))
            elif (domain, name) == ('pdk', 'unlink'):
                unlinks.extend(self.build_links(element))
            else:
                metas.append((domain, name, element.text))
        return metas, links, unlinks

    def is_package_ref(self, rule_element):
        '''Does this element represent a single package?

        Returns true for elements representing both concrete and abstract
        references.
        '''
        return rule_element.tag in ('deb', 'udeb', 'dsc', 'rpm', 'srpm',
                                    'src', 'bin')

    def build_condition(self, element, package_type, blob_id):
        '''Build up a condition from xml.
        '''
        relation_tags = { 'version-lt': ('version', lt),
                          'version-lt-eq': ('version', le),
                          'version-gt': ('version', gt),
                          'version-gt-eq': ('version', ge),
                          'version': ('version', eq) }
        if element.tag in relation_tags:
            predicate, relation_fn = relation_tags[element.tag]
            target_str = element.text.strip()
            target_class = package_type.version_class
            target = target_class(version_string = target_str)
            return rules.rc(relation_fn, 'pdk', predicate, target)
        elif element.tag in ('and', 'or'):
            condition_class_map = {'and': rules.ac, 'or': rules.oc}
            condition = condition_class_map[element.tag]([])
            conditions = condition.conditions
            for and_element in element:
                conditions.append(self.build_condition(and_element,
                                                       package_type,
                                                       blob_id))
            return condition
        else:
            target = element.text.strip()
            domain, name = parse_domain(element.tag)
            return rules.rc(eq, domain, name, target)


    def build_package_ref(self, ref_element):
        '''Return a package_ref given an element.

        This function should only be applied to elements which pass the
        is_package_ref test.
        '''
        xml_condition = rules.ac([])
        debish_condition = None

        blob_id = None
        if 'ref' in ref_element.attrib:
            blob_id = ref_element.attrib['ref']

        package_type = get_package_type(format = ref_element.tag)

        ref_links = []
        ref_unlinks = []
        predicates = []
        inner_refs = []
        if ref_element.text and ref_element.text.strip():
            target = ref_element.text.strip()
            xml_condition.conditions.append(rules.rc(eq, 'pdk', 'name',
                                            target))
        else:
            for element in ref_element:
                if element.tag == 'meta':
                    meta, links, unlinks = self.build_meta(element)
                    predicates.extend(meta)
                    ref_links.extend(links)
                    ref_unlinks.extend(unlinks)
                elif self.is_package_ref(element):
                    inner_ref = self.build_package_ref(element)
                    inner_refs.append(inner_ref)
                elif element.tag == 'cond':
                    if debish_condition:
                        raise InputError, \
                              "Only one debish condition allowed."
                    debish_condition = compile_debish(element.text,
                                                      package_type,
                                                      blob_id)
                else:
                    inner_condition = self.build_condition(element,
                                                           package_type,
                                                           blob_id)
                    xml_condition.conditions.append(inner_condition)

        if debish_condition and xml_condition.conditions:
            raise InputError, \
                  "Can't mix debish and xml conditions"

        if debish_condition:
            condition = debish_condition
        else:
            condition = PhantomConditionWrapper(xml_condition,
                                                package_type,
                                                blob_id)

        ref = PackageStanza(package_type, blob_id, condition, predicates)
        ref.children = inner_refs
        ref.links = ref_links
        ref.unlinks = ref_unlinks
        return ref

    def normalize_text(self, element, strip):
        '''Read a text string from an xml element.

        Null values are converted to the empty string.

        strip is a boolean indicating if whitespace should be stripped
        from the ends of the string.
        '''
        value = None
        if element is not None:
            value = element.text
            if strip:
                value = value.strip()
        if not value:
            value = ''
        return value

    def read_field(self, root, name, strip = True):
        '''Return the text of the first element with the given name.

        Search is limited to direct descendants of the root.

        See normalize_text for strip description.
        '''
        element = root.find(name)
        return self.normalize_text(element, strip)

    def read_multifield(self, root, name, strip = True):
        '''Return the text of all elements with given name in the root.

        Search is limited to direct descendants of the root.

        See normalize_text for strip description.
        '''
        elements = root.findall(name)
        value = []
        for element in elements:
            value.append(self.normalize_text(element, strip))
        return value

    def build_entity(self, root):
        '''Build up a single raw entity from an entity declaration element.
        '''
        if not 'id' in root.attrib:
            raise InputError, "id field required for entities"
        entity = Entity(root.tag, root.attrib['id'])
        for element in root:
            key_tuple = parse_domain(element.tag)
            entity[key_tuple] = element.text
        return entity

    def build_component_reference(self, component_ref_element):
        '''Build up a component reference from a component element.'''
        if component_ref_element.text.strip():
            ref = ComponentReference(component_ref_element.text.strip())
            return ref
        else:
            conditions = []
            ref_file = None
            # narrow and mask are deprecated, but still work.
            for element in component_ref_element:
                if element.tag in ('limit', 'narrow'):
                    condition = compile_debish(element.text, None, None)
                    conditions.append(condition)
                elif element.tag in ('exclude', 'mask'):
                    n_condition = compile_debish(element.text, None, None)
                    condition = rules.notc(n_condition)
                    conditions.append(condition)
                elif element.tag == 'file':
                    ref_file = element.text.strip()
                else:
                    raise InputError, \
                          'Unexpected "%s" tag in component reference' \
                          % element.tag
            if not ref_file:
                raise InputError, "No filename provided for component."
            root_condition = rules.ac(conditions)
            ref = ComponentReference(ref_file, root_condition)
            return ref

    def build_component_descriptor(self, component_element):
        '''Build up the state of this descriptor from the given element.'''
        contents_element = component_element.find('contents')
        if contents_element:
            for element in contents_element:
                if self.is_package_ref(element):
                    ref = self.build_package_ref(element)
                    self.contents.append(ref)
                elif element.tag == 'component':
                    ref = self.build_component_reference(element)
                    self.contents.append(ref)

        entities_element = component_element.find('entities')
        if entities_element:
            for element in entities_element:
                entity = self.build_entity(element)
                self.entities[(entity.ent_type, entity.ent_id)] = entity

        meta_element = component_element.find('meta')
        if meta_element:
            meta, links, unlinks = self.build_meta(meta_element)
            self.meta.extend(meta)
            self.links.extend(links)
            self.unlinks.extend(unlinks)

        self.id = self.read_field(component_element, 'id')
        self.name = self.read_field(component_element, 'name')
        self.description = self.read_field(component_element,
                                           'description',
                                           False)
        self.requires = self.read_multifield(component_element, 'requires')
        self.provides = self.read_multifield(component_element, 'provides')

    def diff_self(self, workspace, printer, show_unchanged):
        '''Run semdiff between self and its previously written state.'''
        orig_descriptor = ComponentDescriptor(self.filename)
        c_cache = workspace.world.get_backed_cache(workspace.cache)
        print_report(orig_descriptor.load(c_cache), self.load(c_cache),
                     show_unchanged, printer)


class Component(object):
    """Represents a logical PDK component.

    Do not mutate the fields of Component objects. They are meant to
    be used as hash
    """
    __slots__ = ('ref', 'cache', 'package_condition', 'type', 'links',
                 'id', 'name', 'description', 'requires', 'provides',
                 'ordered_contents', 'system', 'entities', 'meta')
    identity_fields = ('ref', 'type',
                       'id', 'name', 'description', 'requires', 'provides')

    def __init__(self, ref, cache, package_condition):
        self.ref = ref
        self.cache = cache
        self.package_condition = package_condition
        self.type = 'component'

        self.id = ''
        self.name = ''
        self.description = ''
        self.requires = []
        self.provides = []
        self.links = []

        self.ordered_contents = []
        self.system = None
        self.entities = Entities()
        self.meta = {}

    def get_ent_type(self):
        '''Getter for virtual ent_type.'''
        return self.type
    ent_type = property(get_ent_type)

    def get_ent_id(self):
        '''Getter for virtal ent_id.'''
        return self.ref
    ent_id = property(get_ent_id)

    def iter_contents(self):
        '''Iterate over all the items in ordered_contents.'''
        return self.iter_ordered_contents((Package, Component), True)

    def iter_ordered_contents(self, classes, recursive, entities = None,
                              system = None):
        '''Iterate over ordered_contents and filter by package_condition.

        The filtering is only performed on Package object.
        '''
        for item in self.iter_raw_ordered_contents(classes, recursive,
                                                   entities, system):
            if isinstance(item, Package):
                package = item
                if self.package_condition.evaluate(package):
                    yield package
            else:
                yield item

    def iter_raw_ordered_contents(self, classes, recursive,
                                  entities = None, system = None):
        '''Iterate over ordered_contents and load objects as needed.

        classes -       Only instantiate objects which would be instances
                        of the given classes.
        recursive -     True/False, recurse into child components.
        entities -      Optional, an entities object for linking.
        system -        Optional, a rule system to fire on packages.
        '''
        if not entities:
            entities = self.entities
        if not system:
            system = self.system
        for item in self.ordered_contents:
            if Package in classes and isinstance(item, PackageReference):
                package = item.load(self.cache)
                for comp_ref in item.complement:
                    package.complement.append(comp_ref.load(self.cache))
                system.fire(package)
                yield package
            elif isinstance(item, Component):
                if Component in classes:
                    yield item
                if recursive:
                    for inner_item in item.iter_ordered_contents(classes,
                                                                 recursive,
                                                                 entities,
                                                                 system):
                        yield inner_item

    def iter_direct_packages(self):
        '''Iterate over packages which are direct children.
        '''
        return self.iter_ordered_contents((Package,), False)

    def iter_packages(self):
        '''Iterate over all child packages of this component.
        '''
        return self.iter_ordered_contents((Package,), True)

    def iter_direct_components(self):
        '''Iterate over direct child components.'''
        return self.iter_ordered_contents((Component,), False)

    def iter_components(self):
        '''Iterate over all child components.'''
        return self.iter_ordered_contents((Component,), True)

    def _get_values(self):
        '''Return an immutable value representing the full identity.'''
        values = ['component']
        for field in self.identity_fields:
            value = getattr(self, field)
            if isinstance(value, list):
                value = tuple(value)
        return tuple(values)

    def __cmp__(self, other):
        return cmp(self._get_values(), other._get_values())

    def __hash__(self):
        return hash(self._get_values())


def get_deb_child_condition(package):
    """Get child condition data for a deb."""
    return rules.ac([ rules.rc(eq, 'pdk', 'name', package.pdk.sp_name),
                      rules.rc(eq, 'pdk', 'version',
                               package.pdk.sp_version),
                      rules.rc(eq, 'pdk', 'type', 'dsc') ])

def get_dsc_child_condition(package):
    """Get child condition data for a dsc."""
    type_condition = rules.oc([ rules.rc(eq, 'pdk', 'type', 'deb'),
                                rules.rc(eq, 'pdk', 'type', 'udeb') ])

    return rules.ac([ rules.rc(eq, 'pdk', 'sp-name', package.name),
                      rules.rc(eq, 'pdk', 'sp-version',
                                package.version),
                      type_condition ])

def get_rpm_child_condition(package):
    """Get child condition data for an rpm."""
    return rules.ac([ rules.rc(eq, 'pdk', 'filename',
                               package.pdk.source_rpm),
                      rules.rc(eq, 'pdk', 'type', 'srpm') ])

def get_srpm_child_condition(package):
    """Get child condition data for an srpm."""
    return rules.ac([ rules.rc(eq, 'pdk', 'source-rpm', package.filename),
                      rules.rc(eq, 'pdk', 'type', 'rpm') ])

def get_general_condition(package):
    """Get condition data for any package."""
    condition = rules.ac([ rules.rc(eq, 'pdk', 'name', package.name),
                           rules.rc(eq, 'pdk', 'version',
                                     package.version) ])
    if package.role == 'binary':
        condition.conditions.append(rules.rc(eq, 'pdk', 'arch',
                                             package.arch))
    return condition

def get_child_condition(package, stanza):
    """Get child condition data for any package."""
    condition_fn = get_child_condition_fn(package)
    child_condition = condition_fn(package)
    # Always pin the the child's parent to a single version.
    # Someday we may need a more sophisticated mechanism for RPM.
    # I'm just not sure. -dt
    parent_condition = rules.ac([ stanza.reference.condition,
                                  rules.rc(eq, 'pdk', 'version',
                                           package.version) ])
    key_condition = child_condition.conditions[0]
    key_info = (key_condition.domain, key_condition.predicate,
                key_condition.target)
    return rules.oc([child_condition, parent_condition]), key_info

child_condition_fn_map = {
    'deb': get_deb_child_condition,
    'udeb': get_deb_child_condition,
    'dsc': get_dsc_child_condition,
    'rpm': get_rpm_child_condition,
    'srpm': get_srpm_child_condition }
def get_child_condition_fn(package):
    """Determine which child condition function to use on a package."""
    return child_condition_fn_map[package.type]

class PackageReference(object):
    '''Represents a concrete package reference.'''
    def __init__(self, package_type, blob_id, condition):
        self.package_type = package_type
        self.blob_id = blob_id
        self.condition = condition
        self.complement = []

    def load(self, cache):
        '''Load the package associated with this ref.'''
        type_string = self.package_type.type_string
        package = cache.load_package(self.blob_id, type_string)
        if not(self.condition.evaluate(package)):
            message = 'Concrete package does not ' + \
                      'meet expected constraints: %s' \
                      % package.blob_id
            raise SemanticError(message)
        return package

    def is_abstract(self):
        '''Return true if this package reference is abstact.'''
        return not bool(self.blob_id)

class PackageStanza(object):
    '''Represents a package stanza as found in a component descriptor.

    This object may be somewhat recursive, as abstract stanza may also
    contain concrete stanzas.
    '''
    __slots__ = ('reference', 'predicates', 'children', 'links', 'unlinks')
    def __init__(self, package_type, blob_id, condition, predicates):
        self.reference = PackageReference(package_type, blob_id,
                                          condition)
        self.predicates = predicates
        self.children = []
        self.links = []
        self.unlinks = []

    def evaluate_condition(self, candidate):
        '''Wraper for evaluating a candidate versus the condition.'''
        return self.rule.evaluate_condition(candidate)

    def from_package(package):
        '''Instantiate a reference for the given package.'''
        fields = get_general_condition(package)
        return PackageStanza(package.package_type, package.blob_id,
                                fields, [])
    from_package = staticmethod(from_package)

    def load(self, cache):
        '''Load the package associated with this ref.'''
        return self.reference.load(cache)

    def is_abstract(self):
        '''Return true if this package stanza is abstact.'''
        return self.reference.is_abstract() and not bool(self.children)

    def get_condition_dict(self):
        '''Get a dictionary relating predicates to conditions.

        Only root level predicates are used. Predicates in deeper in
        and or or conditions are ignored.

        This is really just a hack to make __contains__ and
        __getitem__ work.
        '''
        condition_dict = {}
        for condition in self.reference.condition.conditions:
            if hasattr(condition, 'predicate'):
                key = (condition.domain, condition.predicate)
                condition_dict[key] = condition
        return condition_dict

    def __contains__(self, field):
        return field in self.get_condition_dict()

    def __getitem__(self, field):
        return self.get_condition_dict()[field].target

    def get_name(self):
        '''Get the expected name of the referenced package(s).

        Returns a blank string if no name was given.
        '''
        key = ('pdk', 'name')
        return (key in self and self[key]) or ''
    name = property(get_name)

    def get_version(self):
        '''Get the exected version of the referenced package(s).

        Returns a blank string if no version was given.
        '''
        key = ('pdk', 'version')
        return (key in self and self[key]) or ''
    version = property(get_version)

    def get_arch(self):
        '''Get the exected arch of the referenced package(s).

        Returns a blank string if no arch was given.
        '''
        key = ('pdk', 'arch')
        return (key in self and self[key]) or ''
    arch = property(get_arch)

    def get_rule(self):
        '''Construct a rule object for this reference.'''
        raw_condition = self.reference.condition
        if isinstance(raw_condition, PhantomConditionWrapper):
            condition = raw_condition.phantom_wrapper
        else:
            condition = raw_condition
        actions = [ ActionMetaSet(*p) for p in self.predicates ]
        actions += [ ActionLinkEntities(*p) for p in self.links ]
        actions += [ ActionUnlinkEntities(*p) for p in self.unlinks ]
        action = CompositeAction(actions)
        return Rule(condition, action)
    rule = property(get_rule)

    def _get_parent_match(self, find_package, cache, world_index):
        '''Find a package which represents a match for this stanza.

        The world index is searched. It is only efficient if this stanza
        has a name condition.

        find_package - a function we can call to pick the right package
                       out of a world_items iterator.
        cache        - a workspace cache
        world_index  - a world index we will use to search for candidate
                       packages.
        abstract_constraint -
                       whether stanzas must be resolved or unresolved.
        '''

        if self.name:
            item_list = world_index.iter_candidates(('pdk', 'name'),
                                                    self.name)
        else:
            item_list = world_index.iter_all_candidates()
            message = 'Using unoptimized package list. ' + \
                      'This operation may take a long time.\n' + \
                      ' condition = %r' % self.rule.condition
            logger = get_logger()
            logger.warn(message)

        found_package = find_package(cache, self, item_list)
        if found_package:
            return found_package
        else:
            return None

    def _get_child_condition(self, world_index, parent_match):
        '''Find a condition which represents parent and child packages.

        Also returns an iterator over potential package matches. Some
        optimization has been done to prevent this interator from covering
        the whole world.
        '''
        child_condition, candidate_key_info = \
            get_child_condition(parent_match, self)

        if self.name:
            item_list = world_index.iter_candidates(('pdk', 'name'),
                                                    self.name)
        else:
            item_list = world_index.iter_all_candidates()
        parent_candidates = item_list

        key_domain, key_field, key_value = candidate_key_info
        candidate_key = (key_domain, key_field)
        child_candidates = world_index.iter_candidates(candidate_key,
                                                       key_value)
        candidates = chain(parent_candidates, child_candidates)
        return (child_condition, candidates)

    def resolve(self, find_package, cache, world_index):
        """Resolve this stanza by searching the world_index.

        find_package - a function we can call to pick the right package
                       out of a world_items iterator.
        cache        - a workspace cache
        world_index  - a world index we will use to search for candidate
                       packages.
        """
        parent_match = self._get_parent_match(find_package, cache,
                                              world_index)
        if not parent_match:
            return
        child_condition, candidate_items = \
            self._get_child_condition(world_index, parent_match)

        self.children = []

        # run through all the packages again, this time using the
        # child_conditions of new references.
        for item in candidate_items:
            ghost_package = item.package
            if child_condition.evaluate(ghost_package):
                new_child_ref = \
                    PackageStanza.from_package(ghost_package)
                expected_filename = ghost_package.filename
                found_filename = ghost_package.pdk.found_filename
                if expected_filename != found_filename:
                    predicate = ('pdk', 'filename', found_filename)
                    new_child_ref.predicates.append(predicate)
                self.children.append(new_child_ref)

        # Remove duplicates.
        child_set = Set(self.children)
        new_child_list = list(child_set)
        new_child_list.sort()
        self.children = new_child_list

    def __identity_tuple(self):
        '''Return a tuple to help cmp and hash handle this object.'''
        return self.reference.package_type.format_string, \
               self.reference.package_type.role_string, \
               self.reference.package_type.type_string, \
               self.name, self.version, self.arch, \
               self.reference.blob_id, \
               self.reference.condition, tuple(self.predicates), \
               tuple(self.children)

    def __cmp__(self, other):
        return cmp(self.__identity_tuple(), other.__identity_tuple())

    def __hash__(self):
        return hash(self.__identity_tuple())

class ComponentReference(object):
    '''Represents a component reference.

    Use self.load() as a shortcut to the component descriptor.
    '''
    def __init__(self, filename, condition = rules.tc()):
        self.filename = filename
        self.condition = condition

    def load(self, get_desc):
        '''Instantiate the ComponentDescriptor object for this reference.
        '''
        return get_desc(self.filename)

class ActionMetaSet(object):
    '''A rule action which sets domain, predicate, target on the entity.
    '''
    def __init__(self, domain, predicate, target):
        self.domain = domain
        self.predicate = predicate
        self.target = target

    def execute(self, entity):
        '''Execute this action.'''
        entity[(self.domain, self.predicate)] = self.target

    def __str__(self):
        return 'set meta %r' % ((self.domain, self.predicate,
                                 self.target),)

    __repr__ = __str__

class ActionLinkEntities(object):
    '''A rule action which links the entity to another entity.

    ent_type, type of the entity to link to.
    ent_id, ent_id of the entity to link to.
    '''
    def __init__(self, ent_type, ent_id):
        self.ent_type = ent_type
        self.ent_id = ent_id

    def get_key(self):
        '''Getter for the complete key.'''
        return (self.ent_type, self.ent_id)
    key = property(get_key)

    def execute(self, entity):
        '''Execute this action.'''
        if self.key not in entity.links:
            entity.links.append(self.key)

    def __str__(self):
        return 'link %r' % (self.key,)

    __repr__ = __str__

class ActionUnlinkEntities(object):
    '''A rule action which unlinks two entities.

    ent_type, type of the entity to link to.
    ent_id, ent_id of the entity to link to.

    If the unlinked entity does not exist, this action is a noop.
    '''
    def __init__(self, ent_type, ent_id):
        self.ent_type = ent_type
        self.ent_id = ent_id

    def get_key(self):
        '''Getter for the complete key.'''
        return (self.ent_type, self.ent_id)
    key = property(get_key)

    def execute(self, entity):
        '''Execute this action.'''
        while self.key in entity.links:
            entity.links.remove(self.key)

    def __str__(self):
        return 'unlink %r' % (self.key,)

    __repr__ = __str__

class PhantomConditionWrapper(object):
    '''A delicate utility class for making conditions write to xml.

    Don't use this class outside this module. It is purpose built for a
    single use and probably won't work for much of anything else.

    condition       - assumed to be an and condition.
    package_type    - Optional: package type candidates must match
    blob_id         - Optional: blob_id of candidates
    '''
    def __init__(self, condition, package_type, blob_id):
        self.package_type = package_type
        self.blob_id = blob_id
        self.phantom_wrapper = rules.ac([])
        self.condition = condition
        self.conditions = self.condition.conditions
        conditions = self.phantom_wrapper.conditions
        if blob_id or package_type:
            if blob_id:
                conditions.append(rules.rc(eq, 'pdk', 'blob-id', blob_id))
            conditions.extend(condition.conditions)
            if package_type.format_string == 'unknown':
                role_string = package_type.role_string
                conditions.append(rules.rc(eq, 'pdk', 'role', role_string))
            else:
                type_string = package_type.type_string
                conditions.append(rules.rc(eq, 'pdk', 'type', type_string))

    def evaluate(self, candidate):
        '''Use the full wrapper to evaluate the condition.'''
        return self.phantom_wrapper.evaluate(candidate)

    def get_identity(self):
        '''Return the identity of this object for comparisons.'''
        return self.phantom_wrapper

    def __str__(self):
        return '(*phantom* %s )' % self.condition

    __repr__ = __str__

make_comparable(PhantomConditionWrapper)

# vim:set ai et sw=4 ts=4 tw=75:
