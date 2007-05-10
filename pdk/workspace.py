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
workspace

Library interface to pdk workspace
"""
__revision__ = '$Progeny$'

import os
import sys
import stat
from urlparse import urlsplit
from itertools import chain
from pdk.version_control import VersionControl, CommitNotFound
from pdk.cache import Cache
from pdk.channels import OutsideWorldFactory, WorldData, \
     MassAcquirer
from pdk.exceptions import ConfigurationError, SemanticError, \
     CommandLineError, InputError
from pdk.util import pjoin, make_self_framer, cached_property, \
     relative_path, get_remote_file_as_string, make_ssh_framer, \
     make_fs_framer, get_remote_file, noop, string_domain
from pdk.semdiff import print_bar_separated, print_man, \
     iter_diffs, iter_diffs_meta, filter_predicate, filter_data
from pdk.component import ComponentDescriptor
from pdk.repogen import compile_product
from pdk.progress import ConsoleMassProgress, NullMassProgress, \
     SizeCallbackAdapter
from pdk.command_base import make_invokable

# current schema level for this pdk build
schema_target = 6

class NotAWorkspaceError(ConfigurationError):
    '''A workspace op was requested on or in a non workspace directory.'''
    pass

def find_workspace_base(directory=None):
    """Locate the directory above the current directory, containing
    the work, cache, and svn directories.

    Returns None if a workspace is not to be found in the current path.
    """
    if directory is None:
        directory = os.getcwd()

    directory = os.path.normpath(directory)

    while True:
        schema_number = find_schema_number(directory)
        if schema_number:
            return directory, schema_number
        else:
            # no markers found. try parent.
            directory, tail = os.path.split(directory)
            # If we run out of path, quit
            if not tail:
                break

    return None, None

def current_workspace(given_directory = None):
    """
    Locate the current workspace and return the workspace object.

    This works on the assumption/presumption that you are in a
    workspace currently.  It merely looks upward in the directory
    tree until it finds its' marker files/dirs, and then instances
    the Workspace object with that directory as its base.
    """
    if given_directory is None:
        given_directory = os.getcwd()

    directory, schema_number = find_workspace_base(given_directory)
    assert_schema_current(directory, schema_number)
    if not directory:
        raise NotAWorkspaceError("Not currently a workspace: '%s'"
                                 % given_directory)
    return _Workspace(directory)

def currently_in_a_workspace():
    """Determine if pwd is in a workspace"""
    directory, schema_number = find_workspace_base()
    assert_schema_current(directory, schema_number)
    return bool(schema_number)

def assert_schema_current(ws_directory, schema_number):
    """Assert that the workspace can be handled by this software."""
    if schema_number and schema_number != schema_target:
        message = "Workspace migration is required.\n" + \
                  "cd %s; pdk migrate" % os.path.abspath(ws_directory)
        raise ConfigurationError(message)

def find_schema_number(directory):
    """Try to find a schema number for the given directory.

    Returns None on failure.
    """
    schema_path = pjoin(directory, 'etc', 'schema')
    if os.path.exists(schema_path):
        schema_number = int(open(schema_path).read())
        return schema_number

    cache_dir = pjoin(directory, 'cache')
    work_dir = pjoin(directory, 'work')
    if os.path.isdir(cache_dir) and os.path.isdir(work_dir):
        return 1

    return None

def write_migration_notes(filename, notes):
    '''Write migration notes to the given filename.

    Append some boilerplate helpful info the end of the notes.
    '''
    handle = open(filename, 'a')
    print >> handle, notes
    print >> handle
    trailer = """
This information has been saved to: %s
You can safely delete the file after reviewing it.
""" % filename
    print >> handle, trailer,
    handle.close()
    handle = open(filename)
    print handle.read(),
    handle.close()

def migrate(dummy):
    """\\fB%prog\\fP
.PP
Migrate the current workspace
to a form supported
by this software.
.PP
Only use this command
from the base of the workspace.
    """
    while 1:
        directory, schema_number = find_workspace_base()
        if schema_number > schema_target:
            message = 'Cannot migrate. Workspace schema newer than pdk'
            raise ConfigurationError(message)

        if directory != os.getcwd():
            message = \
                'Cannot migrate. Change directory to workspace base.\n' \
                'cd %s; pdk migrate' % directory
            raise ConfigurationError(message)

        if schema_number == 1:
            os.makedirs('etc')
            os.rename(pjoin('work','.git'), pjoin('etc', 'git'))
            for item in os.listdir('work'):
                os.rename(pjoin('work', item), item)
            os.rmdir('work')
            os.rename('cache', pjoin('etc', 'cache'))
            os.rename('channels.xml', pjoin('etc', 'channels.xml'))
            if os.path.exists('sources'):
                os.remove('sources')
            os.symlink(pjoin('etc', 'git'), '.git')
            os.symlink(pjoin('git', 'remotes'), pjoin('etc', 'sources'))
            open(pjoin('etc', 'schema'), 'w').write('2\n')
            continue

        if schema_number == 2:
            os.makedirs(pjoin('etc', 'channels'))
            channels_pickle = pjoin('etc', 'outside_world.cache')
            if os.path.exists(channels_pickle):
                os.remove(channels_pickle)
            open(pjoin('etc', 'schema'), 'w').write('3\n')
            continue

        if schema_number == 3:
            sources_dir = pjoin('etc', 'sources')
            if os.path.exists(sources_dir):
                os.remove(sources_dir)
            open(pjoin('etc', 'schema'), 'w').write('4\n')
            continue

        if schema_number == 4:
            cache = Cache(pjoin('etc', 'cache'))
            cache.write_index()
            open(pjoin('etc', 'schema'), 'w').write('5\n')
            continue

        if schema_number == 5:
            os.makedirs(pjoin('etc', 'git', 'pdk'))
            exclude_dir = pjoin('etc', 'git', 'info')
            exclude_file = pjoin(exclude_dir, 'exclude')
            exclude_needs_written = True
            if os.path.exists(exclude_file):
                contents = open(exclude_file).read()
                if 'etc/' in contents:
                    exclude_needs_written = False
            if exclude_needs_written:
                if not os.path.exists(exclude_dir):
                    os.makedirs(exclude_dir)
                open(exclude_file, 'a').write('etc/*\n')
            notes = '''
    If you have added or removed any files since your last commit, or if
    you have added files but have never committed, you will need to run
    pdk add or remove on the affected files again.
    '''
            write_migration_notes(pjoin('etc', 'MIGRATION_NOTES.txt'),
                                  notes)
            open(pjoin('etc', 'schema'), 'w').write('6\n')
            continue

        break

migrate = make_invokable(migrate)

def info(ignore):
    """Report information about the local workspace"""
    ignore.pop() # stop pylint complaining about unused arg
    try:
        ws = current_workspace()
        print 'Base Path: %s' % ws.location
        print 'Cache is: %s' % os.path.join(ws.location,'cache')
    except ConfigurationError, message:
        print message

def create_workspace(workspace_root):
    """
    Create a local pdk working directory.
    Usage:
        pdk workspace create [workspace name]
    """
    # Friends don't let friends nest workspaces.
    if currently_in_a_workspace():
        raise SemanticError(
            "%s is Already in a workspace"
            % os.getcwd()
            )

    # Create empty workspace
    os.makedirs(workspace_root)
    ws = _Workspace(workspace_root)
    os.makedirs(ws.cache_dir)
    os.makedirs(ws.vc_dir)
    os.makedirs(ws.channel_dir)
    vc = ws.vc
    vc.create()
    os.symlink(pjoin('etc', 'git'), pjoin(ws.location, '.git'))
    open(pjoin(ws.config_dir, 'schema'), 'w').write('%d\n' % schema_target)
    return ws

def create(args):
    """\\fB%prog\\fP \\fIDIRECTORY\\fP
.PP
Creates a new workspace for pdk.
.PP
The directory should not already exist.
    """
    # Friends don't let friends nest workspaces.
    if currently_in_a_workspace():
        raise SemanticError(
            "%s is Already in a workspace"
            % os.getcwd()
            )

    new_workspace_dir = args.get_new_directory()
    if not args:
        raise CommandLineError("requires an argument")
    create_workspace(new_workspace_dir)

create = make_invokable(create)

def repogen(args):
    """\\fB%prog\\fP [\\fIOPTIONS\\fP] \\fICOMPONENT\\fP
.PP
Generate a file-system repository
for a linux product.
    """
    ws = current_workspace()
    product_file = args.get_one_reoriented_file(ws)
    get_desc = ws.get_component_descriptor
    if args.opts.output_dest:
        repo_dir = pjoin(ws.location,
                         ws.reorient_filename(args.opts.output_dest))
    else:
        repo_dir = pjoin(ws.location, 'repo')
    ws.download([ws.get_component_descriptor(product_file)])
    compile_product(product_file, ws.cache, repo_dir, get_desc)

repogen = make_invokable(repogen, 'output-dest')

def mediagen(args):
    """\\fB%prog\\fP \\fICOMPONENT\\fP
.PP
Generate media for a linux product.
    """

    import picax.config
    import picax.apt
    import picax.package
    import picax.installer
    import picax.order
    import picax.split
    import picax.newrepo
    import picax.media

    ws = current_workspace()
    product_file = args.get_one_reoriented_file(ws)
    desc = ws.get_component_descriptor(product_file)
    comp = desc.load(ws.cache)
    picax.config.handle_args(component = comp)

    picax_conf = picax.config.get_config()
    picax.apt.init()
    (package_list, source_list) = \
        picax.package.get_all_distro_packages()
    first_part_space = picax.installer.install()
    order_list = picax.order.order(package_list)
    package_group = picax.split.split(order_list, package_list,
                                      source_list, first_part_space)

    for part in range(0, len(package_group)):
        current_group = package_group[part]
        top_path = "%s/bin%d" % (picax_conf["dest_path"], part + 1)
        newrepo = picax.newrepo.NewRepository(current_group, top_path)
        newrepo.write_repo()

    picax.installer.post_install()
    picax.media.create_media()

mediagen = make_invokable(mediagen)

def add(args):
    """\\fB%prog\\fP \\fIFILES\\fP
.PP
Put files under version control,
scheduling them for addition to the
repository.
It will be added on the next commit.
    """
    ws = current_workspace()
    files = args.get_reoriented_files(ws, 0)
    return ws.add(files)

add = make_invokable(add)

def remove(args):
    """\\fB%prog\\fP [\\fIOPTIONS\\fP] \\fIFILES\\fP
.PP
Remove files from version control.
The removal is essentially noted
in the changeset of the next commit.
.PP
Use of the force option also unlinks the file.
Without it, the file
must have already been unlinked
or the command will fail.
    """
    ws = current_workspace()
    files = args.get_reoriented_files(ws, 0)
    return ws.remove(files, args.opts.force)

remove = make_invokable(remove, 'force')

def mv(args):
    '''\\fB%prog\\fP \\fIFILE\\fP \\fIFILE\\fP
.PP
Wrap up the operation
of version control remove and add
into a single convenience command.
.PP
This command won't work on directories
or remove an existing file.
    '''
    ws = current_workspace()
    files = args.get_reoriented_files(ws, 0)
    if len(files) != 2:
        message = 'Must provide exactly two filenames'
        raise CommandLineError(message)

    def abspath(filename):
        '''Get the absolute path to a reoriented file.'''
        return pjoin(ws.location, filename)

    for absfile in [ abspath(f) for f in files ]:
        if os.path.isdir(absfile):
            raise InputError('Rename does not work on a directory.')

    if os.path.exists(abspath(files[1])):
        raise InputError('Cannot rename over and existing file')

    os.rename(abspath(files[0]), abspath(files[1]))
    ws.remove([files[0]], False)
    ws.add([files[1]])

mv = make_invokable(mv)

def cat(args):
    """\\fB%prog\\fI \\fIFILE\\fP
.PP
Output the content of specified file
from the HEAD commit in version control.
    """
    ws = current_workspace()
    name = args.get_one_reoriented_file(ws)
    result = ws.cat(name).read().strip()
    print >> sys.stdout, result
    return result

cat = make_invokable(cat)

def revert(args):
    """\\fB%prog\\fP \\fIFILES\\fP
.PP
Restore pristine copies
of files from the HEAD commit
in version control.
    """
    ws = current_workspace()
    files = args.get_reoriented_files(ws, 1)
    return ws.revert(files)

revert = make_invokable(revert)

def commit(args):
    """\\fB%prog\\fP [\\fIOPTIONS\\fP] \\fIFILES\\fP
.PP
Commit changes to files in the work area.
.PP
If \\fIFILES\\fP are present,
the scope of the commit is limited to these files.
If it is empty, all commit-worthy files are committed.
.PP
Naming files which have not been added will work
and can be considered a shortcut
around the pdk add command.
.PP
If no commit message is provided through options,
$EDITOR will be invoked to obtain a commit message.
    """
    ws = current_workspace()
    files = args.get_reoriented_files(ws, 0)
    ws.commit(args.opts.commit_msg_file, args.opts.commit_msg, files)

commit = make_invokable(commit, 'commit-msg')

def update(ignore):
    """\\fB%prog\\fP
.PP
DEPRECATED
.PP
Synchronize working copy to HEAD in repository.
    """
    ws = current_workspace()
    ws.update()
    return ignore

update = make_invokable(update)

def status(dummy):
    """\\fB%prog\\fP
.PP
Show the current version control status
of files in this work area.
    """
    ws = current_workspace()
    ws.status()

status = make_invokable(status)

def log(args):
    """\\fB%prog\\fP
.PP
Show version control history.
    """
    ws = current_workspace()
    ws.log(args.args)

log = make_invokable(log)

def pull(args):
    """\\fB%prog\\fP \\fIREMOTE_NAME\\fP
.PP
Bring version control info
from a remote workspace
into this workspace.
Bring working copy up-to-date
with remote HEAD revision.
.PP
The remote name should be configured
as a channel of type 'source'
in the workspace channels file.
    """
    remote_path = args.pop_arg('remote workspace name')
    local = current_workspace()
    local.pull(remote_path)

pull = make_invokable(pull)

# Externally-exposed function -- pdk channel update
def world_update(args):
    '''\\fB%prog\\fP
.PP
Reads channel configuration and downloads all metadata.
    '''
    args.assert_no_args()
    workspace = current_workspace()
    workspace.world_update()

world_update = make_invokable(world_update)

def push(args):
    """\\fB%prog\\fP \\fIREMOTE_NAME\\fP
.PP
Publish the HEAD of this workspace
to another workspace.
.PP
This command also pushes the cache.
The remote HEAD must appear
in the history of this HEAD
or the remote workspace will reject the push.
.PP
The remote name should be configured
as a channel of type 'source'
in the workspace channels file.
    """
    remote_path = args.pop_arg('remote workspace name')
    local = current_workspace()
    local.push(remote_path)

push = make_invokable(push)

def semdiff(args):
    workspace = current_workspace()
    cache = workspace.world.get_backed_cache(workspace.cache)
    files = args.get_reoriented_files(workspace)

    if args.opts.machine_readable:
        printer = print_bar_separated
    else:
        printer = print_man

    get_desc = workspace.get_component_descriptor
    if args.opts.channels:
        class faux_component(object):
            '''This is a one-off class we use to adapt a channel
            to semdiff, which expects a component.
            '''
            def __init__(self, direct_packages):
                self.direct_packages = direct_packages

            def iter_direct_packages(self):
                '''Imitate Component class'''
                return self.direct_packages

        ref = files[0]
        desc = get_desc(ref)
        old_component = desc.load(cache)
        old_package_list = list(old_component.iter_direct_packages())
        world_index = workspace.world.get_limited_index(args.opts.channels)
        new_package_list = [ i.package
                             for i in world_index.iter_all_candidates() ]
        new_component = faux_component(new_package_list)
    elif len(files) == 1 or args.opts.revision:
        if args.opts.revision:
            revision = args.opts.revision
        else:
            revision = 'HEAD'
        ref = files[0]
        # Get old
        get_hist_desc = workspace.get_historical_component_descriptor
        old_desc = get_hist_desc(ref, revision)
        old_component = old_desc.load(cache)
        old_package_list = list(old_component.iter_packages())
        # Get new
        new_desc = get_desc(ref)
        new_component = new_desc.load(cache)
        new_package_list = list(new_component.iter_packages())
    elif len(files) == 2:
        ref = files[1]
        # get old
        old_desc = get_desc(files[0])
        old_component = old_desc.load(cache)
        old_package_list = list(old_component.iter_packages())
        # Get new
        new_desc = get_desc(files[1])
        new_component = new_desc.load(cache)
        new_package_list = list(new_component.iter_packages())
    else:
        raise CommandLineError("Argument list is invalid")

    diffs = iter_diffs(old_package_list, new_package_list)
    diffs_meta = iter_diffs_meta(old_component, new_component)
    data = filter_data(chain(diffs, diffs_meta), args.opts.show_unchanged)
    printer(ref, data)

semdiff.__doc__ = '\\fB%prog\\fP [\\fIOPTIONS\\fP] ' + \
    '\\fICOMPONENT\\fP [\\fICOMPONENT\\fP]' + '''
.PP
Return a report containing
meaningful component changes.
.PP
Works against version control,
two arbitrary components,
or a component and a set of channels.
    '''

semdiff = make_invokable(semdiff, 'machine-readable', 'channels',
                         'show-unchanged', 'revision')
def dumpmeta(args):
    """\\fB%prog\\fP \\fICOMPONENTS\\fP
.PP
Prints all component metadata to standard out.
    """
    workspace = current_workspace()
    get_desc = workspace.get_component_descriptor
    cache = workspace.cache
    component_refs = args.get_reoriented_files(workspace)
    for component_ref in component_refs:
        descriptor = get_desc(component_ref)
        workspace.download([descriptor])
        comp = descriptor.load(cache)
        for item in chain(comp.iter_packages(),
                          comp.iter_components(),
                          [comp]):
            if hasattr(item, 'meta'):
                # must be a component
                meta = item.meta
                ent_type = 'component'
                ent_id = item.ref
                name = ''
            else:
                meta = item
                ent_type = item.type
                ent_id = item.ent_id
                name = item.name

            for key, value in meta.iteritems():
                if not filter_predicate(key):
                    continue

                tag = string_domain(*key)
                print '|'.join([ent_id, ent_type, name, tag, str(value)])

dumpmeta = make_invokable(dumpmeta)

def dumplinks(args):
    """\\fB%prog\\fP \\fICOMPONENT\\fP
.PP
Prints a list of entity links to standard out.
    """

    workspace = current_workspace()
    get_desc = workspace.get_component_descriptor
    cache = workspace.cache
    component_ref = args.get_one_reoriented_file(workspace)

    descriptor = get_desc(component_ref)
    workspace.download([descriptor])
    component = descriptor.load(cache)
    for item in component.iter_contents():
        for ent_type, ent_id in item.links:
            print '|'.join((item.ent_type, item.ent_id, ent_type, ent_id))

dumplinks = make_invokable(dumplinks)

def run_resolve(args, find_package, assert_resolved, abstract_constraint):
    '''Take care of details of running descriptor.resolve.

    args         - passed from command handlers
    find_package - a function we can call to pick the right package
                   out of a world_items iterator.
    assert_resolved -
                   [boolean] warn if any references are not resolved
    abstract_constraint -
                   whether stanzas must be resolved or unresolved.
    '''
    workspace = current_workspace()
    extended_cache = workspace.world.get_backed_cache(workspace.cache)
    get_desc = workspace.get_component_descriptor
    component_names = args.get_reoriented_files(workspace)
    os.chdir(workspace.location)
    for component_name in component_names:
        descriptor = get_desc(component_name)
        channel_names = args.opts.channels
        world_index = workspace.world.get_limited_index(channel_names)
        descriptor.resolve(find_package, extended_cache, world_index,
                           abstract_constraint)

        if assert_resolved:
            descriptor._assert_resolved()

        if args.opts.show_report:
            if args.opts.machine_readable:
                printer = print_bar_separated
            else:
                printer = print_man

            descriptor.diff_self(workspace, printer,
                                 args.opts.show_unchanged)

        if args.opts.save_component_changes:
            descriptor.write()

def cmp_packages(a, b):
    '''Compare two packages.'''
    return -cmp(a.version, b.version)

def find_newest(dummy, stanza, iter_world_items):
    '''Find the newest (by version) package in iter_world_items'''
    matching_packages = \
        [ i.package for i in iter_world_items
          if stanza.rule.condition.evaluate(i.package) ]
    if matching_packages:
        matching_packages.sort(cmp_packages)
        first_package = matching_packages[0]
        return first_package
    return None

def resolve(args):
    """\\fB%prog\\fP [\\fIOPTIONS\\fP] \\fICOMPONENTS\\fP
.PP
Resolves abstract package references.
.PP
If the command succeeds,
the component will be modified in place.
Abstract package references
will be populated with concrete references.
.PP
If no channel names are given,
resolve uses all channels
to resolve references.
.PP
A warning is given
if any unresolved references remain.
    """

    run_resolve(args, find_newest, True, True)

resolve = make_invokable(resolve, 'machine-readable', 'no-report',
                         'dry-run', 'channels', 'show-unchanged')

def find_upgrade(cache, stanza, iter_world_items):
    '''Find the best stanza upgrade in iter_world_items.

    The package must be newer (by version) than the currently already in
    the stanza meeting its condition, and also the newest in
    iter_world_items.
    '''
    parent_package = None
    # Find the "parent" package in the stanza.
    # Stanza is assumed to be resolved.
    for package_ref in stanza.children:
        package = package_ref.load(cache)
        if stanza.evaluate_condition(package):
            parent_package = package
            break

    candidate_packages = [ i.package for i in iter_world_items ]
    candidate_packages.sort(cmp_packages)
    for candidate in candidate_packages:
        if stanza.evaluate_condition(candidate) and \
            candidate.version > parent_package.version:
            return candidate
    return None

def upgrade(args):
    """\\fB%prog\\fP [\\fIOPTIONS\\fP] \\fICOMPONENTS\\fP
.PP
Upgrades concrete package references
by package version.
.PP
If the command succeeds,
the component will be modified in place.
Package references with concrete children
will be examined to see
if channels can provide newer packages.
If this is the case,
all concrete refrences
which are grouped
by an abstract reference
are removed and replaced
with references to newer pacakges.
.PP
If no channel names are given,
resolve uses all channels
to resolve references.
    """

    run_resolve(args, find_upgrade, False, False)

upgrade = make_invokable(upgrade, 'machine-readable', 'no-report',
                         'dry-run', 'channels', 'show-unchanged')

def download(args):
    """\\fB%prog\\fP \\fIFILES\\fP
.PP
Acquire copies of the package files needed
by the component descriptor \\fIFILES\\fP.
The needed package files will be located based
on the package indexes of configured channels.
    """
    workspace = current_workspace()
    component_names = args.get_reoriented_files(workspace)
    descriptors = [ workspace.get_component_descriptor(n)
                    for n in component_names ]
    workspace.download(descriptors)

download = make_invokable(download)

class _Workspace(object):
    """
    Library interface to pdk workspace

    Provides attributes for finding common workspace files and directories,
    as well as takes care of lazily creating related objects.

    Functions which require coordination of channels, cache, and
    version control may be found here.
    """
    def __init__(self, directory):
        self.location = os.path.abspath(directory)
        self.config_dir = pjoin(self.location, 'etc')
        self.vc_dir = pjoin(self.config_dir, 'git')
        self.cache_dir = pjoin(self.config_dir,'cache')

        self.channel_data_source = pjoin(self.config_dir, 'channels.xml')
        self.channel_dir = pjoin(self.config_dir, 'channels')
        self.outside_world_store = pjoin(self.config_dir,
                                         'outside-world.cache')

    def __create_cache(self):
        """The cache for this workspace."""
        return Cache(self.cache_dir)
    cache = cached_property('cache', __create_cache)

    def __create_vc(self):
        """The version contorl object for this workspace."""
        return VersionControl(self.location, self.vc_dir)
    vc = cached_property('vc', __create_vc)

    def __create_world(self):
        """Get the outside world object for this workspace."""
        world_data = WorldData.load_from_stored(self.channel_data_source)
        factory = OutsideWorldFactory(world_data, self.channel_dir,
                                      self.outside_world_store)
        world = factory.create()
        return world
    world = cached_property('world', __create_world)
    channels = world

    def reorient_filename(self, filename):
        '''Return the given path relative to self.location.'''
        return relative_path(self.location, filename)

    def download(self, descriptors):
        '''Download packages for the named componenst.'''
        extended_cache = self.world.get_backed_cache(self.cache)
        acquirer = self.get_acquirer()
        def run_download_pass(message):
            '''Find and acquire all needed blob_ids.'''
            for descriptor in descriptors:
                descriptor.note_download_info(acquirer, extended_cache)
            acquirer.acquire(message, self.cache)
        # Two passes are needed when pulling from remote workspaces.
        run_download_pass('Download Packages Pass 1 of 2')
        run_download_pass('Download Packages Pass 2 of 2')

    def add(self, files):
        """
        Add an item to local version control
        """
        return self.vc.add(files)

    def remove(self, files, force):
        """
        Remove an item from local version control
        """
        return self.vc.remove(files, force)

    def cat(self, name):
        """
        Remove an item from local version control
        """
        return self.vc.cat(name)

    def revert(self, files):
        """
        Remove an item from local version control
        """
        return self.vc.revert(files)

    def commit(self, commit_msg_file, commit_msg, files):
        """
        Commit changes to version control
        """
        self.vc.commit(commit_msg_file, commit_msg, files)
        self.cache.write_index()

    def update(self):
        """
        Get latest changes from version control
        """
        self.vc.update()

    def status(self):
        """
        Show version control status of files in work area.
        """
        self.vc.status()

    def log(self, limits):
        """
        Show version control history.
        """
        self.vc.log(limits)

    def pull(self, upstream_name):
        """
        Get latest changes from version control
        """
        conveyor = Conveyor(self, upstream_name)
        conveyor.pull()

    def push(self, upstream_name):
        """
        Get push local history to a remote workspace.
        """
        conveyor = Conveyor(self, upstream_name)
        conveyor.push()

    def world_update(self):
        """Update remote index files for outside world."""
        self.world.fetch_world_data()

    def get_acquirer(self):
        '''Get a MassAcquirer for this workspace.'''
        return MassAcquirer(self.world.index)

    def get_component_descriptor(self, oriented_name, handle = None):
        '''Using oriented_name, create a new component descriptor object.
        '''
        if not handle:
            full_path = pjoin(self.location, oriented_name)
            if os.path.exists(full_path):
                handle = open(full_path)
            else:
                message = 'Component descriptor "%s" does not exist.' \
                          % oriented_name
                raise InputError(message)
        return ComponentDescriptor(oriented_name, handle,
                                   self.get_component_descriptor)

    def get_historical_component_descriptor(self, oriented_name, revision):
        '''Using oriented_name and revision, create a new descriptor.'''
        def load_other_components(oriented_name):
            '''Load future descriptors from this revision.'''
            return self.get_historical_component_descriptor(oriented_name,
                                                            revision)
        handle = self.vc.cat(oriented_name, revision)
        return ComponentDescriptor(oriented_name, handle,
                                   load_other_components)

class Net(object):
    '''Encapsulates the details of most framer conversations.

    send_* methods correspond to handle_* methods on remote processes.
    (mostly)
    '''
    protocol_version = '2'

    def __init__(self, framer, local_workspace):
        self.framer = framer
        self.ws = local_workspace

    def verify_protocol(self):
        '''Verify that the remote can speak our protocol version.'''
        self.framer.write_stream(['verify-protocol'])
        self.framer.write_stream(self.protocol_version)
        frame = self.framer.read_frame()
        if frame == 'protocol-ok':
            pass
        elif frame == 'error':
            message = self.framer.read_frame()
            raise SemanticError, message
        self.framer.assert_end_of_stream()

    def handle_verify_protocol(self):
        '''Handle protocl verification'''
        self.framer.assert_frame(self.protocol_version)
        self.framer.assert_end_of_stream()
        self.framer.write_stream(['protocol-ok'])

    def send_done(self):
        '''Indicate that we are done speaking with the remote process.'''
        self.framer.write_stream(['done'])

    def send_push_pack(self, head_id, remote_commit_ids, upstream_name):
        '''Intitiate pushing of a pack file.

        head_id is where the pack starts.
        remote_commit_ids are what we do not need to send.
        '''
        self.framer.write_stream(['push-pack'])
        self.framer.write_stream(['HEAD', head_id])
        self.ws.vc.send_pack_via_framer(self.framer, [head_id],
                                        remote_commit_ids)
        self.framer.assert_frame('status')
        op_status = self.framer.read_frame()
        if op_status == 'ok':
            self.ws.vc.note_ref(upstream_name, head_id)
        elif op_status == 'out-of-date':
            raise SemanticError('Out of date. Run pdk pull and try again.')
        else:
            assert False, 'Unknown status: %s' % op_status
        self.framer.assert_end_of_stream()

    def handle_push_pack(self):
        '''Receive a pack.

        Send back an "out-of-date" status if the pack does not include
        the current HEAD in its history.
        '''
        self.framer.assert_frame('HEAD')
        head_id = self.framer.read_frame()
        self.framer.assert_end_of_stream()

        self.ws.vc.import_pack_via_framer(self.framer)
        if self.ws.vc.is_valid_new_head(head_id):
            self.ws.vc.note_ref('HEAD', head_id)
            self.framer.write_stream(['status', 'ok'])
        else:
            self.framer.write_stream(['status', 'out-of-date'])

    def send_pull_pack(self, local_commit_ids):
        '''Initiate pulling a pack file.

        local_commit_ids are ids which do not need to be sent.
        '''
        self.framer.write_stream(['pull-pack'])
        self.framer.write_stream(local_commit_ids)

        self.framer.assert_frame('HEAD')
        new_head_id = self.framer.read_frame()
        self.framer.assert_end_of_stream()
        return new_head_id

    def handle_pull_pack(self):
        '''Handle a pull pack request.'''
        remote_commit_ids = list(self.framer.iter_stream())
        head_id = self.ws.vc.get_commit_id('HEAD')
        self.framer.write_stream(['HEAD', head_id])
        self.ws.vc.send_pack_via_framer(self.framer, [head_id],
                                     remote_commit_ids)

    def send_pull_blob_list(self, section):
        '''Initiate pulling the remote blob_list.'''
        index_file = self.ws.cache.get_index_file()
        if os.path.exists(index_file):
            index_mtime = os.stat(index_file)[stat.ST_MTIME]
        else:
            index_mtime = 0
        self.framer.write_stream(['pull-blob-list'])
        self.framer.write_stream([str(index_mtime)])
        op = self.framer.read_frame()
        if op == 'new-data':
            new_mtime = int(self.framer.read_frame())
            handle = open(section.channel_file, 'w')
            for frame in self.framer.iter_stream():
                handle.write(frame)
            handle.close()
            os.utime(section.channel_file, (new_mtime, new_mtime))
            self.ws.world.index_world_data()
        elif op == 'up-to-date':
            self.framer.assert_end_of_stream()
        else:
            message = 'unknown frame recieved after pull-blob-list'
            raise SemanticError, message

    def handle_pull_blob_list(self):
        '''Handle a pull blob list request.'''
        index_file = self.ws.cache.get_index_file()
        puller_mtime = int(self.framer.read_frame())
        self.framer.assert_end_of_stream()
        if os.path.exists(index_file):
            index_mtime = os.stat(index_file)[stat.ST_MTIME]
            if puller_mtime < index_mtime:
                self.framer.write_frame('new-data')
                self.framer.write_frame(str(index_mtime))
                index_handle = open(index_file)
                self.framer.write_handle(index_handle)
                index_handle.close()
            else:
                self.framer.write_stream(['up-to-date'])
        else:
            self.framer.write_stream(['new-data', '0'])

    def handle_pull_blobs(self):
        '''Handle a pull blobs request.'''
        blob_ids = list(self.framer.iter_stream())
        for blob_id in blob_ids:
            self.ws.cache.send_via_framer(blob_id, self.framer, noop)
        self.framer.write_stream(['done'])

    def send_push_blobs(self, remote_blob_ids):
        '''Intitiate pushing blobs.'''
        self.framer.write_stream(['push-blobs'])
        cache = self.ws.cache
        # first figure out everything we need to do
        size_map = {}
        for blob_id in cache.iter_sha1_ids():
            if blob_id in remote_blob_ids:
                continue
            size_map[blob_id] = cache.get_size(blob_id)

        mass_progress = ConsoleMassProgress('Push Blobs to Remote',
                                            size_map)
        for blob_id, size in size_map.iteritems():
            progress = mass_progress.get_single_progress(blob_id)
            size_callback = SizeCallbackAdapter(progress, size)
            progress.start()
            cache.send_via_framer(blob_id, self.framer, size_callback)
            progress.done()
            mass_progress.note_finished(blob_id)
            mass_progress.write_progress()
        self.framer.write_stream(['done'])

    def handle_push_blobs(self):
        '''Handle a push blobs request.'''
        cache = self.ws.cache
        cache.import_from_framer(self.framer, NullMassProgress())
        cache.write_index()

    def listen_loop(self):
        '''Start an "event loop" for handling requests.

        Terminates on "done".
        '''
        handler_map = { 'push-pack': self.handle_push_pack,
                        'push-blobs': self.handle_push_blobs,
                        'pull-pack': self.handle_pull_pack,
                        'pull-blob-list': self.handle_pull_blob_list,
                        'pull-blobs': self.handle_pull_blobs,
                        'verify-protocol': self.handle_verify_protocol, }

        while 1:
            first = self.framer.read_frame()
            if first == 'done':
                break
            self.framer.assert_end_of_stream()
            handler_map[first]()

def listen(args):
    '''\\fB%prog\\fP
.PP
Start an event loop for handling requests
via standard in and out.
.PP
Not intended to be invoked by users.
    '''
    if len(args.args) != 1:
        raise CommandLineError('requires a workspace path')
    framer = make_self_framer()
    try:
        local_workspace = current_workspace(args.args[0])
    except NotAWorkspaceError, e:
        framer.write_stream(['error', str(e)])
        return
    net = Net(framer, local_workspace)
    net.listen_loop()

listen = make_invokable(listen)

class Conveyor(object):
    '''Adapter for dealing with widely divergent pull/push strategies.

    Pulling over anonymous https is very different from pulling over
    a framer either on the local machine or via ssh.

    Currently there is only one way to push.

    channel       - the channel object
    vc            - A version control object.
    upstream_name - The name associated with the workspace in channels.xml.

    Call self.pull() to actually initiate a pull.
    Call self.push() to actually initiate a push.
    '''
    def __init__(self, workspace, upstream_name):
        self.workspace = workspace
        self.world = self.workspace.world
        self.channel = self.world.get_workspace_section(upstream_name)
        self.full_path = self.channel.full_path
        self.vc = self.workspace.vc
        self.upstream_name = upstream_name

        parts = urlsplit(self.full_path)
        if parts[0] in ('http', 'https'):
            self.pull = self._anon_http_pull_strategy
            self.push = None
        else:
            self.pull = self._framer_pull_strategy
            self.push = self._framer_push_strategy

    def _get_framer(self):
        '''Get a framer suitable for communicating with this workspace.'''
        path = self.full_path
        parts = urlsplit(path)
        if parts[0] == 'file' and parts[1]:
            framer = make_ssh_framer(parts[1], parts[2])
        else:
            framer = make_fs_framer(path)
        return framer

    def _anon_http_pull_strategy(self):
        '''Run a pull.

        This method is run when the path indicates that we need to do
        an anonymous http pull.
        '''
        try:
            schema_url = self.full_path + '/etc/schema'
            schema_number = \
                int(get_remote_file_as_string(schema_url).strip())
        except ValueError:
            message = "Remote workspace has invalid schema number."
            raise SemanticError, message
        if schema_number != schema_target:
            raise SemanticError, 'Workspace schema mismatch with remote.'

        blob_list_url = self.full_path + '/etc/cache/blob_list.gz'
        get_remote_file(blob_list_url, self.channel.channel_file)
        self.world.index_world_data()

        git_path = self.full_path + '/etc/git'
        self.vc.direct_pull(git_path, self.upstream_name)

    def _framer_pull_strategy(self):
        '''Run a pull.

        This method is run when the path indicates that we need to
        communicate with a remote process over pipes.
        '''
        local_commit_ids = self.vc.get_all_refs()
        framer = self._get_framer()

        net = Net(framer, self.workspace)
        net.verify_protocol()
        new_head_id = net.send_pull_pack(local_commit_ids)
        self.vc.import_pack_via_framer(framer)
        self.vc.note_ref(self.upstream_name, new_head_id)
        self.vc.merge(self.upstream_name)
        net.send_pull_blob_list(self.channel)
        net.send_done()
        framer.close()

    def _framer_push_strategy(self):
        '''Run a push.

        This method is run when the path indicates that we need to
        communicate with a remote process over pipes.
        '''
        framer = self._get_framer()
        head_id = self.vc.get_commit_id('HEAD')
        try:
            remote_head = self.vc.get_commit_id(self.upstream_name)
            remote_commit_ids = self.vc.get_rev_list([remote_head])
        except CommitNotFound:
            remote_commit_ids = []
        index = self.world.index
        net = Net(framer, self.workspace)
        net.verify_protocol()
        net.send_pull_blob_list(self.channel)
        remote_blob_ids = index.get_blob_ids(self.upstream_name)
        net.send_push_blobs(remote_blob_ids)
        try:
            net.send_push_pack(head_id, remote_commit_ids,
                               self.upstream_name)
            net.send_pull_blob_list(self.channel)
        finally:
            net.send_done()
        framer.close()

# vim:set ai et sw=4 ts=4 tw=75:
