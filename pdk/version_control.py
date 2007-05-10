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
version_control

Version Control Library
Part of the PDK suite

The primary interface is the VersionControl class. The methods of the
class tend to correspond to actual pdk version control operations. The
details of it's operation tend to be split between the AddRemoveData and
Git classes.

AddRemoveData is a fairly simple class that persistently stores a list
of added and removed files.

Git is more complicated with a lot of methods. It is responsible for
ipc details between pdk and git. The goal of the git class is make
sure that the mechanisms underlying the VersionControl methods can be
easily deduced from the code. This generally means hiding verbose ipc
details like spawning and waiting on processes.

A common theme in this module is exploding lists when empty lists are
provided. Often version control operations expect that the user means
all when they provide no arguments. A number of methods in this module
integrate this exploding behavior.

"""
__revision__ = '$Progeny$'

import sys
import os
from sets import Set
from commands import mkarg
from shutil import copyfileobj
from tempfile import mkstemp
from pdk.exceptions import InputError, SemanticError
from pdk.util import pjoin, shell_command, NullTerminated

## version_control
## Author:  Glen Smith
## Date:    23 June 2005
## Version: 0.0.1

class CommitNotFound(SemanticError):
    '''Raised when a caller attempts to operate on a non-existent commit.
    '''
    pass

class popen_wrap_handle(object):
    '''Delegate calls to handle, but on close(), call waiter.
    '''
    def __init__(self, handle, waiter):
        self.__handle = handle
        self.__waiter = waiter

    def close(self):
        '''Close handle and call waiter.'''
        self.__handle.close()
        self.__waiter()

    def __getattr__(self, attr):
        return getattr(self.__handle, attr)

class AddRemoveData(object):
    """Stores file adds and removes persistently."""
    def __init__(self, destination):
        self.destination = destination
        self.files = {}

    def norm(filename):
        '''Normalize (os.path.normpath) the filename.'''
        return os.path.normpath(filename)
    norm = staticmethod(norm)

    def get_status(self, filename):
        '''Get the status associated with the filename.

        Returns None if the file is not known.
        '''
        return self.files.get(self.norm(filename), None)

    def add(self, files):
        '''Mark the given files as "add"s.'''
        for filename in files:
            self.files[self.norm(filename)] = 'add'

    def remove(self, files):
        '''Mark the given files as "removes"s.'''
        for filename in files:
            self.files[self.norm(filename)] = 'remove'

    def get_set_by_value(self, value):
        '''Get a set of all files set to the given value.'''
        return Set([ k for k, v in self.files.iteritems() if v == value ])

    def get_added_files(self):
        '''Get a set of all added files.'''
        return self.get_set_by_value('add')

    def get_removed_files(self):
        '''Get a set of all removed files.'''
        return self.get_set_by_value('remove')

    def filter_add_files(self, files):
        '''Filter the given file list down to only added files.

        List explodes to all added files if provided an empty list.
        '''
        if files:
            return Set(files) & self.get_added_files()
        else:
            return self.get_added_files()

    def filter_remove_files(self, files):
        '''Filter the given file list down to only removed files.

        List explodes to all removed files if provided an empty list.
        '''
        if files:
            return Set(files) & self.get_removed_files()
        else:
            return self.get_removed_files()

    def save(self):
        '''Rewrite the persistent add/remove list.'''
        keys = self.files.keys()
        keys.sort()
        handle = open(self.destination, 'w')
        for key in keys:
            print >> handle, key, self.files[key]
        handle.close()

    def clear(self, files):
        '''Clear the given files from the list.

        Files to clear explodes to all when provided an empty list.
        '''
        if files:
            for filename in files:
                if filename in self.files:
                    del self.files[filename]
            self.save()
        else:
            if os.path.exists(self.destination):
                os.unlink(self.destination)


    def load(destination):
        '''Load a new AddRemove object from the given file.'''
        self = AddRemoveData(destination)
        if os.path.exists(destination):
            handle = open(destination)
            for line in handle:
                key, value = line.split()
                self.files[key] = value
            handle.close()
        return self
    load = staticmethod(load)

class Git(object):
    '''Takes care of IPC between pdk and git.

    work_dir is the version control work area.

    git_dir is the git database.

    priv_dir is a directory in the git db where we can put private data.

    exclude_file is a file in the git db which contains patterns git should
        ignore.

    index_file is where the git index file is kept. If it is set to
        None, the default git index file is used.
    '''
    def __init__(self, work_dir, git_dir, priv_dir,
                 exclude_file, index_file):
        self.work_dir = work_dir
        self.git_dir = git_dir
        self.priv_dir = priv_dir
        self.exclude_file = exclude_file
        self.index_file = index_file

    def popen2(self, command, pipes = True):
        """Forks off a git command.

        Returns handles to stdin and standard out.
        command is fed to /bin/sh, not exec'ed directly.

        Command is executed with cwd set to self.work_dir, and
        env variable GIT_DIR pointed at self.git_dir.
        """
        def set_up_child():
            '''Child process should chdir [work]; and set GIT_DIR.'''
            os.chdir(self.work_dir)
            os.environ.update({ 'GIT_DIR': self.git_dir })
            if self.index_file:
                os.environ.update({ 'GIT_INDEX_FILE': self.index_file })
            if 'PDK_SSL_NO_VERIFY' in os.environ:
                os.environ.update({ 'GIT_SSL_NO_VERIFY': '1' })
        return shell_command(command, set_up_child, pipes)

    def shell_to_string(self, command, pipes = True):
        """Execute self.popen2; capture stdout as a string.

        Uses self.popen2, so it inherits those characteristics.

        Closes the command's stdin.
        """
        remote_in, remote_out, waiter = self.popen2(command, pipes)
        remote_in.close()
        value = remote_out.read()
        remote_out.close()
        waiter()
        return value

    def quote_args(self, files):
        '''Join files into a single shell quoted string.'''
        return ''.join([ mkarg(f) for f in files ])

    def unlink_index(self):
        '''Remove the index file if it exists.'''
        if self.index_file:
            index_file = self.index_file
        else:
            index_file = pjoin(self.git_dir, 'index')
        if os.path.exists(index_file):
            os.unlink(index_file)

    def write_empty_tree(self):
        '''Create an empty tree object and return its tree_id.'''
        self.unlink_index()
        self.run_update_index([])
        tree_id = self.shell_to_string('git-write-tree').strip()
        return tree_id

    def iter_diff_index(self, tree_id):
        '''Run git-diff-index aginst the given tree.

        Results are run through iter_diff_files to make the iterator.

        Rename and break detection are enabled.
        '''
        cmd = 'git-diff-index -z -B -M %s' % mkarg(tree_id)
        remote_in, remote_out, waiter = self.popen2(cmd)
        remote_in.close()
        for status, file_name, extra in self.iter_diff_files(remote_out):
            yield status, file_name, extra
        waiter()

    def iter_diff_files(self, handle):
        '''Iterate over null terminated results of git-diff-*.

        Yields status, filename, extra_filename; where status is the
        status code from git-diff-*, filename is the filename, and
        extra_filename is either None or a filename involved in a
        rename or copy operation.

        The command executed should contain -z, as this function
        assumes null terminated output.
        '''
        segments = iter(NullTerminated(handle))
        try:
            while 1:
                info = segments.next()
                # strip colon
                info = info[1:]
                info_fields = info.split()
                status = info_fields[4]
                file_name = segments.next()
                if status[0] in 'CR':
                    extra_file_name = segments.next()
                else:
                    extra_file_name = None
                yield status, file_name, extra_file_name
        except StopIteration:
            pass

    def run_init_db(self):
        '''Initialize a new git instance.'''
        self.shell_to_string('git-init-db')

    def iter_ls_tree(self, raw_tree, raw_files):
        '''Run git-ls-tree against the given tree.

        Yields stat, kind, blob_id, filename.

        File list explodes to all files if empty.
        '''
        if raw_files:
            files = '--' + self.quote_args(raw_files)
        else:
            files = ''
        tree = mkarg(raw_tree)
        cmd = 'git-ls-tree -r -z %s %s' % (tree, files)
        remote_in, remote_out, waiter = self.popen2(cmd)
        remote_in.close()
        for item in NullTerminated(remote_out):
            stat, kind, blob_id, filename = item.split(None, 3)
            yield stat, kind, blob_id, filename
        waiter()

    def iter_ls_files(self, files, modified_flag = False):
        '''Run git-ls-files.

        Yields filename.

        If modified_flag is true, only modified files are
        returned. The modified filter is applied after file list
        explosion.
        '''
        args = self.quote_args(files)

        if modified_flag:
            modified_arg = '-m'
        else:
            modified_arg = ''

        cmd = 'git-ls-files -z %s %s' % (modified_arg, args)
        remote_in, remote_out, waiter = self.popen2(cmd)
        remote_in.close()
        for filename in NullTerminated(remote_out):
            yield filename
        waiter()

    def iter_unknown_files(self):
        '''Run git-ls-files -o to find "unknown" files.

        Yields filename.
        '''
        cmd = 'git-ls-files -z -o --directory --exclude-from=%s' \
              % self.exclude_file
        remote_in, remote_out, waiter = self.popen2(cmd)
        remote_in.close()
        for filename in NullTerminated(remote_out):
            yield filename
        remote_out.close()
        waiter()

    def run_update_index(self, files, add_flag = False,
                         remove_flag = False, force_remove_flag = False):
        '''Run git-update-index on the given files.

        add_flag implies --add.
        remove_flag implies --remove.
        force_remove flat implies --force-remove
        '''
        if add_flag:
            add_arg = '--add'
        else:
            add_arg = ''

        if remove_flag:
            remove_arg = '--remove'
        else:
            remove_arg = ''

        if force_remove_flag:
            force_remove_arg = '--force-remove'
        else:
            force_remove_arg = ''

        cmd = 'git-update-index -z %s %s %s --stdin' \
              % (add_arg, remove_arg, force_remove_arg)
        remote_in, remote_out, waiter = self.popen2(cmd)
        for filename in files:
            remote_in.write('%s\0' % filename)
        remote_in.close()
        remote_out.close()
        waiter()

    def run_update_index_cacheinfo(self, mode, blob_id, filename):
        '''Run git-update-index --cacheinfo.'''
        update_command = 'git-update-index --cacheinfo %s %s %s' \
                         % (mode, blob_id, mkarg(filename))
        self.shell_to_string(update_command)

    def run_checkout_index(self, files, force_flag = False,
                           all_flag = False):
        '''Run git-checkout-index.

        File list explodes to all files if file list is empty.

        force_flag implies -f
        add_flag implies -a
        '''
        if force_flag:
            force_arg = '-f'
        else:
            force_arg = ''

        if all_flag:
            all_arg = '-a'
        else:
            all_arg = ''

        file_args = self.quote_args(files)
        checkout_command = 'git-checkout-index %s %s -- %s' \
                           % (force_arg, all_arg, file_args)
        self.shell_to_string(checkout_command)

    def run_read_tree(self, tree_id):
        '''Run git-read-tree on the given tree.'''
        self.shell_to_string('git-read-tree %s' % mkarg(tree_id))

    def refresh_index(self):
        '''Run git-update-index --refresh.'''
        self.shell_to_string('git-update-index --refresh || true')

    def has_index_changed(self, tree_id):
        '''Make sure that the index file is identical to the given tree.'''
        output = self.shell_to_string('git-diff-index --cached %s'
                                      % mkarg(tree_id))
        if output.strip():
            return True
        else:
            return False

    def run_commit(self, commit_message_file, commit_message):
        '''Execute a raw git commit.

        This is only used for simple one parent commits.
        '''
        if self.is_new():
            parent_arg = ''
        else:
            parent = self.shell_to_string('git-rev-parse HEAD').strip()
            parent_arg = '-p %s' % parent

        tree_id = self.shell_to_string('git-write-tree').strip()
        cmd = 'git-commit-tree %s %s' % (tree_id, parent_arg)

        remote_in, remote_out, waiter = self.popen2(cmd)
        if commit_message_file:
            if commit_message_file == '-':
                handle = sys.stdin
            else:
                handle = open(commit_message_file)
            for commit_line in handle:
                if commit_line[0] == '#':
                    continue
                remote_in.write(commit_line)
            if handle != sys.stdin:
                handle.close()
        elif commit_message:
            remote_in.write(commit_message)
        else:
            fd_no, temp_file = mkstemp('.txt', 'commit-msg')
            os.close(fd_no)
            self.shell_to_string('git-status > %s' % temp_file)
            editor = os.environ.get('EDITOR', 'vi')
            edit_waiter = self.popen2('%s %s' % (editor, temp_file), False)
            edit_waiter()
            handle = open(temp_file)
            copyfileobj(handle, remote_in)
            handle.close()
            os.unlink(temp_file)

        remote_in.close()
        commit_id = remote_out.read().strip()
        remote_out.close()
        waiter()
        self.shell_to_string('git-update-ref HEAD %s' % commit_id)
        self.shell_to_string('git-update-server-info')

    def filter_refs(self, raw_refs):
        '''Return a list of refs that are given and present.

        Applies only to commit ids.
        '''
        refs = Set(raw_refs)
        head_ids = self.get_all_refs()
        refs_here = Set(self.get_rev_list(head_ids, []))
        return refs_here & refs

    def get_rev_list(self, head_ids, limits):
        '''Invoke git-rev-list on the given commit_ids.

        limits is used to limit the rev-list generation.
        '''
        limit_string = ' '.join([ mkarg('^%s') % l for l in limits ])
        command = 'git-rev-list %s %s' % (self.quote_args(head_ids),
                                          limit_string)
        output = self.shell_to_string(command)
        refs_here = [ i.strip() for i in output.split() ]
        return refs_here

    def direct_fetch(self, url, upstream_name):
        '''Use git directly to do a pull.'''
        # for now we assume master, as HEAD is inaccessible. too bad.
        refspec = '+master:%s' % (upstream_name)
        command = 'git fetch %s %s' % (mkarg(url), refspec)
        wait = self.popen2(command, False)
        wait()

    def get_pack_handle(self, refs_wanted, raw_refs_not_needed):
        '''Return a file handle + waiter streaming a git pack.'''

        refs_not_needed = self.filter_refs(raw_refs_not_needed)
        command_string = 'git-rev-list --objects '
        for ref in refs_wanted:
            command_string += '%s ' % ref
        for ref in refs_not_needed:
            command_string += '^%s ' % ref
        command_string += '| git-pack-objects --stdout'
        self.shell_to_string(command_string)
        remote_in, remote_out, waiter = self.popen2(command_string)
        remote_in.close()
        return popen_wrap_handle(remote_out, waiter)

    def get_unpack_handle(self):
        '''Return a file handle + waiter for receiving a git pack.'''
        command_string = 'git-unpack-objects'
        remote_in, remote_out, waiter = self.popen2(command_string)
        remote_out.close()
        return popen_wrap_handle(remote_in, waiter)

    def is_valid_new_head(self, new_head):
        '''Does this new head_id include the old head_id in its history.'''
        if self.is_new():
            return True
        new_revs = self.get_rev_list([new_head], [])
        old_head = self.get_commit_id('HEAD')
        return old_head in new_revs

    def get_commit_id(self, ref_name):
        '''Return the commit_id for a given name.'''
        command_string = 'git-rev-parse %s' % ref_name
        try:
            commit_id = self.shell_to_string(command_string).strip()
        except SemanticError:
            raise CommitNotFound('No commit for "%s"' % ref_name)
        return commit_id

    def note_ref(self, upstream_name, commit_id):
        '''Note a commit id as refs/heads/[upstream_name].'''
        self.shell_to_string('git-update-ref %s %s'
                             % (mkarg(upstream_name), commit_id))

    def get_all_refs(self):
        '''List all raw commit_ids found under the git refs directory.'''
        command_string = 'git-rev-parse --all'
        output = self.shell_to_string(command_string)
        commit_ids = [ i.strip() for i in output.split() ]
        return commit_ids

    def is_new(self):
        '''Is this a "new" (no commits) git repository?'''
        command_string = 'git-rev-parse HEAD 2>/dev/null'
        try:
            self.shell_to_string(command_string)
        except SemanticError:
            return True
        return False

    def clean_fetch_head(self):
        '''Remove any "FETCH_HEAD" present.'''
        command = 'rm -f %s/FETCH_HEAD' % self.git_dir
        wait = self.popen2(command, False)
        wait()

    def silence(self, command, silent):
        '''If silent is true, wrap command up in a >/dev/null.'''
        if silent:
            return '{ %s ; } >/dev/null' % command
        else:
            return command

    def merge(self, dest_head, source_head, silent):
        '''Invoke git merge.'''
        command = 'git merge -n "Merge" %s %s' \
                  % (mkarg(dest_head), mkarg(source_head))
        command = self.silence(command, silent)
        wait = self.popen2(command, False)
        wait()

    def new_branch(self, dest_head, source_head, silent):
        '''Make a brand new branch.'''
        command = 'git branch %s %s' \
                  % (mkarg(dest_head), mkarg(source_head))
        command = self.silence(command, silent)
        wait = self.popen2(command, False)
        wait()

    def checkout_branch(self, head_id, silent):
        '''Do a first checkout of a branch.'''
        command = 'git checkout %s' % (mkarg(head_id))
        command = self.silence(command, silent)
        wait = self.popen2(command, False)
        wait()

    def get_commit(self, commit_id):
        '''Get the contents of a commit as a string.'''
        return self.shell_to_string('git-cat-file commit %s' % commit_id)

    def get_blob(self, blob_id):
        '''Get a wrapped filehandle of a blob.'''
        command = 'git-cat-file blob %s' % mkarg(blob_id)
        remote_in, remote_out, waiter = self.popen2(command)
        remote_in.close()
        return popen_wrap_handle(remote_out, waiter)

class VersionControl(object):
    """
    Library Interface to pdk version control
    """

    def __init__(self, work_path, git_path):
        self.work_dir = work_path
        self.vc_dir = git_path
        self.priv_dir = pjoin(git_path, 'pdk')
        self.add_remove_file = pjoin(self.priv_dir, 'add-remove')
        self.alt_index = pjoin(self.priv_dir, 'pdk-index')
        self.exclude = pjoin(git_path, 'info', 'exclude')
        self.git = Git(self.work_dir, self.vc_dir, self.priv_dir,
                       self.exclude, None)
        self.alt_git = Git(self.work_dir, self.vc_dir, self.priv_dir,
                           self.exclude, self.alt_index)


    def get_add_remove(self):
        """Get the AddRemove object for this repository."""
        return AddRemoveData.load(self.add_remove_file)

    def create(self):
        """
        Populate self.vc_dir with a git skeleton.
        """
        self.git.run_init_db()
        remotes_dir = pjoin(self.vc_dir, 'remotes')
        if not os.path.exists(remotes_dir):
            os.makedirs(remotes_dir)
        os.makedirs(self.priv_dir)
        print >> open(self.exclude, 'w'), 'etc'

    def assert_no_dirs(self, files):
        '''Assert that none of the given files is a directory.'''
        for filename in files:
            if os.path.isdir(pjoin(self.work_dir, filename)):
                message = 'VC does not operate on directories: "%s"' \
                          % filename
                raise InputError, message

    def assert_known(self, raw_given_files, expected_known):
        '''Assert the "known" status of the given files equals expected.
        '''
        given_files = Set(raw_given_files)
        if self.is_new():
            found_files = Set([])
        else:
            iter_tree = self.git.iter_ls_tree('HEAD', raw_given_files)
            git_found_files = Set([ t[3] for t in iter_tree ])
            add_remove = self.get_add_remove()
            added_found_files = add_remove.get_added_files() & given_files
            found_files = ( git_found_files | added_found_files ) \
                          - add_remove.get_removed_files()

        if expected_known:
            missing_files = given_files - found_files
            if missing_files:
                message = 'VC unknown files: %r' % list(missing_files)
                raise SemanticError, message
        else:
            if found_files:
                message = 'VC files already known: %r' % list(found_files)
                raise SemanticError, message

    def add(self, files):
        """
        Initialize version control
        """
        self.assert_no_dirs(files)
        self.assert_known(files, False)
        for name in files:
            if not os.path.exists(pjoin(self.work_dir, name)):
                message = 'File %s missing.' % name
                raise SemanticError(message)
        add_remove = self.get_add_remove()
        add_remove.add(files)
        add_remove.save()

    def remove(self, files, force):
        """
        Remove files from version control.
        """
        self.assert_no_dirs(files)
        self.assert_known(files, True)
        for name in files:
            if os.path.exists(pjoin(self.work_dir, name)):
                if force:
                    os.unlink(name)
                else:
                    message = 'File %s exists. Remove it and retry.' % name
                    raise SemanticError(message)
        add_remove = self.get_add_remove()
        add_remove.remove(files)
        add_remove.save()

    def revert(self, files):
        """
        Initialize version control
        """
        add_remove = self.get_add_remove()
        removed_files = add_remove.get_removed_files()
        for filename in files:
            if filename in removed_files:
                add_remove.clear([filename])
        self.assert_known(files, True)
        add_remove.clear(files)
        self.update_index(add_remove, files, self.alt_git)

        iter_tree = self.git.iter_ls_tree('HEAD', files)

        for mode, kind, blob_id, filename in iter_tree:
            if kind != 'blob':
                continue
            self.alt_git.run_update_index_cacheinfo(mode, blob_id,
                                                    filename)
            self.alt_git.run_checkout_index([filename], force_flag = True)

    def verify_add_remove(self, add_remove):
        '''Verify the (non)existence of files in add_remove are valid.'''
        for filename in add_remove.get_added_files():
            full_path = pjoin(self.work_dir, filename)
            if not os.path.exists(full_path):
                raise SemanticError, 'Missing added file "%s".' % full_path

        for filename in add_remove.get_removed_files():
            full_path = pjoin(self.work_dir, filename)
            if os.path.exists(full_path):
                raise SemanticError, 'Delete removed file "%s".' \
                    % full_path

        if not self.is_new():
            for item in self.git.iter_ls_tree('HEAD', []):
                # don't bother verifying directories
                mode = item[0]
                if mode.startswith('04'):
                    continue
                filename = item[3]
                if add_remove.get_status(filename):
                    continue
                full_path = pjoin(self.work_dir, filename)
                if not os.path.exists(full_path):
                    message = 'Missing known file "%s".' % full_path
                    raise SemanticError, message

    def update_index(self, add_remove, files, git):
        '''Write from scratch a correct index file for this workspace.'''
        if self.is_new():
            pass
        else:
            git.run_read_tree('HEAD')
            git.refresh_index()
        # If no files are provided, git-ls-files will list all files.
        # We rely on that.
        removed_files = add_remove.filter_remove_files(files)
        git.run_update_index(removed_files, force_remove_flag = True)

        # Find all modified files.
        # Be overly trusting. If we really cared about whether all the
        # files existed we would have called verify_add_remove before
        # calling this function.
        iter_modified = list(git.iter_ls_files(files,
                                               modified_flag = True))
        modified_files = []
        for filename in iter_modified:
            full_path = pjoin(self.work_dir, filename)
            if os.path.exists(full_path):
                modified_files.append(filename)

        modified_files.extend(add_remove.filter_add_files(files))
        git.run_update_index(modified_files, add_flag = True)

    def commit(self, commit_message_file, commit_message, files):
        '''Commit this workspace.'''
        add_remove = self.get_add_remove()

        self.assert_no_dirs(files)
        self.verify_add_remove(add_remove)
        self.update_index(add_remove, files, self.alt_git)

        # look for any files which need to be implicitly added and add them
        all_files = Set(self.alt_git.iter_ls_files([]))
        given_files = Set(files)
        removed_files = add_remove.get_removed_files()
        implicit_add_files = given_files - all_files - removed_files
        for implicit_add in implicit_add_files:
            full_path = pjoin(self.work_dir, implicit_add)
            if not os.path.exists(full_path):
                message = 'Missing file "%s".' % implicit_add
                raise SemanticError, message

        self.alt_git.run_update_index(implicit_add_files, add_flag = True)
        self.alt_git.run_commit(commit_message_file, commit_message)

        add_remove.clear(files)

    def update(self):
        """
        update the version control
        """
        self.alt_git.run_read_tree('HEAD')
        self.alt_git.run_checkout_index([], all_flag = True)

    def status(self):
        '''
        Send git status information to standard out.
        '''
        if self.is_new():
            tree_id = self.alt_git.write_empty_tree()
        else:
            tree_id = 'HEAD'

        files = []
        add_remove = self.get_add_remove()
        self.update_index(add_remove, files, self.alt_git)

        iter_diff = self.alt_git.iter_diff_index(tree_id)
        for status, filename, extra in iter_diff:
            # corner case: If it's deleted but we don't know about it,
            # then it's missing.

            if status[0] == 'D' \
                   and add_remove.get_status(filename) != 'remove':
                status = '!'

            if extra:
                line = '\t'.join((status, filename, extra))
            else:
                line = '\t'.join((status, filename))
            print line

        for name in self.alt_git.iter_unknown_files():
            print '\t'.join(('?', name))

    def log(self, limits):
        '''
        Send commit messages to standard out.
        '''
        if self.is_new():
            message = 'Log not available on new workspaces. ' + \
                      'Commit something first.'
            raise InputError(message)
        revs = self.git.get_rev_list(['HEAD'], limits)
        for rev in revs:
            print self.git.get_commit(rev)

    def cat(self, filename, revision = 'HEAD'):
        '''Get the historical version of the given filename.

        Returns a handle.
        '''
        self.assert_no_dirs([filename])
        if self.is_new():
            message = 'Empty version control. Need an initial commit.'
            raise SemanticError(message)

        matching_files = list(self.git.iter_ls_tree(revision, [filename]))
        matches = len(matching_files)
        assert matches in (0, 1)
        if matches == 0:
            raise SemanticError('No file by that name in version %s'
                                % revision)
        elif matches == 1:
            blob_id = matching_files[0][2]
            return self.git.get_blob(blob_id)

    def is_new(self):
        '''Is this a "new" workspace (no commits)?'''
        return self.git.is_new()

    def get_all_refs(self):
        '''Get all top level refs for this workspace.'''
        return self.git.get_all_refs()

    def is_valid_new_head(self, new_head):
        '''Can we reach the new_head without merging?'''
        return self.git.is_valid_new_head(new_head)

    def direct_pull(self, url, upstream_name):
        '''Do a direct git pull and merge with it.'''
        self.git.direct_fetch(url, upstream_name)
        self.merge(upstream_name)

    def send_pack_via_framer(self, framer, target_ids, unneeded_ids):
        '''Send a pack via the given framer.'''
        handle = self.git.get_pack_handle(target_ids, unneeded_ids)
        framer.write_handle(handle)
        handle.close()

    def import_pack_via_framer(self, framer):
        '''Import a pack from the given framer.'''
        handle = self.git.get_unpack_handle()
        for frame in framer.iter_stream():
            handle.write(frame)
        handle.close()

    def get_commit_id(self, ref_name):
        '''Get the commit_id for the given ref_name.'''
        return self.git.get_commit_id(ref_name)

    def note_ref(self, upstream_name, commit_id):
        '''Make a new head file for the given commit_id.'''
        self.git.note_ref(upstream_name, commit_id)

    def get_rev_list(self, head_ids):
        '''List all commits reachable from head_ids.'''
        return self.git.get_rev_list(head_ids, [])

    def merge(self, branch_name, silent = False):
        '''Do a merge from branch to HEAD.

        Do a plain checkout for new repositories.
        '''
        self.git.clean_fetch_head()
        if self.is_new():
            self.alt_git.new_branch('master', branch_name, silent)
            self.alt_git.checkout_branch('master', silent)
        else:
            add_remove = self.get_add_remove()
            self.verify_add_remove(add_remove)
            self.update_index(add_remove, [], self.alt_git)
            if self.alt_git.has_index_changed('HEAD'):
                raise InputError, \
                      'Cannot merge with uncommitted changes in the ' + \
                      'workspace.'
            self.alt_git.merge('HEAD', branch_name, silent)
            add_remove.clear([])

# vim:set ai et sw=4 ts=4 tw=75:
