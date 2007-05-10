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
repogen.py

Generate a repository from component & cache
"""
import os
import os.path
from time import strftime, gmtime
import re
import md5
from sets import Set
from itertools import chain
from commands import mkarg
from pdk.exceptions import SemanticError, InputError, IntegrityFault
import pdk.log as log
from pdk.util import ensure_directory_exists, pjoin, LazyWriter, \
     parse_domain
from pdk.package import udeb

logger = log.get_logger()

__revision__ = "$Progeny$"

# The following lists are derived from the field sort order in apt.
# As of apt 0.5.28.1, that is in apt-pkg/tagfile.cc, starting at
# line 363.
deb_binary_field_order = [
    "Package", 'name', "Essential", "Status", "Priority",
    "Section", "Installed-Size", "Maintainer",
    "Architecture", 'arch', "Source", "Version", 'version', "Replaces",
    "Provides", "Depends", "Pre-Depends", "Recommends",
    "Suggests", "Conflicts", "Conffiles", "Filename",
    "Size", "MD5Sum", "SHA1Sum", "Description" ]

deb_source_field_order = [
    "Package", "Source", 'name', "Binary", "Version", 'version',
    "Priority", "Section", "Maintainer", "Build-Depends",
    "Build-Depends-Indep", "Build-Conflicts",
    "Build-Conflicts-Indep", "Architecture", 'arch',
    "Standards-Version", "Format", "Directory", "Files" ]

def make_deb_field_comparator(field_order):
    """Make a comparator which sorts apt fields into order

    Fields not appearing in the given order are sorted and placed
    after all the given fields.
    """
    field_order_dict = dict([ (f, i) for i, f in enumerate(field_order) ])
    def _comparator(field_a, field_b):
        """Field comparing closure."""
        try:
            return cmp(field_order_dict[field_a],
                       field_order_dict[field_b])
        except KeyError:
            a_in_dict = field_a in field_order_dict
            b_in_dict = field_b in field_order_dict
            if not a_in_dict and not b_in_dict:
                return cmp(field_a, field_b)
            elif a_in_dict:
                return -1
            else:
                return 1
    return _comparator

deb_source_field_cmp = make_deb_field_comparator(deb_source_field_order)
deb_binary_field_cmp = make_deb_field_comparator(deb_binary_field_order)

def compile_product(component_name, cache, repo_dir, get_desc):
    """Compile the product described by the component.

    component_name is a component to load and compile a repo from.

    cache is the package cache

    repo_dir should be an absolute directory were the repo will be
    created.
    """

    compiler = Compiler(cache)

    repo_types = { 'report': compiler.dump_report,
                   'apt-deb': compiler.create_debian_pool_repo,
                   'raw': compiler.create_raw_package_dump_repo }

    product = get_desc(component_name).load(cache)
    contents = product.meta

    if ('pdk', 'repo-type') in contents:
        repo_type_string = contents['pdk', 'repo-type']
    else:
        try:
            first_package = product.iter_packages().next()
        except StopIteration:
            message = 'The component given to repogen must have ' + \
                      'at least one package.'
            raise InputError(message)
        if first_package.format == 'deb':
            repo_type_string = 'apt-deb'
        else:
            repo_type_string = 'raw'

    if repo_type_string not in repo_types:
        message = 'invalid repo-type given for %s' % component_name
        raise InputError, message
    repo_type = repo_types[repo_type_string]

    if os.path.exists(repo_dir):
        os.system('rm -rf %s' % mkarg(repo_dir))

    repo_type(product, contents, repo_dir)

class DebianPoolInjector(object):
    """This class handles the details of putting a package into a
    traditional Debian-style pool.  It also creates apt-style headers
    for the package index.
    """

    def __init__(self, cache, package, section, repo_dir):
        self.cache = cache
        self.package = package
        self.section = section
        self.repo_dir = pjoin(repo_dir)

    def get_subsection(self):
        '''Get the repo subsection for this package.

        Used for udebs to divert their metadata into debian-installer.
        '''
        if self.package.package_type == udeb:
            return 'debian-installer'
        else:
            return None

    def get_pool_dir(self):
        """Return the top-level absolute path for the pool."""
        if self.package.role == 'binary':
            name = self.package.pdk.sp_name
        else:
            name = self.package.pdk.name

        return pjoin(self.repo_dir, 'pool', self.section, name[0], name)


    def get_pool_location(self):
        """Where should the given package be put?"""
        repo_path = self.get_pool_dir()
        repo_filename = self.package.filename
        return pjoin(repo_path, repo_filename)


    def get_relative_pool_path(self):
        """Return the top-level path for the pool, relative to what
        will become the base URI for the repository."""
        abs_path = str(self.get_pool_dir())
        rel_path = ""
        fn = ""
        psplit = os.path.split
        while fn != "pool":
            (abs_path, fn) = psplit(abs_path)
            if rel_path:
                rel_path = pjoin(fn, rel_path)
            else:
                rel_path = fn
        return rel_path


    def get_extra_pool_locations(self):
        """Return a dict { pool_location: fileref }

        Return a dictionary relating pool_locations to
        filerefs. This method only handles extra files. (diff.gz etc.)
        """
        if not hasattr(self.package.pdk, 'extra_file'):
            return {}
        pool_dir = self.get_pool_dir()
        return dict([ (pjoin(pool_dir, filename), blob_id)
                      for blob_id, dummy, filename
                      in self.package.pdk.extra_file ])


    def get_links(self):
        """Return { pool_location: fileref } for all package's filerefs

        Relate all pool locations associated with this package to their
        respective filerefs.

        This is useful for putting packages into a repository.
        """
        locations = self.get_extra_pool_locations()
        locations.update(dict([ (self.get_pool_location(),
                                 self.package.blob_id) ]))
        return locations


    def get_file_size_and_hash(self):
        """Return (size, md5) for the main package file."""

        fn = self.cache.file_path(self.package.blob_id)
        size = os.stat(fn).st_size

        f = open(fn)
        m = md5.new(f.read())
        digest = m.hexdigest()
        f.close()

        return (size, digest)

    def get_source_file_line(self, blob_id, filename):
        """Return a line appropriate for a single Sources 'Files:' entry.
        """
        md5sum = re.match('md5:(.*)', blob_id).group(1)
        return ' %s %d %s' \
               % (md5sum, self.cache.get_size(blob_id), filename)

    def get_apt_header(self):
        """Return the full apt header for the package the object
        handles.
        """
        apt_fields = {}
        # I'm not entirely sure about this, as we are tangling apt
        # knowledge with deb knowledge.
        apt_fields['Package'] = self.package.name
        apt_fields['Version'] = self.package.version.full_version
        apt_fields['Architecture'] = self.package.arch
        for predicate, value in self.package.iter_by_domains(('deb')):
            if predicate == 'arch':
                continue
            apt_fields[predicate] = value

        pool_path_dir = self.get_relative_pool_path()
        (size, md5_digest) = self.get_file_size_and_hash()
        if self.package.role == 'binary':
            field_cmp = deb_binary_field_cmp
            pool_path = os.path.join(pool_path_dir, self.package.filename)

            sp_name_str = self.package.pdk.sp_name
            if self.package.pdk.sp_version != self.package.version:
                sp_version_str = self.package.pdk.sp_version.full_version
                source_value = '%s (%s)' % (sp_name_str, sp_version_str)
            else:
                source_value = sp_name_str
            apt_fields['Source'] = source_value

            apt_fields["Size"] = str(size)
            apt_fields["Filename"] = pool_path
            apt_fields["MD5Sum"] = md5_digest
        else:
            field_cmp = deb_source_field_cmp
            pool_path = pool_path_dir
            apt_fields["Directory"] = pool_path
            extra_files = ['']
            blob_id = self.package.blob_id
            filename = self.package.filename
            extra_files.append(self.get_source_file_line(blob_id,
                                                         filename))
            for blob_id, dummy, filename in self.package.pdk.extra_file:
                extra_files.append(self.get_source_file_line(blob_id,
                                                             filename))
            extra_files_str = '\n'.join(extra_files)
            apt_fields["Files"] = extra_files_str

        sorted_fields = list(apt_fields)
        sorted_fields.sort(field_cmp)

        header_lines = []
        for key in sorted_fields:
            value = apt_fields[key]
            if value and value[0].isspace():
                spacer = ''
            else:
                spacer = ' '
            header_lines.append('%s:%s%s\n' % (key, spacer, value))
        header_lines.append('\n')
        return header_lines

    def get_architectures(self, available_archs):
        """Return the architecture this package supports."""
        if self.package.role == 'source':
            arches = ['source']
        elif self.package.arch == 'all':
            arches = available_archs - Set(['source'])
        else:
            arches = [ self.package.arch ]

        return arches


    def link_to_cache(self):
        """Hard-link the cache file into the proper location in the
        pool.
        """

        pexist = os.path.exists
        locations = self.get_links()
        for link_dest, blob_id in locations.items():
            link_src = self.cache.file_path(blob_id)
            if pexist(link_dest):
                if os.path.samefile(link_src, link_dest):
                    continue
                else:
                    message =  ", %s exists and is not %s"  \
                               % (link_dest, link_src)
                    raise IntegrityFault(message)
            link_dest_dir = os.path.dirname(link_dest)
            ensure_directory_exists(link_dest_dir)
            try:
                os.link(link_src, link_dest)
            except OSError, message:
                raise IntegrityFault(
                    "%s: Cannot link %s to %s" \
                    % (message, link_src,link_dest)
                    )

class DebianPoolRepo(object):
    """Create a full repository from a Debian pool, using
    apt-ftparchive to do the actual work.  Injectors are used to write
    the pool before running apt-ftparchive.

    WARNING: Deprecated!  Use DebianDirectPoolRepo instead."""

    tmp_dir_name = 'tmp'

    def __init__(self, work_dir, dist, arches, sections, repo_dir):
        self.work_dir = work_dir
        self.dist = dist
        self.arches = arches
        self.sections = sections
        self.repo_dir = repo_dir
        self.file_lists = self.get_file_lists()


    def get_tmp_dir(self):
        """Return the path for a temporary work area."""
        return os.path.join(self.work_dir, self.tmp_dir_name, self.dist)
    tmp_dir = property(get_tmp_dir)


    def get_file_lists(self):
        """Get a dictionary of LazyWriters keyed by purpose.

        Key format is ('list' or 'override', section, arch)
        """
        lists = {}
        for file_type in ('list', 'overrides'):
            for arch in self.arches:
                for section in self.sections:
                    key = (file_type, section, arch)
                    file_name = '-'.join([file_type, section, arch])
                    full_name = self.tmp_dir[file_name]
                    lists[key] = LazyWriter(full_name)
        return lists


    def get_file_list(self, arch, section):
        """Return a single file list for an architecture and section."""
        return self.file_lists[('list', section, arch)]

    def get_overrides_file(self, arch, section):
        """Return a single overrides file for an architecture and
        section."""
        return self.file_lists[('overrides', section, arch)]


    def write_to_lists(self, injector):
        """Record this package in the appropriate file lists."""
        for arch in injector.get_architectures(self.arches):
            handle = self.file_lists[('list', injector.section, arch)]
            print >> handle, injector.get_pool_location()


    def flush_lists(self):
        """Flush all file handles associated with this object.

        Probably only useful for unit testing."""
        for handle in self.file_lists.values():
            if handle.is_started():
                handle.flush()


    def get_one_dir(self, section, arch):
        """Return the index directory path for a given section and
        architecture."""
        base = pjoin(self.repo_dir, self.dist)
        if arch == 'source':
            arch_dir = 'source'
        else:
            arch_dir = 'binary-%s' % arch
        return pjoin(base, section, arch_dir)


    def get_all_dirs(self):
        """Calculate and return a list of all the package index
        directories supported by this package."""
        all_dirs = Set()
        for arch in self.arches:
            for section in self.sections:
                all_dirs.add(self.get_one_dir(section, arch))
        return all_dirs


    def make_all_dirs(self):
        """Make all directories needed for apt-ftparchive.

        This only applies to directories which are not otherwise created
        while writing filelists, etc.
        """
        for needed_dir in self.get_all_dirs():
            os.makedirs(needed_dir)


    def invoke_archiver(self):
        """Actually invoke apt-ftparchive."""
        bin = 'apt-ftparchive'
        config = self.tmp_dir.config
        status = os.system('%s -q generate %s' % (bin, config))
        if status:
            print status
            raise StandardError, (
                'archiver (%s) returned %d' % (bin, status)
            )


    def write_repo(self):
        """After all injectors have been added properly, create
        the repo."""
        self.flush_lists()
        self.invoke_archiver()


    def write_releases(self, writer):
        """Write all Release files for the repository."""
        for section in self.sections:
            for arch in self.arches:
                release_path = pjoin(
                    self.get_one_dir(section, arch)
                    , 'Release'
                    )
                handle = LazyWriter(release_path)
                writer.write(handle, section, arch)
        release_path = pjoin(self.repo_dir, self.dist, 'Release')
        writer.write_outer(LazyWriter(release_path))


class DebianDirectPoolRepo(DebianPoolRepo):
    """Create a full repository from a Debian pool.  Use injectors
    both to create the pool on the fly and to write the indexes."""

    def _iter_file_list_keys(self):
        '''Yield a series of keys suitable for use as file_list keys.

        See get_file_lists.
        '''
        for arch in self.arches:
            for section in self.sections:
                if arch == "source":
                    yield (section, None, arch)
                else:
                    for subsection in (None, 'debian-installer'):
                        yield (section, subsection, arch)

    def get_file_lists(self):
        """Get a dictionary of LazyWriters keyed by section and arch.

        Key format is (section, subsection, arch)

        Subsection should be None or 'debian-installer'.
        """
        lists = {}
        for key in self._iter_file_list_keys():
            section, subsection, arch = key
            if arch == "source":
                file_name = "%s/%s/source/Sources" \
                            % (self.dist, section)
            else:
                if subsection:
                    file_name = "%s/%s/%s/binary-%s/Packages" \
                                % (self.dist, section, subsection, arch)
                else:
                    file_name = "%s/%s/binary-%s/Packages" \
                                % (self.dist, section, arch)
            full_name = pjoin(self.repo_dir, file_name)
            lists[key] = LazyWriter(full_name)
        return lists


    def get_file_list(self, arch, section):
        """Return the package indexes for a single section and
        architecture."""
        return self.file_lists[(section, arch)]


    def get_overrides_file(self, arch, section):
        """In the parent class, this gets the overrides.  Since we
        don't use apt-ftparchive, flag any use of this function."""
        raise RuntimeError, "get_overrides_file() doesn't work here"


    def write_to_lists(self, injector):
        """Record this package in the appropriate file lists."""
        for arch in injector.get_architectures(self.arches):
            subsection = injector.get_subsection()
            handle = self.file_lists[(injector.section, subsection, arch)]
            handle.write("".join(injector.get_apt_header()))


    def write_repo(self):
        """Write the repository index files."""
        self.flush_lists()
        for file_list in self.file_lists.values():
            if file_list.is_started():
                os.system("gzip -n < %s > %s.gz"
                          % (file_list.name, file_list.name))


class DebianReleaseWriter(object):
    """This class writes Release files for a whole repository,
    including the toplevel Release file and the per-component files.
    """

    def __init__(self, contents, raw_arches, raw_sections, search_path):
        self.archive = contents['apt-deb', 'archive']
        self.version = contents['apt-deb', 'version']
        self.origin = contents['apt-deb', 'origin']
        self.label = contents['apt-deb', 'label']
        self.suite = contents['apt-deb', 'suite']
        self.codename = contents['apt-deb', 'codename']
        self.release_time = contents['apt-deb', 'date']
        self.description = contents['apt-deb', 'description']
        self.search_path = str(search_path)

        self.arches = list(raw_arches)
        self.arches.sort()

        debian_order = ['main', 'contrib', 'non-free']
        if Set(debian_order) >= Set(raw_sections):
            sort_table = dict(zip(debian_order, range(len(debian_order))))
            def _sec_cmp(a, b):
                """Sort compare function using a special table."""
                return cmp(sort_table[a], sort_table[b])
        else:
            _sec_cmp = cmp
        self.sections = list(raw_sections)
        self.sections.sort(_sec_cmp)


    def write(self, handle, section, arch):
        """Write a component-level Release file."""
        data = [ ('Archive', self.archive),
                 ('Version', self.version),
                 ('Component', section),
                 ('Origin', self.origin),
                 ('Label', self.label),
                 ('Architecture', arch) ]

        for label, value in data:
            print >> handle, "%s: %s" % (label, value)
        handle.flush()


    def write_outer(self, handle):
        """Write the toplevel Release file."""
        apt_handle = os.popen('apt-ftparchive release %s | grep -v ^Date'
                              % str(self.search_path))
        sums = apt_handle.read()
        status = apt_handle.close()

        if status:
            print status
            raise SemanticError, 'archiver returned %d' % status

        print >> handle, 'Origin: %s' % self.origin
        print >> handle, 'Label: %s' % self.label
        print >> handle, 'Suite: %s' % self.suite
        print >> handle, 'Version: %s' % self.version
        print >> handle, 'Codename: %s' % self.codename
        print >> handle, 'Date: %s' % self.release_time
        print >> handle, 'Architectures: %s' % ' '.join(self.arches)
        print >> handle, 'Components: %s' % ' '.join(self.sections)
        print >> handle, 'Description: %s' % self.description
        handle.write(sums)


def get_apt_component_name(ref):
    """Extract an apt-component name from a component reference"""
    return os.path.basename(ref[:-4])

class Compiler:
    """This class acts as a generic wrapper to all the little tasks
    needed to create a repository from a product.
    """

    def __init__(self, cache):
        self.cache = cache


    def deb_scan_arches(self, packages):
        """Return arches for a list of debian packages."""
        arches = Set()
        for package in packages:
            if package.role == 'source':
                arches.add('source')
            else:
                if package.arch != 'all':
                    arches.add(package.arch)
        return arches


    def create_debian_pool_repo(self, product, provided_contents,
                                repo_dir):
        """Do the work of creating a pool repo given packages."""

        # some sane defaults for contents
        default_date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        default_apt_suite_name = get_apt_component_name(product.ref)
        contents = { ('apt-deb', 'suite'): default_apt_suite_name,
                     ('apt-deb', 'version'): '0',
                     ('apt-deb', 'origin'):default_apt_suite_name,
                     ('apt-deb', 'label'): default_apt_suite_name,
                     ('apt-deb', 'codename'): default_apt_suite_name,
                     ('apt-deb', 'date'): default_date,
                     ('apt-deb', 'description'): default_apt_suite_name,
                     ('apt-deb', 'split-apt-components'): ''}
        contents.update(provided_contents)

        suite = contents['apt-deb', 'suite']
        if contents['apt-deb', 'split-apt-components']:
            # an apt splittable component should not directly reference
            # packages
            if list(product.iter_direct_packages()):
                raise InputError, 'No direct package references ' + \
                      'allowed with split-components is in effect'
            packages_dict = {}
            # sort packages belonging to various apt_components in a dict
            # keyed by apt component name
            for apt_component in product.iter_direct_components():
                apt_name = get_apt_component_name(apt_component.ref)
                component_packages = list(apt_component.iter_packages())
                packages_dict[apt_name] = component_packages
        else:
            # default behavior: dists/$compname/main .
            # see default suite value in contents above.
            packages_dict = { 'main': list(product.iter_packages()) }


        sections = packages_dict.keys()
        all_packages = Set(chain(*packages_dict.values()))
        arches = self.deb_scan_arches(all_packages)
        # Set True to use apt-ftparchive, False to use the direct version.
        cwd = os.getcwd()
        suitepath = pjoin('dists', suite)
        if False:
            repo = DebianPoolRepo(cwd, suitepath, arches, sections,
                                  repo_dir)
        else:
            repo = DebianDirectPoolRepo(cwd, suitepath, arches, sections,
                                        repo_dir)

        search_path = pjoin(repo.repo_dir, repo.dist)
        contents['apt-deb', 'archive'] = suite
        writer = DebianReleaseWriter(contents, arches, sections,
                                     search_path)
        repo.make_all_dirs()
        for section, packages in packages_dict.items():
            for package in packages:
                injector = DebianPoolInjector(self.cache, package, section,
                                              repo.repo_dir)
                repo.write_to_lists(injector)
                injector.link_to_cache()
        repo.write_repo()
        repo.write_releases(writer)

    def create_raw_package_dump_repo(self, component, dummy, repo_dir):
        """Link all the packages in the product to the repository."""
        os.mkdir(repo_dir)
        for package in component.iter_packages():
            link_dest = os.path.join(repo_dir, package.filename)
            if not os.path.exists(link_dest):
                os.link(self.cache.file_path(package.blob_id), link_dest)

    def dump_report(self, component, contents, dummy):
        """Instead of building a repo, dump a report of component contents.
        """
        if ('pdk', 'format') not in contents:
            raise InputError, 'Component descriptor missing format element'

        format = contents['pdk', 'format']
        lines = []
        for package in component.iter_packages():
            cache_location = self.cache.file_path(package.blob_id)
            overlaid_package = overlay_getitem(package, cache_location, '')
            lines.append(format % overlaid_package)
        lines.sort()
        for line in lines:
            print line
        print

class overlay_getitem(object):
    """A dict like delegator that returns a default for missing keys.

    Also converts None to the the default value.

    Also adds a cache_location value

    fd['missing'] -> ''
    """
    def __init__(self, target, cache_location, default):
        self.target = target
        self.cache_location = cache_location
        self.default = default

    def default_wrap(self, value):
        '''If value is None return self.default, otherwise, return value.
        '''
        if value is None:
            return self.default
        else:
            return value

    def __getitem__(self, raw_key):
        domain, predicate = parse_domain(raw_key)
        key = (domain, predicate)
        if predicate in ('cache-location', 'cache_location'):
            return self.cache_location

        try:
            if domain == 'version':
                return self.default_wrap(getattr(self.target.version,
                                                 predicate))

            return self.default_wrap(self.target[key])
        except KeyError:
            return self.default

# vim:set ai et sw=4 ts=4 tw=75:
