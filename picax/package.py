# $Progeny$
#
# Classes for managing package information.
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

"""This module captures package information from the index files for
later use.  The functions used to load this information generally
create a PackageFactory, which creates and returns subclasses of Package
objects."""

import os
import apt_pkg

import picax.config
import picax.log

# Class definitions

class Package:
    """This class encapsulates a Package as represented in an apt
    Packages file.  Don't create one of your own; instead, rely on the
    PackageFactory class below to create these for you."""

    def __init__(self, base_path, fn, start_pos, section, distro,
                 component):
        self.base_path = base_path
        self.fn = fn
        self.start_pos = start_pos
        self.lines = []
        self.meta = {}

        self.fields = {}
        for key in section.keys():
            self.fields[key] = section[key]

        self.meta["distribution"] = distro
        self.meta["component"] = component

        self.log = picax.log.get_logger()

    def __str__(self):
        return self["Package"]

    def get_lines(self):
        "Retrieve the data about this package from the index."

        if len(self.lines) == 0:
            tagfile = open(self.fn)
            tagfile.seek(self.start_pos)
            line = tagfile.readline()
            while len(line.strip()) > 0:
                self.lines.append(line)
                line = tagfile.readline()
            tagfile.close()

        return self.lines[:]

    def get_source_info(self):
        """Retrieve the information about this package's source package.
        If the package is a source package, just return its own
        information."""

        if self.fields.has_key("Source"):
            source = self["Source"].strip().split()
            if len(source) == 1:
                return (source[0], self["Version"])
            else:
                return (source[0], source[1][1:-1])
        else:
            return (self["Package"], self["Version"])

    def link(self, dest_path):
        """Link a package to its destination in the filesystem.
        This method must be overriden in subclasses."""

        raise RuntimeError, "invoked link() on base class"

    def _get_package_size(self, key):
        """Return the package's size.  This method must be overriden
        in subclasses."""

        raise RuntimeError, "size calculation not available in base class"

    def has_key(self, key):
        "Verify that the package has the particular key."

        if self.fields.has_key(key) or \
           self._calc_meta.has_key(key) or \
           self.meta.has_key(key):
            return True
        else:
            return False

    def __getitem__(self, key):
        if self.fields.has_key(key):
            return self.fields[key]

        if not self.meta.has_key(key) and self._calc_meta.has_key(key):
            func = getattr(self, self._calc_meta[key])
            func(key)

        return self.meta[key]

    def __setitem__(self, key, value):
        if self.fields.has_key(key):
            raise KeyError, "meta field already defined in Packages file"
        self.meta[key] = value

    _calc_meta = { "Package-Size": "_get_package_size" }

class BinaryPackage(Package):
    "This is a subclass of Package to support binary packages."

    def __repr__(self):
        return "<picax.package.BinaryPackage instance: %s>" \
               % (self["Package"],)

    def link(self, dest_root_path):
        "Link the binary package to its proper destination."

        pkg_path = self["Filename"]
        src_path = self.base_path + "/" + pkg_path
        dest_path = dest_root_path + "/" + pkg_path

        if os.path.exists(dest_path):
            self.log.warning(
                "Binary package %s already copied once, skipping"
                % (self["Package"],))
            return

        pkg_dir = os.path.dirname(dest_path)
        if not os.path.exists(pkg_dir):
            os.makedirs(pkg_dir)

        os.link(src_path, dest_path)

    def _get_package_size(self, key):
        "Return the size of the package file."

        self.meta[key] = os.stat(self.base_path + "/"
                                 + self["Filename"]).st_size

class UBinaryPackage(BinaryPackage):
    "This is a subclass of Package to support binary udebs."

    def __repr__(self):
        return "<picax.package.UBinaryPackage instance: %s>" \
               % (self["Package"],)

class SourcePackage(Package):
    "This is a subclass of Package to support source packages."

    def __init__(self, base_path, fn, start_pos, section, distro,
                 component):
        Package.__init__(self, base_path, fn, start_pos,
                         section, distro, component)
        self.file_list = []

    def __str__(self):
        return "%s (source)" % (self["Package"],)

    def __repr__(self):
        return "<picax.package.SourcePackage instance: %s>" \
               % (self["Package"],)

    def _get_file_list(self):
        if not self.file_list:
            file_dir = self["Directory"]
            for file_line in self["Files"].split("\n"):
                if len(file_line.strip()) == 0:
                    continue
                fn = file_line.strip().split()[2]
                self.file_list.append(file_dir + "/" + fn)

        return self.file_list

    def link(self, dest_path):
        "Link the source package's files to their proper destinations."

        for path in self._get_file_list():
            dest_file_path = dest_path + "/" + path
            if os.path.exists(dest_file_path):
                self.log.warning(
                    "Source package %s already copied once, skipping"
                    % (self["Package"],))
                return

            pkg_dir = os.path.dirname(dest_file_path)
            if not os.path.exists(pkg_dir):
                os.makedirs(pkg_dir)

            os.link(self.base_path + "/" + path, dest_file_path)

    def _get_package_size(self, key):
        "Retrieve the total size of the package's files."

        total_size = 0
        for path in self._get_file_list():
            total_size = total_size + os.stat(self.base_path + "/"
                                              + path).st_size
        self.meta[key] = total_size

class PackageFactory:
    """This class creates Package objects from the Packages file it is
    given.  Besides the explicit function calls, PackageFactory
    objects can be treated as iterators."""

    def __init__(self, package_file_stream, base_path, distro, component):
        self.base_path = base_path
        self.distro = distro
        self.component = component
        self.package_file = package_file_stream
        self.package_parser = apt_pkg.ParseTagFile(package_file_stream)
        self.eof = False
        self.last_pos = None

        self.current_pos = self.package_parser.Offset()

    def _next_package(self):
        if self.eof:
            return

        self.last_pos = self.current_pos
        self.eof = not self.package_parser.Step()
        self.current_pos = self.package_parser.Offset()

    def get_next_package(self):
        """Retrieve the next set of package information from the index,
        and create the proper Package subclass object for it."""

        if self.eof:
            return None

        self._next_package()
        if self.eof:
            return None

        if self.package_parser.Section.has_key("Binary"):
            return SourcePackage(self.base_path, self.package_file.name,
                                 self.last_pos,
                                 self.package_parser.Section,
                                 self.distro, self.component)
        elif self.package_parser.Section["Filename"][-4:] == "udeb":
            return UBinaryPackage(self.base_path, self.package_file.name,
                                  self.last_pos,
                                  self.package_parser.Section,
                                  self.distro, self.component)
        else:
            return BinaryPackage(self.base_path, self.package_file.name,
                                 self.last_pos,
                                 self.package_parser.Section,
                                 self.distro, self.component)

    def get_packages(self):
        "Retrieve all the packages from this index."

        pkg_list = []
        package = self.get_next_package()
        while package:
            pkg_list.append(package)
            package = self.get_next_package()

        return pkg_list

    def __iter__(self):
        return self

    def next(self):
        "Return the next package in the index."

        package = self.get_next_package()
        if not package:
            raise StopIteration
        return package

# Functions.

def get_package_factory(distro, section, source = False, base_path = None):
    """Return the package factory associated with the distribution and
    section."""

    conf = picax.config.get_config()

    if base_path is None:
        base_path = conf["base_path"]

    if source:
        packages_path = "%s/dists/%s/%s/source/Sources" \
                        % (base_path, distro, section)
    else:
        packages_path = "%s/dists/%s/%s/binary-%s/Packages" \
                        % (base_path, distro, section, conf["arch"])

    packages_file = open(packages_path)
    return picax.package.PackageFactory(packages_file, base_path,
                                        distro, section)

def get_base_media_packages():
    """Return a list of binary base media packages.  These packages can
    be assumed to be available, and should not be packed onto CDs."""

    log = picax.log.get_logger()
    base_media_pkgs = []

    conf = picax.config.get_config()
    if len(conf["base_media"]) > 0:
        log.info("Reading base media packages")

        for base_media_path in conf["base_media"]:
            base_media_dists_path = base_media_path + "/dists"
            if not os.path.isdir(base_media_dists_path) or \
                   os.path.islink(base_media_dists_path):
                continue

            for dist in os.listdir(base_media_dists_path):
                for comp in os.listdir("%s/dists/%s"
                                       % (base_media_path, dist)):
                    try:
                        factory = picax.package.get_package_factory(
                            dist, comp, base_path = base_media_path)
                    except IOError:
                        continue

                    base_media_pkgs.extend([pkg for pkg in factory])

    return base_media_pkgs

def get_distro_packages(distro, section, source = False):
    """Get the packages (source or binary) from a particular distro."""

    log = picax.log.get_logger()

    package_list = []
    read_packages = {}
    factory = get_package_factory(distro, section, source = source)

    for pkg in factory:
        if read_packages.has_key(pkg["Package"]):
            if pkg["Version"] in read_packages[pkg["Package"]]:
                log.warning("Package %s is a duplicate, skipping"
                            % (str(pkg),))
                continue
            else:
                log.warning("Multiple versions of package %s exist"
                            % (str(pkg),))

        package_list.append(pkg)

    return package_list

def get_all_distro_packages():
    """Using the current configuration, get all the packages in the
    configured distributions.  Return two lists, one each for
    source and binary."""

    conf = picax.config.get_config()
    log = picax.log.get_logger()
    binary_list = []
    source_list = []

    for (distro, component) in conf["repository_list"]:
        try:
            list_name = "binary"
            binary_list.extend(get_distro_packages(distro, component))
            if conf["source"] != "none":
                list_name = "source"
                source_list.extend(get_distro_packages(distro, component,
                                                       source=True))
        except IOError:
            log.warn("Could not load %s index for %s %s"
                     % (list_name, distro, component))
            continue

    return (binary_list, source_list)

# vim:set ai et sw=4 ts=4 tw=75:
