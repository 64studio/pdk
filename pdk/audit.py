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
audit

Load the component(s), and verify that all of its parts exist in the
cache Part of the PDK suite
"""
__revision__ = '$Progeny$'

from sets import Set
import sha
import md5
import pdk.workspace as workspace
from pdk.component import ComponentDescriptor
from pdk.command_base import make_invokable
import pdk.log as log
from pdk.exceptions import IntegrityFault
audit_logger = log.get_logger()


def audit(args):
    """\\fB%prog\\fP
.PP
Load the component,
and verify that it and it's parts are well-formed.
    """
    ##specialization code starts here

    def note_problem(fact, prediction, prediction_basis,
                     evidence, evidence_basis):
        """A mismatch handler for Arbiter

        Handle the case of a prediction that doesn't pan out
        by reporting the mismatch to stdout, in a format
        suitable for: cut -d'|'
        """
        note_problem.called = True
        fields = fact.get_problem_description(prediction, prediction_basis,
                                         evidence, evidence_basis)
        result = string_together(fields, '|')
        print result

    note_problem.called = False

    my_cache = workspace.current_workspace().cache
    arbiter = Arbiter(note_problem)

    for component_name in args.args:
        def _note_blob_id(blob_id):
            """Make common predictions and warrants for blob_id.

            Predict that a blob_id will be in cache
            Warrant the blob_id will be needed by the component.
            """
            arbiter.predict(InCache(blob_id), True, component_name)

        # Get the set of packages in the component
        descriptor = ComponentDescriptor(component_name)
        component = descriptor.load(my_cache)

        # predict expected blob_ids and headers
        for package in component.iter_packages():
            _note_blob_id(package.blob_id)
            arbiter.predict(InCache(package.blob_id + '.header'),
                            True, component_name)
            for package_tuple in package.extra_files:
                blob_id = package_tuple[0]
                _note_blob_id(blob_id)

        # predict upcoming source packages
        for package in component.iter_packages():
            if package.role == 'binary':
                fact = HasSource(package.format, package.pdk.sp_name,
                                 package.pdk.sp_version.full_version)
                arbiter.predict(fact, True, component_name)

        # warrant source packages found
        for package in component.iter_packages():
            if package.role == 'source':
                fact = HasSource(package.format, package.name,
                                 package.version.full_version)
                arbiter.warrant(fact, True, component_name)

    # predict upcoming cache checksums
    # pre-warrant found inodes
    # note inode -> filename relationships for later
    found_by_inode = {}
    for blob_id in my_cache:
        inode = my_cache.get_inode(blob_id)
        if blob_id.endswith('.header'):
            arbiter.warrant(InCache(blob_id), True, 'cache')
            continue

        entry = found_by_inode.setdefault(inode, Set([]))
        entry.add(blob_id)

        # ? Won't this create repeated predictions?
        for blob_id in found_by_inode[inode]:
            arbiter.predict(ChecksumMatches(blob_id), blob_id, 'cache')

    for inode, blob_ids in found_by_inode.iteritems():
        for blob_id in blob_ids:
            arbiter.warrant(InCache(blob_id), True, 'cache')

        # warrant cache checksums
        one_id = tuple(blob_ids)[0]
        handle = open(my_cache.file_path(one_id))
        sha1_digest = sha.new()
        md5_digest = md5.new()
        read_size = 8196
        while 1:
            block = handle.read(read_size)
            if not block:
                break
            sha1_digest.update(block)
            md5_digest.update(block)
        handle.close()

        prefixes = []
        for blob_id in blob_ids:
            if blob_id.startswith('sha-1'):
                prefixes.append('sha-1')
                arbiter.warrant(ChecksumMatches(blob_id),
                                'sha-1:' + sha1_digest.hexdigest(),
                                'cache')
            elif blob_id.startswith('md5'):
                prefixes.append('md5')
                arbiter.warrant(ChecksumMatches(blob_id),
                                'md5:' + md5_digest.hexdigest(), 'cache')
            else:
                # note unknown prefixes
                arbiter.note_problem(
                    blob_id
                    , ('md5:', 'sha-1:')
                    , 'unknown prefix'
                    )
        prefixes.sort()
        if prefixes != ['md5', 'sha-1']:
            digests = (md5_digest.hexdigest(), sha1_digest.hexdigest())
            arbiter.note_problem(tuple(blob_ids), digests,
                                 'not hard linked properly')

    arbiter.note_leftovers()

    if note_problem.called:
        raise IntegrityFault, "Audit detected fault(s)"

audit = make_invokable(audit)

def string_together(fields, separator):
    """Stringify fields and join them with separator.

    if not bool(field): stringified field becomes ''.
    """
    string_fields = [ f and str(f) or '' for f in fields ]
    joined_string = separator.join(string_fields)
    return joined_string

class Arbiter(object):
    """Match predictions with warrants.

    Predictions do not neccessarily have to precede warrants.

    Warranted facts which are never predicted are ignored.

    mismatch_handler is called as possible when a mismatch is found.

    Call note_leftovers after adding all predictions and warrants to
    mop up any dangling predictions.

    Call note_problem to note problems which do not require a
    prediction/warrant pair.
    """
    __slots__ = ('prediction_index', 'warrant_index', 'mismatch_handler')

    def __init__(self, mismatch_handler):
        self.mismatch_handler = mismatch_handler
        self.prediction_index = {}
        self.warrant_index = {}

    def predict(self, fact, prediction, prediction_basis):
        """Predict that evidence will assert a fact."""
        if fact in self.warrant_index:
            evidence, warrant_basis = self.warrant_index.pop(fact)
            if prediction != evidence:
                self.mismatch_handler(fact, prediction, prediction_basis,
                                 evidence, warrant_basis)
        else:
            self.prediction_index[fact] = (prediction, prediction_basis)

    def warrant(self, fact, evidence, warrant_basis):
        """Warrant that evidence has been found to establish a fact."""
        if fact in self.prediction_index:
            prediction, prediction_basis = self.prediction_index.pop(fact)
            if prediction != evidence:
                self.mismatch_handler(fact, prediction, prediction_basis,
                                 evidence, warrant_basis)
        else:
            self.warrant_index[fact] = (evidence, warrant_basis)

    def note_leftovers(self):
        """Note any dangling predictions."""
        for fact in dict(self.prediction_index):
            self.warrant(fact, None, 'no warrant')

    def note_problem(self, subject, prediction, message):
        """Directly note a problem; No prediction/warrant pair is needed.
        """
        fact = AlwaysFail(message)

        self.mismatch_handler(fact, prediction, None, None, subject)

class FactType(object):
    """Base class for fact types.

    Requires the use of a __slots__ field.

    Automatically makes derived types hashable, comparable, and iterable
    on the fields in their slot list.
    """
    # Our facts are made to work with the 'note_problem'
    def __init__(self, *args):
        arity = len(self.__slots__) + 1
        args_len = len(args) + 1
        if args_len != arity:
            raise TypeError, '__init__() takes %d arguments %d given.' \
                  % (arity, args_len)
        for name, arg in zip(self.__slots__, args):
            setattr(self, name, arg)

    def __iter__(self):
        return iter([ getattr(self, x) for x in self.__slots__ ])

    def __cmp__(self, other):
        return cmp(type(self), type(other)) or cmp(list(self), list(other))

    def __hash__(self):
        return hash((type(self), tuple(self)))

class InCache(FactType):
    """The blob_id is expected to be in the cache."""
    __slots__ = 'blob_id',
    blob_id = None

    def get_problem_description(self, *args):
        """Return data suitable for Arbiter.mismatch_handler."""
        #prediction, prediction_basis, evidence, evidence_basis
        prediction_basis = args[1]
        return (self.blob_id, prediction_basis, 'missing from cache')

class InodeNeeded(FactType):
    """The inode is needed by some component."""
    __slots__ = 'inode',
    inode = None

    def get_problem_description(self, *args):
        """Return data suitable for Arbiter.mismatch_handler."""
        #prediction, prediction_basis, evidence, evidence_basis
        prediction_basis = args[1]
        return (prediction_basis, '', 'not needed by components')

class HasSource(FactType):
    """The given fields represent a source package in a component."""
    __slots__ = 'format', 'name', 'version'
    format = None
    name = None
    version = None

    def get_problem_description(self, *dummy):
        """Return data suitable for Arbiter.mismatch_handler."""
        subject = string_together([self.format, self.name, self.version],
                                  ',')
        return (subject, '', 'missing source')

class ChecksumMatches(FactType):
    """The the contents of the blob_id match it's checksum."""
    __slots__ = 'blob_id',
    blob_id = None

    def get_problem_description(self, *args):
        """Return data suitable for Arbiter.mismatch_handler."""
        # args= prediction, dummy, evidence, ...
        prediction, evidence = args[0], args[2]
        return (prediction, evidence, 'checksum mismatch')

class AlwaysFail(FactType):
    """Fail directly. Used by Arbiter.note_problem."""
    __slots__ = 'message',
    message = None

    def get_problem_description(self, *args):
        """Return data suitable for Arbiter.mismatch_handler."""
        prediction, evidence_basis = args[0], args[3]
        return (evidence_basis, prediction, self.message)

# vim:set ai et sw=4 ts=4 tw=75:
