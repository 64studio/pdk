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

"""
Houses functionality used in calculating and outputting semantic diffs.
"""

import os
from sets import Set
from itertools import chain
from pdk.util import string_domain

predicate_filter = Set([
    'Architecture', 'Binary', 'Build-Conflicts', 'Build-Conflicts-Indep',
    'Build-Depends', 'Build-Depends-Indep', 'Conffiles', 'Conflicts',
    'Depends', 'Description', 'Directory', 'Essential', 'Filename',
    'Files', 'Format', 'Installed-Size', 'MD5Sum', 'Maintainer', 'Package',
    'Pre-Depends', 'Priority', 'Provides', 'Recommends', 'Replaces',
    'SHA1Sum', 'Section', 'Size', 'Source', 'Standards-Version', 'Status',
    'Suggests', 'Version', 'Uploaders', 'arch', 'name', 'extra-file',
    'found-filename', 'nosrc', 'raw-filename', 'size', 'source-rpm',
    'sp-name', 'sp-version', 'version'])

full_predicate_filter = Set([
    ('deb', 'directory'), ('deb', 'Enhances')])

def index_by_fields(packages, fields):
    """Scan packages, return a dict indexed by the given fields."""
    index = {}
    for package in packages:
        key = tuple([ package[f] for f in fields ])
        if not key in index:
            index[key] = []
        index[key].append(package)
    return index

def permute(old_packages, new_packages, anchor_fields):
    """Permute all old and new packages sharing anchor fields."""
    old_index = index_by_fields(old_packages, anchor_fields)
    new_index = index_by_fields(new_packages, anchor_fields)

    all_anchors = Set(old_index.keys()) | Set(new_index.keys())
    for anchor in all_anchors:
        for old_package in old_index.get(anchor, [None]):
            for new_package in new_index.get(anchor, [None]):
                yield old_package, new_package

def iter_diffs(old_package_list, new_package_list):
    """Permute component packages together properly and yield actions.

    Tuples yielded are of the form (action, primary, secondary).

    Action may be one of add, drop upgrade, downgrade, or unchanged.

    For add and drop, primary is the added or dropped package, secondary
    is None.

    For upgrade, downgrade, and unchanged, primary is the preexisting
    package, and secondary is the current package.
    """
    anchor_fields = [ ('pdk', f) for f in ('name', 'arch', 'type') ]
    permutations = permute(old_package_list, new_package_list,
                           anchor_fields)
    for old_package, new_package in permutations:
        if not old_package:
            yield 'add', new_package, None
            continue
        if not new_package:
            yield 'drop', old_package, None
            continue

        compared = cmp(old_package.version, new_package.version)
        if compared < 0:
            action = 'upgrade'
        elif compared > 0:
            action = 'downgrade'
        else:
            action = 'unchanged'

        yield action, old_package, new_package

def list_merge(iter_old, iter_new):
    """Perform a list merge on the two iterables.

    Iterable; yields change, item
    Change is one of ('add', 'drop')
    """
    old = list(iter_old)
    new = list(iter_new)
    old.sort()
    new.sort()

    if old and new:
        left = old.pop(0)
        right = new.pop(0)
        while old and new:
            if left == right:
                left = old.pop(0)
                right = new.pop(0)
                continue
            elif left < right:
                yield ('drop', left)
                left = old.pop(0)
            else:
                yield ('add', right)
                right = new.pop(0)
    for left in old:
        yield('drop', left)
    for right in new:
        yield('add', right)

def get_meta_key(package):
    """Returns a tuple representing a key for merging meta elements.

    Notably, it does not contain version.
    """
    return (package.name, package.type, package.arch)

def filter_predicate(predicate):
    '''Is this predicate one which we tend to not show the user?

    Some predicates are too trivial to warrant reporting.
    '''
    parsed_predicate = predicate[1]
    if parsed_predicate in predicate_filter:
        return False
    if predicate in full_predicate_filter:
        return False
    return True

def get_joinable_meta_list(component):
    """Take meta and get an iterable suitable for feeding to list_merge."""
    for package in component.iter_direct_packages():
        new_key = get_meta_key(package)
        for key, target in package.iteritems():
            domain, predicate = key
            tag = string_domain(domain, predicate)
            if filter_predicate(key):
                yield new_key, tag, target

def iter_diffs_meta(old_component, new_component):
    """Detect additions and drops of metadata items.

    Package versions are _not_ considered when comparing metadata.
    """
    old_joinable = get_joinable_meta_list(old_component)
    new_joinable = get_joinable_meta_list(new_component)

    old_joinable = list(old_joinable)
    new_joinable = list(new_joinable)

    event_names = {'add': 'meta-add', 'drop': 'meta-drop'}
    for event_type, item in list_merge(old_joinable, new_joinable):
        yield (event_names[event_type], item, None)

def filter_data(data, show_unchanged):
    '''If show_unchanged is False, filter out unchanged items.'''
    for item in data:
        if show_unchanged or item[0] != 'unchanged':
            yield item

def print_report(old_component, new_component, show_unchanged, printer):
    '''Print a human readable report diffing two components.'''
    old_package_list = list(old_component.iter_direct_packages())
    new_package_list = list(new_component.iter_direct_packages())
    diffs = iter_diffs(old_package_list, new_package_list)
    diffs_meta = iter_diffs_meta(old_component, new_component)
    data = filter_data(chain(diffs, diffs_meta), show_unchanged)
    printer(new_component.ref, data)

def print_man(ref, data):
    """Write groff source '-mmandoc -t' for the diff."""
    output = os.popen('groff -m mandoc -t -Tutf8', 'w')

    collater = {}
    for field in ('add', 'drop', 'meta-add', 'meta-drop',
                  'upgrade', 'downgrade', 'unchanged'):
        collater[field] = []

    for item in data:
        collater[item[0]].append(item[1:])

    for key in collater:
        collater[key].sort()

    print >> output, '.\\" t'
    print >> output, '.TH SEMDIFF X'
    print >> output, '.SH COMPONENT'
    print >> output, '.B', ref

    for field in ('meta-add', 'meta-drop'):
        if collater[field]:
            print >> output, '.SH', field.upper()
            print >> output, '.TS H'
            print >> output, 'lb lb lb lb lb.'
            print >> output, 'format\tname\tarch\tpredicate\ttarget'
            print >> output, '.T&'
            print >> output, 'l l l l l.'
            for item in collater[field]:
                fields = get_meta_presence_fields(item[0])
                print >> output, '\t'.join(fields)
            print >> output, '.TE'
        else:
            continue

    for field in ('add', 'drop'):
        if collater[field]:
            print >> output, '.SH', field.upper()
            print >> output, '.TS H'
            print >> output, 'lb lb lb lb lb.'
            print >> output, 'format\tname\told\tnew\tarch'
            print >> output, '.T&'
            print >> output, 'l l l l.'
            for item in collater[field]:
                fields = get_package_presence_fields(item[0], ref)
                print >> output, '\t'.join(fields)
            print >> output, '.TE'
        else:
            continue

    for field in ('upgrade', 'downgrade', 'unchanged'):
        if collater[field]:
            print >> output, '.SH', field.upper()
            print >> output, '.TS H'
            print >> output, 'lb lb lb lb lb lb.'
            print >> output, 'format\tname\told\tnew\tarch\treference'
            print >> output, '.T&'
            print >> output, 'l l l l l l.'
            for item in collater[field]:
                fields = get_package_diff_fields(item[0], item[1], ref)
                print >> output, '\t'.join(fields)
            print >> output, '.TE'
        else:
            continue


def print_bar_separated(ref, data):
    """Write bar separated data for the diff."""
    for action, primary, secondary in data:
        if action in ('add', 'drop'):
            fields = get_package_presence_fields(primary, ref)
            print '|'.join((action,) + fields)
        elif action in ('meta-add', 'meta-drop'):
            fields = get_meta_presence_fields(primary)
            print '|'.join((action,) + fields)
        else:
            old_package, new_package = primary, secondary
            fields = get_package_diff_fields(old_package, new_package, ref)
            print '|'.join((action,) + fields)

def get_meta_presence_fields(data):
    """Get fields used for added and dropped metadata."""
    key, predicate, target = data
    name, type_str, arch = key
    return (type_str, name, arch, predicate, str(target))

def get_package_diff_fields(old_package, new_package, ref):
    """Get fields used for package veresion changes."""
    return (old_package.type,
            old_package.name,
            old_package.version.full_version,
            new_package.version.full_version,
            old_package.arch,
            ref)

def get_package_presence_fields(package, ref):
    """Get fields used for added and dropped packages."""
    return (package.type,
            package.name,
            package.version.full_version,
            package.arch,
            ref)

# vim:set ai et sw=4 ts=4 tw=75:
