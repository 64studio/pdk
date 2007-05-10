# $Progeny$
#
#   Copyright 2003, 2004, 2005 Progeny Linux Systems, Inc.
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

"""This module acts as a helper for building runtime systems for
installers."""

import os
import types
import re
import tempfile
import xml.dom
import xml.dom.minidom
import urllib2

import picax.config
import picax.apt
import picax.log

class PackageDocument:
    "Parse Packages files. Provide group operations for their packages."

    def __init__(self, document):
        self.document = document
        self.package_nodes = []
        self.package_list = []
        self.default_package_node = None
        self._create_package_nodes()
        self._create_package_list()
        self.log = picax.log.get_logger()

    def _create_package_list(self):
        list_node = None
        for node in self.document.documentElement.childNodes:
            if node.nodeType != xml.dom.Node.ELEMENT_NODE:
                continue
            if node.tagName not in ("architecture", "list"):
                raise ValueError, "invalid XML file"
            if node.tagName == "list":
                list_node = node
                break

        if list_node:
            for node in list_node.childNodes:
                if node.nodeType != xml.dom.Node.ELEMENT_NODE:
                    continue
                if node.tagName != "entry":
                    raise ValueError, "invalid list in XML file"
                text = ""
                for subnode in node.childNodes:
                    if subnode.nodeType == xml.dom.Node.TEXT_NODE:
                        text = text + subnode.data
                if text:
                    self.package_list.append(text.encode().strip())
        else:
            for node in self.package_nodes:
                self.package_list.append(
                    node.node.getAttribute("name").encode())

    def _create_package_nodes(self):
        arch = picax.config.get_config()["arch"]

        for node in self.document.documentElement.childNodes:
            if node.nodeType != xml.dom.Node.ELEMENT_NODE:
                continue
            if node.tagName not in ("architecture", "list"):
                raise ValueError, "invalid XML file"
            if node.tagName != "architecture":
                continue

            node_arch = node.getAttribute("type")
            if node_arch == "all" or node_arch == arch:
                for subnode in node.childNodes:
                    if subnode.nodeType != xml.dom.Node.ELEMENT_NODE:
                        continue
                    if subnode.attributes.has_key("default"):
                        self.default_package_node = subnode
                    else:
                        self.package_nodes.append(Package(self, subnode))

    def _check_nodes(self):
        if len(self.package_nodes) == 0:
            self._create_package_nodes()
        if len(self.package_list) == 0:
            self._create_package_list()

    def _get_node_by_name(self, name):
        for node in self.package_nodes:
            if node.node.getAttribute("name") == name:
                return node

        if self.default_package_node:
            new_node = self.default_package_node.cloneNode(True)
            new_node.removeAttribute("default")
            new_node.setAttribute("name", name)
            self.default_package_node.parentNode.appendChild(new_node)
            new_node_obj = Package(self, new_node)
            self.package_nodes.append(new_node_obj)
            return new_node_obj

        raise ValueError, "named node %s not found" % (name,)

    def _get_node_list(self):
        resolved_list = picax.apt.resolve_package_list(self.package_list,
                                                       None, False)
        nodes = []
        for pkg_cluster in resolved_list:
            if isinstance(pkg_cluster, types.ListType):
                pkg_name_list = pkg_cluster
            else:
                pkg_name_list = [pkg_cluster]

            for pkg_name in pkg_name_list:
                node = None
                try:
                    node = self._get_node_by_name(pkg_name)
                except ValueError:
                    self.log.warning("Could not find %s" % (pkg_name,))

                if node:
                    nodes.append(node)

        return nodes

    def unpack_all(self, destination_path):
        "Unpack all packages in this index to the given path."

        self._check_nodes()

        for node in self._get_node_list():
            try:
                node.unpack(destination_path)
            except OSError:
                self.log.warning("Could not unpack %s"
                                 % (node.node.getAttribute("name"),))

    def run_script_all(self, destination_path):
        """Run all post-installation scripts for packages unpacked
        to the given path."""

        self._check_nodes()

        for node in self._get_node_list():
            node.run_script(destination_path)

    def load_all(self, destination_path):
        "Unpack and script all packages to the given path."

        self._check_nodes()

        for node in self._get_node_list():
            node.load(destination_path)

class Package:
    """This class represents a package that needs to be unpacked to the
    runtime image."""

    def __init__(self, document, node):
        self.document = document
        self.node = node
        self.pkg_uri = None
        self.pkg_path = None
        self.pkg_path_ref = 0
        self.temp_pkg_path = False
        self.log = picax.log.get_logger()
        self.manidiff = None
        self.script = None

        self._check_node()

    def _check_node(self):
        if self.node.nodeType != xml.dom.Node.ELEMENT_NODE:
            raise ValueError, "package information must be in an element"

        if self.node.tagName[-7:] != "package":
            raise ValueError, "invalid tag found in XML file: %s" \
                  % (self.node.tagName,)

        self.manidiff = None
        self.script = None
        for node in self.node.childNodes:
            if node.nodeType != xml.dom.Node.ELEMENT_NODE:
                continue

            if node.tagName == "manidiff":
                if self.manidiff is not None:
                    raise ValueError, "multiple manidiffs found in package"
                self.manidiff = node
            if node.tagName == "script":
                if self.script is not None:
                    raise ValueError, "multiple scripts found in package"
                self.script = node

    def _get_package_file(self):
        if self.pkg_uri is None:
            pkg_name = self.node.getAttribute("name")
            self.pkg_uri = picax.apt.find_package_uri(pkg_name)

        if self.pkg_path is None:
            remove_temp_pkg = False
            pkg_path = None
            if self.pkg_uri[:5] == "http:":
                tmp_path = picax.config.get_config()["temp_dir"]
                pkg_path = tmp_path + "/" + os.path.basename(self.pkg_uri)
                tmp_pkg = open(pkg_path, "w")
                net_pkg = urllib2.urlopen(self.pkg_uri)
                tmp_pkg.write(net_pkg.read())
                net_pkg.close()
                tmp_pkg.close()
                remove_temp_pkg = True
            elif self.pkg_uri[:5] == "file:":
                pkg_path = self.pkg_uri[5:]
                while pkg_path[1] == "/":
                    pkg_path = pkg_path[1:]
            else:
                raise RuntimeError, "cannot recognize URI: %s" \
                      % (self.pkg_uri,)

            self.pkg_path = pkg_path
            self.temp_pkg_path = remove_temp_pkg
        else:
            self.pkg_path_ref = self.pkg_path_ref + 1

    def _free_package_file(self):
        if self.pkg_path_ref <= 1:
            if self.temp_pkg_path:
                os.unlink(self.pkg_path)
                self.pkg_path = None
                self.temp_pkg_path = False
            self.pkg_path_ref = 0
        else:
            self.pkg_path_ref = self.pkg_path_ref - 1

    def _get_file_list(self):
        self._get_package_file()

        dpkg_process = os.popen("dpkg --contents %s" % (self.pkg_path,))
        content_lines = dpkg_process.readlines()
        dpkg_process.close()

        paths = []
        for line in content_lines:
            items = re.split(r'\s+', line.strip())
            path_items = items[5:]
            path = path_items[0]
            if path[0] == ".":
                path = path[1:]
            paths.append(path)

        self._free_package_file()
        return paths

    def _check_path(self, path, node, acc_path = ""):
        node_path = node.getAttribute("path")
        total_path = acc_path
        if (len(total_path) == 0 or total_path[-1] != "/") and \
           node_path[0] != "/":
            total_path = total_path + "/"
        total_path = total_path + node_path

        if path[:len(total_path)] == total_path:
            for child_node in node.childNodes:
                if child_node.nodeType != xml.dom.Node.ELEMENT_NODE:
                    continue
                child_check = self._check_path(path, child_node,
                                               total_path)
                if child_check:
                    return child_check
            return node.tagName
        else:
            return None

    def _get_remove_list(self):
        manidiff_nodes = self.node.getElementsByTagName("manidiff")
        if len(manidiff_nodes) < 1:
            return []
        if len(manidiff_nodes) > 1:
            raise ValueError, "only one manidiff node allowed per package"
        manidiff_node = manidiff_nodes[0]

        remove_list = []
        pkg_files = self._get_file_list()
        for fn in pkg_files:
            for node in manidiff_node.childNodes:
                if node.nodeType != xml.dom.Node.ELEMENT_NODE:
                    continue
                check_result = self._check_path(fn, node)
                if check_result == "exclude":
                    remove_list.append(fn)
                    break

        return remove_list

    def unpack(self, destination_path):
        "Unpack the package to the given path."

        self._get_package_file()

        os.system("ar -p %s data.tar.gz | zcat | (cd %s && tar -xf -)"
                  % (self.pkg_path, destination_path))

        check_dirs = []
        for exclude_file in self._get_remove_list():
            try:
                total_ex_path = destination_path + exclude_file
                if os.path.isdir(total_ex_path):
                    check_dirs.append(total_ex_path)
                else:
                    os.unlink(total_ex_path)
            except OSError:
                self.log.warning("Couldn't remove %s" % (exclude_file,))

        for check_dir in check_dirs:
            if os.path.isdir(check_dir):
                os.rmdir(check_dir)

        self._free_package_file()

    def run_script(self, destination_path):
        "Run the package scripts for the given path."

        script_nodes = self.node.getElementsByTagName("script")
        if len(script_nodes) < 1:
            return
        if len(script_nodes) > 1:
            raise ValueError, "only one script node allowed per package"
        script_node = script_nodes[0]

        interpreter = script_node.getAttribute("interpreter")
        script = ""
        for node in script_node.childNodes:
            if node.nodeType not in (xml.dom.Node.TEXT_NODE,
                                     xml.dom.Node.CDATA_SECTION_NODE):
                raise ValueError, "scripts cannot contain other XML nodes"
            script = script + node.data

        os.environ["PICAX_DEST"] = destination_path

        if interpreter == "python":
            script = script.replace("\r\n", "\n") + "\n"
            script_code = compile(script, "<XML package script>", "exec")
            namespace = { "dest": destination_path }
            exec script_code in namespace
        else:
            tempfn = tempfile.mktemp()
            tempf = open(tempfn, "w")
            tempf.write(script)
            tempf.close()

            os.system("%s %s" % (interpreter, tempfn))
            os.unlink(tempfn)

    def load(self, destination_path):
        "Unpack and script the package to the given path."

        self.unpack(destination_path)
        self.run_script(destination_path)

def read_package_file(fn = None, f = None):
    """Read a given package index, either by filename or file object,
    and return a PackageDocument object for it."""

    if fn is None and f is None:
        raise ValueError, "must provide either a file name or file object"

    if f is None:
        f = open(fn)

    return PackageDocument(xml.dom.minidom.parse(f))

# vim:set ai et sw=4 ts=4 tw=75:
