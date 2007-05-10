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

'''
This module is meant to be a temporary stop-gap measure to provide
basic yaxml parsing to modules which still use it.

This functionality is deprecated though.
'''

from pdk.util import parse_xml

def parse_yaxml_file(filename):
    '''Return data found in the given yaxml file.'''
    tree = parse_xml(filename)
    root = tree.getroot()
    data = {}
    build_tree(data, root)
    return data.values()[0]

def build_tree(parent, element):
    '''Helper function for parse_yaxml_file.

    Actually builds the tree represented by the file contents.
    '''
    children = [ e for e in element if isinstance(e.tag, basestring) ]
    if children:
        if children[0].tag == '_':
            container = []
        else:
            container = {}

        for child in children:
            build_tree(container, child)
            data = container
    else:
        if element.text:
            data = element.text.strip()
        else:
            data = ""
    if element.tag == '_':
        parent.append(data)
    else:
        parent[element.tag] = data

# vim:set ai et sw=4 ts=4 tw=75:
