#!/usr/bin/python
#
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

import sys
import os
from elementtree import ElementTree
import pdk.component
import pdk.cache

component_prefix = "comp:progeny.com/"
toplevel_group_tags = ["id", "uservisible", "default", "name",
                       "description", "langonly"]

def munge(groupname):
    munge = groupname.replace("lsb-2.0", "lsb-3.0")
    return munge

def parse_group(node):
    info = {}
    for subnode in node:
        if subnode.tag in toplevel_group_tags:
            info[subnode.tag] = subnode.text
        elif subnode.tag[-4:] == "list":
            info[subnode.tag] = []
            for itemnode in subnode:
                if itemnode.attrib.has_key("requires"):
                    item_required = itemnode.attrib["requires"]
                else:
                    item_required = None
                if itemnode.attrib.has_key("type") and \
                   itemnode.attrib["type"] != "mandatory":
                    item_type = itemnode.attrib["type"]
                else:
                    item_type = None
                info[subnode.tag].append((itemnode.text, item_type,
                                          item_required))
        else:
            raise RuntimeError, \
                  "unknown group tag '%s' encountered" % (subnode.tag,)
    return info

def group_to_meta(groupinfo):
    xform = {}
    for tag in toplevel_group_tags + ["hierarchy"]:
        if groupinfo.has_key(tag):
            xform["comps_" + tag] = groupinfo[tag]
    return { component_prefix + groupinfo["id"]: xform }

def main():
    compsxml = ElementTree.parse(sys.argv[1])
    groupinfo = {}
    groups = []
    for node in compsxml.getroot():
        if node.tag == "group":
            grpinfo = parse_group(node)
            groups.append(grpinfo["id"])
            groupinfo[grpinfo["id"]] = grpinfo
        elif node.tag == "grouphierarchy":
            for subnode in node:
                subname = subnode.find("name").text
                for itemnode in subnode.find("subcategories"):
                    if groupinfo.has_key(itemnode.text):
                        groupinfo[itemnode.text]["hierarchy"] = subname
        else:
            raise RuntimeError, \
                  "invalid tag found in comps.xml: %s" % (node.tag,)

    cache = pdk.cache.Cache()

    for group in groups:
        if groupinfo[group].has_key("grouplist"):
            continue

        group_uri = component_prefix + munge(group)
        group_desc = pdk.component.ComponentDescriptor(group_uri)
        group_comp = group_desc.load(cache)

        # Do we need to write metadata into the component?

        if not group_comp.meta:
            group_desc.update_meta(group_to_meta(groupinfo[group]))
            group_comp = group_desc.load(cache)

        if len(group_comp.packages):
            continue

        # Now we have a comps.xml group, its associated PDK component,
        # and the knowledge that the PDK component needs to be built.
        # Find the PDK component to base this one on.

        for index in range(17, len(group_uri)):
            if os.path.exists(pdk.component.get_comp_file(group_uri[:index])):
                break

        parent_uri = group_uri[:index]
        parent_desc = pdk.component.ComponentDescriptor(parent_uri)
        parent_comp = parent_desc.load(cache)

        # Find the packages in the parent component and move them
        # to the new component.  This only marks for removal;
        # something like "pdk apply" will be needed for the
        # removal to actually happen.

        for (pkg_name, pkg_type, pkg_requires) in \
                groupinfo[group]["packagelist"]:
            package = [x for x in parent_comp.direct_packages
                       if x.name == pkg_name][0]
            pkgref = pdk.cache.get_package_reference(package)
            group_desc.add_packages([pkgref])
            parent_desc.mark_package(pkgref, "remove", "comps.xml")

            if pkg_type or pkg_requires:
                meta = { pkgref: { "ref": pkgref } }
                if pkg_type:
                    meta[pkgref]["comps_type"] = pkg_type
                if pkg_requires:
                    meta[pkgref]["comps_requires"] = pkg_requires
                group_desc.update_meta(meta)

if __name__ == "__main__":
    main()

# vim:set ai et sw=4 ts=4 tw=75:
