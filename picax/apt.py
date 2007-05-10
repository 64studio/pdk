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

"""This module provides an interface to apt's package dependency
resolver."""

import os
import types
import shutil
import apt_pkg

import picax.config
import picax.log

cache = None
config = {}

class FoundPackage(Exception):
    "Exception to flag when a package is found."
    pass

def init():
    "Initialize apt and prepare it for dependency solving."

    global cache

    if cache:
        raise RuntimeError, "apt is already initialized"

    global_conf = picax.config.get_config()
    base_dir = global_conf["temp_dir"] + "/apt-info"
    path = global_conf["base_path"]

    distro_hash = {}
    for (distro, comp) in global_conf["repository_list"]:
        if not distro_hash.has_key(distro):
            distro_hash[distro] = []
        distro_hash[distro].append(comp)
    distro_list = [(x, distro_hash[x]) for x in distro_hash.keys()]

    subdirs = ("state", "state/lists", "state/lists/partial", "cache",
               "cache/archives", "cache/archives/partial")

    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.mkdir(base_dir)

    for subdir in subdirs:
        os.mkdir(base_dir + "/" + subdir)

    status = open("%s/state/status" % (base_dir,), "w")
    status.close()

    conf = open("%s/apt.conf" % (base_dir,), "w")
    conf.write("""
Dir "%s/"
{
  State "state/" {
    status "status";
  };
  Cache "cache/";
  Etc "%s/";
};
""" % (base_dir, base_dir))
    conf.close()

    slist = open("%s/sources.list" % (base_dir,), "w")
    for (distro, components) in distro_list:
        for component in components:
            slist.write("deb file://%s %s %s\n"
                        % (path, distro, component))
    if global_conf.has_key("correction_apt_repo"):
        slist.write(global_conf["correction_apt_repo"] + "\n")
    slist.close()

    os.system("apt-get --config-file %s/apt.conf update" % (base_dir,))

    # Add base media to apt's cache.

    for base_media_dir in global_conf["base_media"]:
        os.system("apt-cdrom --config-file %s/apt.conf -d %s -m add"
                  % (base_dir, base_media_dir))

    # Initialize the python-apt bindings.

    apt_pkg.InitConfig()
    apt_pkg.ReadConfigFile(apt_pkg.Config, "%s/apt.conf" % (base_dir,))
    apt_pkg.InitSystem()

    cache = apt_pkg.GetCache()
    global_conf["apt_path"] = base_dir

def _find_package_in_cache(pkg_name):
    global cache

    found_pkg = None
    for pkg in cache.Packages:
        if pkg.Name == pkg_name:
            found_pkg = pkg
            break

    if found_pkg is None:
        raise RuntimeError, "could not find package %s" % (pkg_name,)

    return found_pkg

def find_package_uri(pkg_name):
    "Get a URI to the binary package with the given name."

    global_conf = picax.config.get_config()
    found_pkg = _find_package_in_cache(pkg_name)
    if len(found_pkg.VersionList) <= 0:
        raise RuntimeError, "package %s exists, but cannot be found" \
              % (pkg_name,)

    full_uri = None
    for pkg_version in found_pkg.VersionList:
        if full_uri:
            break

        pkg_records = apt_pkg.GetPkgRecords(cache)
        pkg_records.Lookup(pkg_version.FileList[0])
        pkg_path = pkg_records.FileName

        base_paths = [ "file://" + global_conf["base_path"] ]
        base_paths.extend(["file://" + x
                           for x in global_conf["base_media"]])
        if global_conf.has_key("correction_apt_repo"):
            path = global_conf["correction_apt_repo"].split()[1]
            base_paths.append(path)

        for base_path in base_paths:
            if full_uri:
                break
            if base_path[:7] == "file://":
                full_path = base_path[7:] + "/" + pkg_path
                if os.path.exists(full_path):
                    full_uri = base_path + "/" + pkg_path
            else:
                full_uri = base_path + "/" + full_path

    return full_uri

def get_package_data(pkg_name_or_ver):
    "Retrieve the given package's index data."

    if isinstance(pkg_name_or_ver, types.StringType):
        version = cache[pkg_name_or_ver].VersionList[0]
    else:
        version = pkg_name_or_ver

    filename = version.FileList[0][0].FileName

    fo = open(filename)
    tag = apt_pkg.ParseTagFile(fo)
    tag_valid = 1
    while tag_valid:
        if tag.Section["Package"] == version.ParentPkg.Name:
            break
        tag_valid = tag.Step()

    if not tag_valid:
        raise RuntimeError, "could not find package in its cache file"

    results = {}
    for key in tag.Section.keys():
        results[key] = tag.Section[key]

    fo.close()
    return results

def _get_latest_version(pkg):
    latest = None
    for ver in pkg.VersionList:
        if not latest:
            latest = ver
        elif apt_pkg.VersionCompare(ver.VerStr, latest.VerStr) > 0:
            latest = ver

    return latest

def _match_version(ver1, ver2):
    return (ver1.ParentPkg.Name == ver2.ParentPkg.Name and \
            ver1.VerStr == ver2.VerStr)

def _match_dep(target_ver, source_ver, dep_type):
    if not source_ver.DependsList.has_key(dep_type):
        return False

    for dep in source_ver.DependsList[dep_type]:
        for dep_alternative in dep:
            for dep_target in dep_alternative.AllTargets():
                if dep_target.ParentPkg.Name == target_ver.ParentPkg.Name \
                       and dep_target.VerStr == target_ver.VerStr:
                    return True

    return False

def resolve_package_list(pkgs, pkgs_to_ignore, loose_deps = True):
    """Resolve the dependencies in the given list of packages, returning
    a new list in dependency order.  Ignore the dependencies for packages
    in pkgs_to_ignore (and don't include them in the list, either)."""

    log = picax.log.get_logger()
    queue = []
    results = []
    result_versions = {}
    reject = []
    bad_deps = []
    in_list = pkgs[:]

    if pkgs_to_ignore is None:
        ignore_dict = {}
    else:
        ignore_dict = dict(pkgs_to_ignore)

    # This is the loop that resolves all the dependencies.

    while len(in_list) > 0:

        # Take each package in turn off the input list and add it
        # to the queue.

        current_in = in_list.pop(0)

        # Make sure that a package by this name exists; if not, add it
        # to the rejects list.

        current_ver = _get_latest_version(cache[current_in])

        if not current_ver:
            reject.append(current_in)
            continue

        # Add the package to the queue.

        queue.append(current_ver)

        # Prepare to collect cluster information.

        cluster = []
        cluster_handled = []

        # Now resolve the queue.  The package, and its depenencies,
        # will be added in the proper order.

        while len(queue) > 0:

            # Long queue lengths most likely mean loops.

            if len(queue) > 100:
                raise RuntimeError, "queue length too long"

            # Get the most recent dependency off the queue.

            current = queue.pop()

            # Short-circuit the whole process if we've already
            # had to do it before to resolve some other package
            # dependency.

            if result_versions.has_key(current.ParentPkg.Name):
                rv = result_versions[current.ParentPkg.Name]
                if rv != current.VerStr:
                    raise RuntimeError, \
                          "package added twice with different versions"
                continue

            # Also short-circuit if the package appears in the ignore
            # dictionary; we assume that these packages are depsolved.

            if ignore_dict.has_key(current.ParentPkg.Name):
                if ignore_dict[current.ParentPkg.Name] == current.VerStr:
                    continue

            # Look through this package's dependencies for ones
            # that haven't been seen yet.  If there are any, add
            # them to the top of the queue and loop.

            found_dep = False
            dep_list = []
            for key in ("PreDepends", "Depends"):
                if current.DependsList.has_key(key):
                    dep_list.extend(current.DependsList[key])
            for dep in dep_list:

                # For each ORed dependency, check that at least one
                # has been added.  If one has, stop immediately and go
                # on to the next dependency.  All the while, look for
                # candidate packages to add to the queue.

                found = False
                candidate = None
                cluster_candidate = None

                try:

                    # Collapse all the possible alternatives into a
                    # single list.

                    alt_list = []
                    for dep_alternative in dep:

                        # Skip deps we've already flagged as bad.

                        if loose_deps:
                            for bad_dep in bad_deps:
                                d1 = dep_alternative
                                d2 = bad_dep
                                if d1.CompType == d2.CompType and \
                                   d1.TargetVer == d2.TargetVer and \
                                   d1.TargetPkg.Name == d2.TargetPkg.Name:
                                    continue

                        for dep_target in dep_alternative.AllTargets():
                            alt_list.append(dep_target)

                    # Now loop through the alternatives, looking for
                    # a candidate to satisfy the dependency.

                    for dep_target in alt_list:
                        disqualified = False

                        # If the target is in the ignore list, this
                        # is as good as having the package available.

                        if ignore_dict.has_key(dep_target.ParentPkg.Name):
                            ign = ignore_dict[dep_target.ParentPkg.Name]
                            if ign == dep_target.VerStr:
                                raise FoundPackage

                        # If the dependency is part of a cluster, flag
                        # it.  This way, the dep gets handled, and the
                        # current package gets added to the cluster if
                        # needed.

                        cluster_names = [x.ParentPkg.Name
                                         for x in
                                         cluster + cluster_handled]
                        if dep_target.ParentPkg.Name in cluster_names:
                            cluster_candidate = dep_target
                            raise FoundPackage

                        # If the dependency is in the queue, there's
                        # some kind of loop.  Report that we've found
                        # a match, but also report that we need a
                        # cluster.

                        for item in queue:
                            if _match_version(item, dep_target):
                                cluster_candidate = dep_target
                                raise FoundPackage

                        # Otherwise, check to make sure the package
                        # isn't already in the results.

                        if result_versions.has_key(
                            dep_target.ParentPkg.Name):
                            rv = result_versions[dep_target.ParentPkg.Name]
                            if rv != dep_target.VerStr:
                                raise RuntimeError, \
"version mismatch with already added package"
                            raise FoundPackage

                        # If it's not already in the results, maybe
                        # it's a candidate for adding to the results.

                        if not loose_deps and not candidate and \
                           not disqualified:
                            for result_cluster in results:
                                if isinstance(result_cluster,
                                              types.ListType):
                                    rlist = result_cluster
                                else:
                                    rlist = [result_cluster]
                                for result in rlist:
                                    if _match_dep(dep_target, result,
                                                  "Conflicts"):
                                        disqualified = True
                                    elif _match_dep(result, dep_target,
                                                    "Conflicts"):
                                        disqualified = True

                        # We don't have a valid candidate, and this
                        # package looks to be a good one.

                        if not candidate and not disqualified:
                            candidate = dep_target

                # This is where we end up if a package fulfilling
                # a dependency alternative has already been added
                # to some list.

                except FoundPackage:
                    found = True

                # If no alternative was found in the current list,
                # add the candidate we found to the queue.

                if not found:

                    # If no candidate package was found either, then
                    # we have an unresolvable dependency.

                    if not candidate:
                        if loose_deps:
                            log.warning(
                                "Could not resolve dep '%s' for package %s"
                                % (str(dep), current.ParentPkg.Name))
                            for dep_alternative in dep:
                                bad_deps.append(dep_alternative)
                            found_dep = False
                        else:
                            raise RuntimeError, \
                                  "cannot find '%s' dep for package %s" \
                                  % (str(dep), current.ParentPkg.Name)

                    else:

                        # Re-add the current package to the queue.

                        queue.append(current)

                        # Add the candidate after the current package,
                        # so it gets depsolved first.

                        queue.append(candidate)
                        found_dep = True
                        break

                # Otherwise, if a cluster is needed, set it up.

                elif cluster_candidate:
                    rev_queue = queue[:]
                    rev_queue.reverse()
                    cluster_changed = False
                    for candidate in [current] + rev_queue:
                        cluster_names = [x.ParentPkg.Name
                                         for x in
                                         cluster + cluster_handled]
                        if not candidate.ParentPkg.Name in cluster_names:
                            cluster.append(candidate)
                            cluster_changed = True
                        if candidate.ParentPkg.Name == \
                           cluster_candidate.ParentPkg.Name:
                            break

                    # Only interrupt the dep loop if we changed a cluster.

                    if cluster_changed:
                        queue.append(current)
                        found_dep = True
                        break

            # We added a dep to the queue, so re-run the queue.

            if found_dep:
                continue

            # Handle the case where the package is a part of a cluster.
            # Since no deps were added, the cluster member can consider
            # itself "handled".

            if current in cluster:
                cluster.remove(current)
                cluster_handled.append(current)

                # If we've handled the entire cluster, then it's time to
                # add the cluster to the results.

                if len(cluster) == 0:
                    results.append(cluster_handled)
                    for item in cluster_handled:
                        item_name = item.ParentPkg.Name
                        if not result_versions.has_key(item_name):
                            result_versions[item_name] = item.VerStr
                        else:
                            if result_versions[item_name] != item.VerStr:
                                raise RuntimeError, \
"two packages with same names but different versions added (cluster)"
                    cluster_handled = []

                continue

            # "Leaf" dependency, no cluster.

            pkg_name = current.ParentPkg.Name
            results.append(current)
            if not result_versions.has_key(pkg_name):
                result_versions[pkg_name] = current.VerStr
            else:
                if result_versions[pkg_name] != current.VerStr:
                    raise RuntimeError, \
"two packages with same names but different versions added"

    # All done.  Now get the package names, and return them.

    final = []
    for item in results:
        if isinstance(item, types.ListType):
            final.append([x.ParentPkg.Name for x in item])
        else:
            final.append(item.ParentPkg.Name)

    return final

# vim:set ai et sw=4 ts=4 tw=75:
