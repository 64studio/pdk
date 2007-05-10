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


# anacondize.py - extract metadata from a PDK project and turn it
#                 into data Anaconda can use.

import sys
import os
from elementtree import ElementTree
import pdk.cache
import pdk.component
import pdk.yaxml

def write_elements_to_file(tree, fn):
    "Since ElementTree output isn't pretty, reformat it before writing."

    tidy = os.popen("tidy -xml -asxml -i -q -w 500 > %s" % (fn,), "w")
    tree.write(tidy)
    tidy.close()

def meta_to_xml(meta):
    "Convert component metadata into a group stanza, w/o packages."

    group = ElementTree.Element("group")

    # Write the toplevel information.

    for key in ("comps_id", "comps_uservisible", "comps_default",
                "comps_name", "comps_description", "comps_langonly"):
        if not meta.has_key(key):
            continue
        value = meta[key]
        tagname = key[6:]
        sub = ElementTree.SubElement(group, tagname)
        sub.text = value

    # If we have a group list, write that in.

    if meta.has_key("comps_grouplist"):
        grplist = ElementTree.SubElement(group, "grouplist")
        for grp in meta["comps_grouplist"]:
            ElementTree.SubElement(grplist, "groupreq").text = grp

    return group

def find_comps_components(component, top_component = None):
    """Return the highest-level components with comps metadata
    in them from the top_component's point of view.  If
    top_component is not given, use component as top_component."""

    if top_component is None:
        top_component = component

    if component.ref in top_component.meta and \
       top_component.meta[component.ref].has_key("comps_id"):
        return [component]
    else:
        results = []
        for subcomponent in component.direct_components:
            results.extend(find_comps_components(subcomponent,
                                                 top_component))
        return results

def make_comps_xml(top_component):
    """Build an ElementTree for a comps.xml based on component
    metadata."""

    # Find the components with comps.xml info in them.

    comps_components = find_comps_components(top_component)

    # Get the addon component info.

    comps_addons = []
    for item in top_component.meta:
        if item[:9] == "compsxml:":
            comps_addons.append(item)

    # Create the toplevel comps XML tree.

    tree = ElementTree.ElementTree(element = ElementTree.Element("comps"))

    # Create the groups.

    hierarchy = {}
    for component in comps_components:

        # Save the group hierarchy tag.

        if top_component.meta[component.ref].has_key("comps_hierarchy"):
            tagname = top_component.meta[component.ref]["comps_hierarchy"]
            if not hierarchy.has_key(tagname):
                hierarchy[tagname] = []
            hierarchy[tagname].append(top_component.meta[component.ref]["comps_id"])

        # Convert the component metadata into XML.

        group = meta_to_xml(top_component.meta[component.ref])
        tree.getroot().append(group)

        # Write the package list.

        if not top_component.meta[component.ref].has_key("comps_grouplist"):
            pkglist = ElementTree.SubElement(group, "packagelist")
            for package in component.packages:
                if package.type != "binary":
                    continue

                pkgnode = ElementTree.SubElement(pkglist, "packagereq")

                pkgnode.text = package.name

                pkgnode.attrib["type"] = "mandatory"
                pkgref = pdk.cache.get_package_reference(package)
                if pkgref in top_component.meta:
                    pkgmeta = top_component.meta[pkgref]
                    if pkgmeta.has_key("comps_type"):
                        pkgnode.set("type", pkgmeta["comps_type"])
                    if pkgmeta.has_key("comps_requires"):
                        pkgnode.set("requires", pkgmeta["comps_requires"])

    # Write the addon groups.

    for addon in comps_addons:
        group = meta_to_xml(top_component.meta[addon])
        tree.getroot().append(group)

    # Write the group hierarchy info.

    hier_top = ElementTree.SubElement(tree.getroot(), "grouphierarchy")
    hierarchy_keys = hierarchy.keys()
    hierarchy_keys.sort()
    for key in hierarchy_keys:
        hier_category = ElementTree.SubElement(hier_top, "category")
        ElementTree.SubElement(hier_category, "name").text = key
        hier_subs = ElementTree.SubElement(hier_category, "subcategories")
        for sub in hierarchy[key]:
            ElementTree.SubElement(hier_subs, "subcategory").text = sub

    # All done.

    return tree

def main():

    # Load the component information.

    cache = pdk.cache.Cache()
    descriptor = pdk.component.ComponentDescriptor(sys.argv[1])
    top_component = descriptor.load(cache)

    # Build the comps.xml file.

    compstree = make_comps_xml(top_component)

    # Write the results.

    write_elements_to_file(compstree, "comps.xml")

if __name__ == "__main__":
    main()

# vim:set ai et sw=4 ts=4 tw=75:
