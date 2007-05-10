# $Progeny$
#
# Split the aggregated repositories.
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

"""This module splits a group of picax.package.Package objects into
multiple pieces, each a given size or smaller.  (This size is provided
from the configuration.)"""

import types

import picax.config
import picax.log

def _get_binary_and_source(binary_name, binary_list, source_list):
    """Take a binary package name (or a list of names that must be kept
    together) and lists of binary packages and source packages, and
    return two lists: one of packages to add now, and one of packages
    to add later.  'Now' and 'later' have to do with the source packing
    type."""

    conf = picax.config.get_config()
    log = picax.log.get_logger()

    if type(binary_name) is not types.ListType:
        binary_names = [binary_name]
    else:
        binary_names = binary_name

    binary_pkgs = [pkg for pkg in binary_list
                   if pkg["Package"] in binary_names]

    if len(binary_pkgs) < 1:
        raise IndexError, \
              "package(s) %s requested for splitting not found" \
              % (binary_name,)

    now_pkgs = binary_pkgs
    later_pkgs = []

    source_pkgs = []
    if conf["source"] != "none":
        for now_pkg in now_pkgs:
            (source_name, source_version) = now_pkg.get_source_info()
            new_source_pkgs = [pkg for pkg in source_list
                               if pkg["Package"] == source_name and
                               pkg["Version"] == source_version]
            if len(new_source_pkgs) < 1:
                log.warning("package %s has no proper source"
                            % (now_pkg["Package"],))
            else:
                source_pkgs.extend(new_source_pkgs)

    if source_pkgs:
        if conf["source"] == "mixed":
            now_pkgs.extend(source_pkgs)
        else:
            later_pkgs = source_pkgs

    return (now_pkgs, later_pkgs)

def split(binary_order, binary_list, source_list, first_part_size = 0):
    """Take the binary and source packages, and split them into parts
    of part_size bytes, using the given order.  Return the package
    objects stuffed into a list of lists in part order."""

    conf = picax.config.get_config()

    part_size = conf["part_size"]
    if part_size == 0:
        total_binary_size = sum([x["Package-Size"] for x in binary_list])
        total_source_size = sum([x["Package-Size"] for x in source_list])
        total_size = total_binary_size + total_source_size
        part_size = total_size / conf["num_parts"]

    post_binary_list = []
    current_size = first_part_size
    current_list = []
    part_lists = []
    already_added = []

    for pkg_name in binary_order:
        (now_pkgs, later_pkgs) = _get_binary_and_source(pkg_name,
                                                        binary_list,
                                                        source_list)
        post_binary_list.extend([x for x in later_pkgs
                                 if x not in post_binary_list])

        pkgs_to_add = [x for x in now_pkgs if x not in already_added]
        if not pkgs_to_add:
            continue

        pkg_size = sum([x["Package-Size"] for x in pkgs_to_add])

        if (current_size + pkg_size) > part_size:
            part_lists.append(current_list)
            current_list = []
            current_size = 0

        current_list.extend(pkgs_to_add)
        current_size = current_size + pkg_size

        already_added.extend(pkgs_to_add)

    if conf["source"] == "separate":
        part_lists.append(current_list)
        current_list = []
        current_size = 0

    for pkg in post_binary_list:
        if pkg in already_added:
            continue

        if (current_size + pkg["Package-Size"]) > part_size:
            part_lists.append(current_list)
            current_list = []
            current_size = 0

        current_list.append(pkg)
        current_size = current_size + pkg["Package-Size"]

        already_added.append(pkg)

    if current_list:
        part_lists.append(current_list)

    return part_lists

# vim:set ai et sw=4 ts=4 tw=75:
