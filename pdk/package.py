# $Progeny$
#
#   Copyright 2005, 2006 Progeny Linux Systems, Inc.
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
package.py


Houses functionality for representing deb and rpm source and binary
packages.
"""

import re
from pdk.exceptions import InputError
from pdk.meta import Entity

# Obviously at least one of these two needs to work for PDK to be useful.
try:
    # for working with deb packages
    import apt_inst
    import apt_pkg
    import smart.backends.deb.debver as debver
except ImportError:
    pass

try:
    # for working with rpm packages
    import rpm as rpm_api
except ImportError:
    pass


__revision__ = "$Progeny$"

class DomainAttributeAdapter(object):
    '''Expose a domain of an entity as attributes of this object.

    domain - The domain to expose.
    entity - Resolve attributes against this particular entity.
    '''
    def __init__(self, domain, entity):
        self.domain = domain
        self.entity = entity

    def find_key(self, key):
        """Be forgiving about key lookups. s/_/-/g"""
        candidate = (self.domain, key)
        if candidate in self.entity:
            return candidate
        dashed_key = str(key).replace('_', '-')
        dashed_candidate = (self.domain, dashed_key)
        if dashed_candidate in self.entity:
            return dashed_candidate
        message = key + ' (%r, Domain: %s)' % (dict(self.entity),
                                               self.domain)
        raise AttributeError, message

    def __getattr__(self, attr):
        key = self.find_key(attr)
        return self.entity[key]

class Package(Entity):
    """Represents a logical package.

    Fields may be accessed as attributes or items, and dashes are
    converted to underscores as needed.
    """
    def __init__(self, package_type, blob_id):
        super(Package, self).__init__(package_type.type_string, blob_id)
        self.package_type = package_type
        self.pdk = DomainAttributeAdapter('pdk', self)
        self.complement = []

    def set_blob_id(self, blob_id):
        """Set the blob_id and update the internal hash."""
        self.ent_id = blob_id

    def get_blob_id(self):
        """Get the blob_id"""
        return self.ent_id
    blob_id = property(get_blob_id, set_blob_id)

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        elif key[0] == 'pdk' and hasattr(self, key[1]):
            return getattr(self, key[1])
        else:
            raise KeyError, key

    def get_arch(self):
        '''Find the relevant arch '''
        try:
            return self[(self.format, 'arch')]
        except KeyError:
            raise AttributeError, 'arch'
    arch = property(get_arch)

    def get_filename(self):
        """Defer filename calculation to the package type object."""
        if ('pdk', 'filename') in self:
            return self[('pdk', 'filename')]
        else:
            return self.package_type.get_filename(self)
    filename = property(get_filename)

    def get_type(self):
        """Defer the type string to the package type object."""
        return self.package_type.type_string
    type = property(get_type)

    def get_format(self):
        """Defer the format string to the package type object."""
        if ('pdk', 'format') in self:
            return self[('pdk', 'format')]
        else:
            return self.package_type.format_string
    format = property(get_format)

    def get_role(self):
        """Defer the role string to the package type object."""
        return self.package_type.role_string
    role = property(get_role)

    def get_name(self):
        '''Convenience method for accessing the package name.'''
        return self.pdk.name
    name = property(get_name)

    def get_version(self):
        '''Convenience method for accessing the package version object.'''
        return self.pdk.version
    version = property(get_version)

    def get_extra_files(self):
        '''Return extra file tuples or just an empty list.'''
        return self.get(('pdk', 'extra-file'), [])
    extra_files = property(get_extra_files)

    def get_size(self):
        '''Get the expected size of the package.

        WARNING: not always present. No attempt has been made to
        shield the caller from key errors, which may masquerade as
        puzzling AtttributeErrors.
        '''
        return int(self[('pdk', 'size')])
    size = property(get_size)

    def _get_values(self):
        '''Return an immutable value representing the full identity.'''
        field_list = ('format', 'role', 'name', 'version', 'arch',
                      'blob_id')
        contents = [ getattr(self, f) for f in field_list
                     if hasattr(self, f) ]
        return tuple(['package'] + contents)

    def __str__(self):
        try:
            return '<Package %r>' % ((self[('pdk', 'name')],
                                      self[('pdk', 'version')],
                                      self.arch, self.type,),)
        except AttributeError, message:
            return '<Package incomplete "%s">' % message
    __repr__ = __str__

    def __cmp__(self, other):
        return cmp(self._get_values(), other._get_values())

    def __eq__(self, other):
        return self.ent_type == other.ent_type \
               and self.ent_id == other.ent_id

# evil hack so that getattr and hasattr will work for blob DASH id
setattr(Package, 'blob-id', property(lambda self: self.blob_id))

def split_deb_version(raw_version):
    """Break a debian version string into it's component parts."""
    return re.match(debver.VERRE, raw_version).groups()

class DebianVersion(object):
    """A comparable Debian package version number."""
    __slots__ = ('version_string', 'epoch', 'version', 'release',
                 'string_without_epoch', 'full_version')
    def __init__(self, version_string):
        self.version_string = version_string
        self.epoch, self.version, self.release = \
            split_deb_version(version_string)
        self.string_without_epoch = \
            synthesize_version_string(None, self.version, self.release)
        self.full_version = \
            synthesize_version_string(self.epoch, self.version,
                                      self.release)
    def __cmp__(self, other):
        if isinstance(other, basestring):
            other = DebianVersion(other)
        from smart.backends.deb.debver import vercmp as smart_vercmp
        return cmp(self.__class__, other.__class__) or \
               smart_vercmp(self.version_string, other.version_string)

    def __repr__(self):
        return '<dver %r>' % self.full_version

    def __str__(self):
        return self.full_version

    def __hash__(self):
        return hash((self.version, self.release))

def sanitize_deb_header(header):
    """Normalize the whitespace around the deb header/control contents."""
    return header.strip() + '\n'

class _Dsc(object):
    """Handle debian source packages (dsc file + friends)."""
    type_string = 'dsc'
    format_string = 'deb'
    role_string = 'source'
    version_class = DebianVersion

    def parse(self, control, blob_id):
        """Parse control file contents. Returns a package object."""
        tags = apt_pkg.ParseSection(control)
        return self.parse_tags(tags, blob_id)

    def parse_tags(self, apt_tags, blob_id):
        '''Parse an apt tags section object directly.

        Returns a package object.
        '''
        tags = apt_tags
        fields = []
        for tag, l_tag in [ (t, t.lower()) for t in apt_tags.keys() ]:
            if l_tag in ('source', 'package'):
                # be tolerant of both dsc's and apt source stanzas.
                dom, key, value = 'pdk', 'name', tags[tag]
            elif l_tag == 'files':
                raw_file_list = tags['Files']
                extra_files = []
                for line in raw_file_list.strip().splitlines():
                    (md5sum, size, name) = line.strip().split()
                    extra_files.append(('md5:' + md5sum, size, name))
                extra_files = tuple(extra_files)
                dom, key, value = 'pdk', 'extra-file', extra_files
            elif l_tag == 'version':
                dom, key, value = 'pdk', 'version', \
                    DebianVersion(tags[tag])
            elif l_tag == 'architecture':
                dom, key, value = 'deb', 'arch', tags[tag]
            elif l_tag == 'directory':
                dom, key, value = 'deb', 'directory', tags[tag]
            else:
                dom, key, value = 'deb', tag, tags[tag]
            fields.append((dom, key, value))

        for raw_blob_id, size, filename in extra_files:
            if filename.endswith('.dsc'):
                fields.append(('pdk', 'raw-filename', filename))
                fields.append(('pdk', 'size', size))
                found_blob_id = raw_blob_id
                break

        if not blob_id and found_blob_id:
            blob_id = found_blob_id

        package = Package(self, blob_id)
        for dom, key, value in fields:
            package[(dom, key)] = value
        return package

    def extract_signed_content(self, raw):
        '''Yank the signed content out of a pgp signed plaintext.

        No verfication of the signature is done.
        '''
        if re.search(r'(?m)^=', raw):
            lines = iter(raw.splitlines(True))
            for line in lines:
                if re.match('^-', line):
                    break

            for line in lines:
                if line.strip() == '':
                    break

            header_lines = []
            for line in lines:
                if line.strip() == '':
                    break
                header_lines.append(line)

            return ''.join(header_lines)
        else:
            return raw

    def extract_header(self, filename):
        """Extract control file contents from a dsc file."""
        handle  = open(filename)
        full_text = handle.read()
        handle.close()
        header = self.extract_signed_content(full_text)
        return sanitize_deb_header(header)

    def get_filename(self, package):
        """Return a dsc filename for use in an apt repo."""
        version_string = package.pdk.version.string_without_epoch
        return '%s_%s.dsc' % (package.pdk.name, version_string)

dsc = _Dsc()

class _Deb(object):
    """Handle deb packages. (binary)"""
    type_string = 'deb'
    format_string = 'deb'
    role_string = 'binary'
    version_class = DebianVersion

    def parse(self, control, blob_id):
        """Parse control file contents. Returns a package object."""
        tags = apt_pkg.ParseSection(control)
        return self.parse_tags(tags, blob_id)

    def parse_tags(self, apt_tags, blob_id):
        '''Parse an apt tags section object directly.

        Returns a package object.
        '''
        tags = apt_tags

        sp_name, sp_version = None, None

        fields = []
        for tag, l_tag in [ (t, t.lower()) for t in tags.keys() ]:
            if l_tag == 'package':
                name = tags[tag]
                dom, key, value = 'pdk', 'name', name
            elif l_tag == 'source':
                sp_name = tags[tag]
                if re.search(r'\(', sp_name):
                    match = re.match(r'(\S+)\s*\((.*)\)', sp_name)
                    (sp_name, sp_raw_version) = match.groups()
                    sp_version = DebianVersion(sp_raw_version)
            elif l_tag == 'version':
                version = DebianVersion(tags[tag])
                dom, key, value = 'pdk', 'version', version
            elif l_tag == 'architecture':
                dom, key, value = 'deb', 'arch', tags[tag]
            elif l_tag == 'md5sum':
                found_blob_id = 'md5:' + tags[tag]
            elif l_tag == 'filename':
                dom, key, value = 'pdk', 'raw-filename', tags[tag]
            elif l_tag == 'size':
                dom, key, value = 'pdk', 'size', tags[tag]
            else:
                dom, key, value = 'deb', tag, tags[tag]
            fields.append((dom, key, value))

        if not sp_name:
            sp_name = name

        if not sp_version:
            sp_version = version

        fields.append(('pdk', 'sp-name', sp_name))
        fields.append(('pdk', 'sp-version', sp_version))

        if not blob_id and found_blob_id:
            blob_id = found_blob_id

        package = Package(self, blob_id)
        for dom, key, value in fields:
            package[(dom, key)] = value
        return package

    def extract_header(self, filename):
        """Extract control file contents from a deb package."""
        handle = open(filename)
        control = apt_inst.debExtractControl(handle)
        handle.close()
        return sanitize_deb_header(control)

    def get_filename(self, package):
        """Return a deb filename for use in an apt repo."""
        version_string = package.pdk.version.string_without_epoch
        return '%s_%s_%s.deb' % (package.pdk.name, version_string,
                                    package.arch)

deb = _Deb()

class _UDeb(_Deb):
    '''Handle udeb packages. (special binary)'''
    type_string = 'udeb'
    format_string = 'deb'
    role_string = 'binary'

    def get_filename(self, package):
        """Return a udeb filename for use in an apt repo."""
        version_string = package.pdk.version.string_without_epoch
        return '%s_%s_%s.udeb' % (package.pdk.name, version_string,
                                  package.arch)

udeb = _UDeb()

def get_rpm_header(handle):
    """Extract an rpm header from an rpm package file."""
    ts = rpm_api.TransactionSet('/', rpm_api._RPMVSF_NODIGESTS
                            | rpm_api._RPMVSF_NOSIGNATURES)
    header = ts.hdrFromFdno(handle.fileno())
    handle.close()
    return header

def parse_rpm_header(raw_header, blob_id = None, package_type = None):
    '''Parse the header and return and rpm or srpm package object.

    This method works on every type of rpm header representation known
    to pdk, including a real rpm api header object, a dict (channel data),
    and the xml representation in rpm-md repositories.

    Parsing from a dict or rpm header requires that you set the blob_id and
    package_type parameters.
    '''

    if isinstance(raw_header, dict):
        assert blob_id is not None
        assert package_type is not None
        package = Package(package_type, blob_id)
        package.update(raw_header)
        return package

    elif hasattr(raw_header, 'attrib'): # elementtree element
        package_element = raw_header
        common_prefix = 'http://linux.duke.edu/metadata/common'
        rpm_prefix = 'http://linux.duke.edu/metadata/rpm'
        prefii = { 'common': common_prefix, 'rpm': rpm_prefix }
        srpm_path = '{%(common)s}format/{%(rpm)s}sourcerpm' % prefii
        def get_element(tag):
            '''Try to find an element

            Uses the common namespace only if the namespace is
            unspecified.

            Raises KeyError if the element is not found.
            '''
            if tag.startswith('{'):
                namespaced_tag = tag
                sub_element = package_element.find(tag)
            else:

                namespaced_tag = '{%s}%s' % (common_prefix, tag)
                sub_element = package_element.find(namespaced_tag)

            if sub_element is None:
                raise KeyError, namespaced_tag

            return sub_element

        def get_atts(tag):
            '''Gets the attributes associcated with the named tag.

            Inherits the namespace handling from get_element.
            '''
            sub_element = get_element(tag)
            return sub_element.attrib

        def get_text(tag):
            '''Gets the text associcated with the named tag.

            Inherits the namespace handling from get_element.
            '''
            sub_element = get_element(tag)
            return sub_element.text

        pdk_dict = {}
        pdk_dict['pdk', 'name'] = get_text('name')
        version_info = get_atts('version')
        pdk_dict['rpm', 'arch'] = get_text('arch')

        source_rpm_element = package_element.find(srpm_path)
        if source_rpm_element is None:
            raise KeyError, srpm_path
        source_rpm = source_rpm_element.text
        if not source_rpm:
            package_type = srpm
            source_rpm = None
        else:
            package_type = rpm
        pdk_dict['pdk', 'source-rpm'] = source_rpm

        version_string = '%(epoch)s-%(ver)s-%(rel)s' % version_info
        pdk_dict['pdk', 'version'] = \
            package_type.version_class(version_string = version_string)
        location = get_atts('location')['href']
        pdk_dict['pdk', 'nosrc'] = location.endswith('nosrc.rpm')
        size = get_atts('size')['archive']
        pdk_dict['pdk', 'size'] = size

        blob_prefix = get_atts('checksum')['type']
        if blob_prefix == 'sha':
            blob_prefix = 'sha-1'
        blob_body = get_text('checksum')
        blob_id = '%s:%s' % (blob_prefix, blob_body)
        package = Package(package_type, blob_id)
        package.update(pdk_dict)
        return package

    else: # rpm_api Header object
        assert blob_id is not None
        assert package_type is not None
        header = rpm_api.headerLoad(raw_header)
        source_rpm = header[rpm_api.RPMTAG_SOURCERPM]

        # work around rpm oddity
        if source_rpm == []:
            source_rpm = None

        package = Package(package_type, blob_id)

        package[('pdk', 'name')] = header[rpm_api.RPMTAG_NAME]
        package[('pdk', 'version')] = RPMVersion(header)
        package[('rpm', 'arch')] = header[rpm_api.RPMTAG_ARCH]
        package[('pdk', 'source-rpm')] = source_rpm

        # note the nosource and/or nopatch attributes
        keys = header.keys()
        nosrc = (1051 in keys or 1052 in keys)
        package['pdk', 'nosrc'] = nosrc

        return package


class RPMVersion(object):
    """A comparable RPM package version."""
    __slots__ = ('epoch', 'version', 'release', 'string_without_epoch',
                 'full_version', 'tuple')
    def __init__(self, header = None, version_string = None):
        if header:
            if header[rpm_api.RPMTAG_EPOCH]:
                self.epoch = str(header[rpm_api.RPMTAG_EPOCH])
            else:
                self.epoch = ''
            self.version = header[rpm_api.RPMTAG_VERSION]
            self.release = header[rpm_api.RPMTAG_RELEASE]
        else:
            parts = version_string.split('-')
            if len(parts) == 1:
                self.epoch = None
                self.version = parts[0]
                self.release = '0'
            elif len(parts) == 2:
                self.epoch = None
                self.version, self.release = parts
            elif len(parts) == 3:
                self.epoch, self.version, self.release = \
                    [ p or None for p in parts ]
            else:
                raise InputError('Invalid rpm version string: "%s"'
                                 % version_string)

        # Due to a "bug" in createrepo, we have to consider missing epochs
        # as equal to zero epochs. As far as I know this shouldn't hurt any
        # of our users. /me hopes. -dt
        self.tuple = (self.epoch or '0',  self.version, self.release)
        self.string_without_epoch = '-'.join([self.version, self.release])
        if self.epoch:
            self.full_version = '-'.join(self.tuple)
        else:
            self.full_version = self.string_without_epoch

    def __cmp__(self, other):
        if isinstance(other, basestring):
            other = RPMVersion(version_string = other)
        return cmp(self.__class__, other.__class__) or \
               rpm_api.labelCompare(self.tuple, other.tuple)

    def __repr__(self):
        return '<rver %r>' % self.full_version

    def __str__(self):
        return self.full_version

    def __hash__(self):
        return hash((self.version, self.release))

class _Rpm(object):
    """Handle binary rpm packages."""
    type_string = 'rpm'
    format_string = 'rpm'
    role_string = 'binary'
    version_class = RPMVersion

    def parse(self, raw_header, blob_id):
        """Parse an rpm header. Returns a package object."""
        return parse_rpm_header(raw_header, blob_id, self)

    def extract_header(self, filename):
        """Extract an rpm header from an rpm package file."""
        handle = open(filename)
        raw_header = get_rpm_header(handle).unload(1)
        return raw_header

    def get_filename(self, package):
        """Return a reasonable rpm package filename."""
        version_string = package.pdk.version.string_without_epoch
        return '%s-%s.%s.rpm' % (package.pdk.name, version_string,
                                 package.arch)

rpm = _Rpm()

class _SRpm(_Rpm):
    """Handle source rpm packages."""
    type_string = 'srpm'
    role_string = 'source'

    def get_filename(self, package):
        """Return a reasonable srpm package filename."""
        version_string = package.pdk.version.string_without_epoch
        if package.pdk.nosrc:
            src_part = 'nosrc'
        else:
            src_part = 'src'
        return '%s-%s.%s.rpm' % (package.pdk.name, version_string, \
                                 src_part)

srpm = _SRpm()

class _Bin(object):
    """Handle any binary package."""
    type_string = 'bin'
    format_string = 'unknown'
    role_string = 'binary'
    version_class = str

bin = _Bin

class _Src(object):
    """Handle any source package."""
    type_string = 'src'
    format_string = 'unknown'
    role_string = 'source'
    version_class = str

src = _Src

def get_package_type(filename = '', format = ''):
    """Return a packge type for a filename or package reference format."""
    if filename.endswith('.deb') or format == 'deb':
        return deb
    elif filename.endswith('.udeb') or format == 'udeb':
        return udeb
    elif filename.endswith('.dsc') or format == 'dsc':
        return dsc
    elif filename.endswith('.nosrc.rpm') or \
            filename.endswith('.src.rpm') or format == 'srpm':
        return srpm
    elif filename.endswith('.rpm') or format == 'rpm':
        return rpm
    elif format == 'bin':
        return bin
    elif format == 'src':
        return src
    else:
        raise UnknownPackageTypeError((filename, format))

class UnknownPackageTypeError(InputError):
    """Exception used when a package type cannot be determined."""
    pass

def synthesize_version_string(epoch, version, release):
    """Reassemble a debian version string from it's parts."""
    dpkg_version = ''
    if epoch:
        dpkg_version += epoch + ':'
    if version:
        dpkg_version += version
    if release:
        dpkg_version += '-' + release
    return dpkg_version

# vim:set ai et sw=4 ts=4 tw=75:
