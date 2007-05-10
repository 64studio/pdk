# $Progeny$
#
# Generate new repositories from collections of packages.
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

"""This module defines the NewRepository class, which uses Package
objects from picax.package to create new repositories."""

import os
import re
import hashfile
import md5
import sha
import gzip

import picax.config

def _gen_release_key(distro, component):
    return "%s:%s" % (distro, component)

class NewRepository:
    """This class creates new repositories from picax.package.Package
    objects."""

    def __init__(self, packages, dest_path):
        self.packages = packages
        self.dest_path = dest_path
        self.config = picax.config.get_config()
        self.release_info = {}
        self.toprelease_info = {}
        self.index_paths = {}
        self.index_hashes = {}

    def _load_releases(self, base_path):
        "Load release information from the repository we came from."

        for pkg in self.packages:
            release_key = _gen_release_key(pkg["distribution"],
                                           pkg["component"])
            if release_key in self.release_info:
                continue

            toprelease_fn = "%s/dists/%s/Release" % (base_path,
                                                     pkg["distribution"])

            if os.path.exists(toprelease_fn):
                toprelease_file = open(toprelease_fn)
                self.toprelease_info[pkg["distribution"]] = \
                    toprelease_file.readlines()
                toprelease_file.close()

            release_fn = "%s/dists/%s/%s/binary-%s/Release" \
                         % (base_path, pkg["distribution"],
                            pkg["component"], self.config["arch"])

            if os.path.exists(release_fn):
                release_file = hashfile.open(release_fn)
                release_md5 = md5.new()
                release_sha = sha.new()
                release_file.add_hash(release_md5)
                release_file.add_hash(release_sha)
                release_data = release_file.read()
                release_file.close()

                self.release_info[release_key] = \
                    (release_md5, release_sha, release_data)

    def _write_packages(self):
        "Link packages to the target, and write indexes."

        index_files = {}
        hashes = {}

        for pkg in self.packages:
            distro = pkg["distribution"]
            component = pkg["component"]
            distro_key = _gen_release_key(distro, component)

            if not index_files.has_key(distro_key):
                dist_path = "dists/%s/%s/binary-%s" \
                            % (distro, component, self.config["arch"])
                src_dist_path = "dists/%s/%s/source" \
                                % (distro, component)
                os.makedirs(self.dest_path + "/" + dist_path)
                os.makedirs(self.dest_path + "/" + src_dist_path)

                if distro_key not in self.index_paths:
                    self.index_paths[distro_key] = []

                if self.release_info.has_key(distro_key):
                    for release_path in (dist_path, src_dist_path):
                        (release_md5, release_sha, release_data) = \
                            self.release_info[distro_key]
                        release_fn = "%s/Release" % (release_path,)
                        release_file = open(
                            self.dest_path + "/" + release_fn, "w")
                        release_file.write(release_data)
                        release_file.close()

                        self.index_paths[distro_key].append(release_fn)
                        hashes[release_fn] = (release_md5, release_sha)

                pkgs_fn = dist_path + "/Packages"
                pkgs_file = hashfile.open(self.dest_path + "/" + pkgs_fn,
                                          "w")
                pkgs_md5 = md5.new()
                pkgs_sha = sha.new()
                pkgs_file.add_hash(pkgs_md5)
                pkgs_file.add_hash(pkgs_sha)

                srcs_fn = src_dist_path + "/Sources"
                srcs_file = hashfile.open(self.dest_path + "/" + srcs_fn,
                                          "w")
                srcs_md5 = md5.new()
                srcs_sha = sha.new()
                srcs_file.add_hash(srcs_md5)
                srcs_file.add_hash(srcs_sha)

                self.index_paths[distro_key].extend([pkgs_fn, srcs_fn])
                index_files[distro_key] = (pkgs_file, srcs_file)
                hashes[pkgs_fn] = (pkgs_md5, pkgs_sha)
                hashes[srcs_fn] = (srcs_md5, srcs_sha)

            else:
                (pkgs_file, srcs_file) = index_files[distro_key]

            pkg.link(self.dest_path)

            if pkg.has_key("Binary"):
                index_file = srcs_file
            else:
                index_file = pkgs_file

            for line in pkg.get_lines():
                index_file.write(line)
            index_file.write("\n")

        for distro_key in index_files.keys():
            for x in index_files[distro_key]:
                x.close()
            for index_fn in self.index_paths[distro_key]:
                self.index_hashes[index_fn] = \
                    tuple([x.hexdigest() for x in hashes[index_fn]])

    def _compress_and_hash_indexes(self):
        """Create compressed versions of indexes, and their hashes.
        Also clear out zero-length files."""

        index_list = [[(x, z) for z in y]
                      for (x, y) in self.index_paths.items()]
        index_list = reduce(lambda x, y: x + y, index_list)

        for (distro_key, index_fn) in index_list:
            if index_fn[-7:] == "Release":
                continue

            if os.path.exists(self.dest_path + "/" + index_fn):
                (fn_path, fn) = os.path.split(index_fn)
                fn_size = os.stat(self.dest_path + "/" + index_fn).st_size
                if fn_size > 0:
                    gzip_fn = index_fn + ".gz"
                    gzip_hash = hashfile.open(
                        self.dest_path + "/" + gzip_fn, "w")
                    gzip_md5 = md5.new()
                    gzip_sha = sha.new()
                    gzip_hash.add_hash(gzip_md5)
                    gzip_hash.add_hash(gzip_sha)
                    gzip_file = gzip.GzipFile(fn, "w", 9,
                                              gzip_hash)

                    part_file = open(self.dest_path + "/" + index_fn)
                    gzip_file.write(part_file.read())
                    part_file.close()
                    gzip_file.close()

                    self.index_paths[distro_key].append(gzip_fn)
                    self.index_hashes[gzip_fn] = (gzip_md5.hexdigest(),
                                                  gzip_sha.hexdigest())
            else:
                fn_size = 0

            if fn_size == 0:
                if os.path.isdir(self.dest_path + "/" + fn_path):
                    for emptyfn in \
                            os.listdir(self.dest_path + "/" + fn_path):
                        os.unlink("%s/%s/%s" % (self.dest_path, fn_path,
                                                emptyfn))
                    os.rmdir(self.dest_path + "/" + fn_path)
                self.index_paths[distro_key].remove(index_fn)
                del self.index_hashes[index_fn]

    def _write_toplevel_release(self):
        "Write the toplevel Release files as needed."

        for distro in self.toprelease_info.keys():
            release_keys = [x for x in self.index_paths.keys()
                            if x.split(":", 1)[0] == distro]
            components = [x.split(":", 1)[1] for x in release_keys]

            release_file = open("%s/dists/%s/Release" % (self.dest_path,
                                                         distro), "w")

            for line in self.toprelease_info[distro]:
                if line[0].isspace():
                    continue

                (name, dummy) = re.split(r':\s*', line, 1)

                if name == "Components":
                    release_file.write("Components: %s\n"
                                       % (" ".join(components),))
                    continue
                elif name == "Architectures":
                    release_file.write("Architectures: %s\n"
                                       % (self.config["arch"]))
                    continue

                release_file.write(line)

                if name not in ("MD5Sum", "SHA1"):
                    continue

                if name == "MD5Sum":
                    hash_index = 0
                else:
                    hash_index = 1

                for component in components:
                    component_key = _gen_release_key(distro, component)
                    for fn in self.index_paths[component_key]:
                        component_path = \
                            fn.replace("dists/%s/" % (distro,), "")
                        full_path = self.dest_path + "/" + fn
                        if os.path.exists(full_path):
                            size = os.stat(full_path).st_size
                            release_file.write(
                                " %s %18d %s\n"
                                % (self.index_hashes[fn][hash_index],
                                   size, component_path))

            release_file.close()

    def write_repo(self):
        """Write the repository, using the settings the object was
        constructed with."""

        self._load_releases(self.config["base_path"])
        self._write_packages()
        self._compress_and_hash_indexes()
        self._write_toplevel_release()

# vim:set ai et sw=4 ts=4 tw=75:
