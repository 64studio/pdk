# $Progeny$
#
#   Copyright 2005, 2006, 2006 Progeny Linux Systems, Inc.
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
util.py

Catchall module for utilities not clearly belonging anywhere else.
Currently contains path manipulation, parsing of vertical bar separated
fields, and generators which iterate of files using fixed block sizes.
"""
__revision__ = "$Progeny$"
import os
import re
import sys
import inspect
import stat
import pycurl
from cStringIO import StringIO
from cElementTree import ElementTree
from elementtree.ElementTree import XMLTreeBuilder
from xml.sax.writer import XmlWriter
from pdk.progress import ConsoleProgress, CurlAdapter
from pdk.exceptions import ConfigurationError, SemanticError, InputError

normpath = os.path.normpath

def caller():
    """Report the caller of the current function

    Very useful during debugging.
    """
    stack = inspect.stack()
    record = stack[2] # caller's caller
    source = os.path.basename(record[1])
    line = record[2]
    func = record[3]
    text = record[4]
    stack_size = len(stack)
    return "%s(%d):%d:%s:%s" % (source, line, stack_size, func, text)

def cached_property(prop_name, create_fn):
    """Make a lazy property getter that memoizes it's value.

    The prop_name is used to create an internal symbol. When debugging
    the name should be visible so it should normally match the user
    visible property name.

    The create_fn should point to a private function which returns a
    new object. The same object will be used on successive calls to
    the property getter.

    The doc string of create_fn will be used as the property's doc string.

    Usage is simlar to the built in property function.

    name = cached_value('name', __create_name)
    # where __create_name is a function returning some object
    """
    private_name = '__' + prop_name
    def _get_property(self):
        '''Takes care of property getting details.

        Memoizes the result of create_fn.
        '''
        if hasattr(self, private_name):
            value = getattr(self, private_name)
        else:
            value = None
        if not value:
            value = create_fn(self)
            setattr(self, private_name, value)
        return value

    def _set_property(self, value):
        '''Set the underlying private variable.'''
        setattr(self, private_name, value)

    def _del_property(self):
        '''Delete the underlying private variable.

        If we try to delete the property before it has been retrieved,
        just silently succeed.
        '''
        if hasattr(self, private_name):
            delattr(self, private_name)

    return property(_get_property, _set_property, _del_property,
                    doc = create_fn.__doc__)

# These _must_ come from "real" python elementtree
from elementtree.ElementTree import Comment as et_comment
from elementtree.ElementTree import ProcessingInstruction \
     as et_processing_instruction

def cpath(*args):
    """Get an absolute path object pointing to the current directory."""
    return os.path.normpath(os.path.join(os.getcwd(), *args))

def pjoin(*args):
    '''Act like os.path.join but also normalize the result.'''
    return normpath(os.path.join(*args))

def split_pipe(handle):
    """convert a file/list of "<key>|<value" pairings into a map"""
    summary = {}
    for line in handle:
        line = line.strip()
        if not line:
            continue
        key, value = line.split('|', 1)
        item = summary.setdefault(key, [])
        item.append(value)
    return summary

default_block_size = 16384

def gen_file_fragments(filename, block_size = default_block_size):
    """Run gen_fragments on a whole file."""
    return gen_fragments(open(filename), None, block_size)

def gen_fragments(handle, max_size = None,
                  block_size = default_block_size):
    """Generate a series of fragments of no more than block_size.

    Fragments are read from handle.

    If the max_size parameter is provided it acts as a limit on the total
    number of bytes read.
    """
    bytes_remaining = max_size or block_size
    while(bytes_remaining):
        this_read = min(block_size, bytes_remaining)
        data = handle.read(this_read)
        if data:
            yield data
        else:
            break
        if max_size:
            bytes_remaining -= len(data)


def assert_python_version():
    """single location to assure installed version of python"""
    if [2, 3] > sys.version_info[:2]:
        raise ConfigurationError, \
              "This program requires python 2.3 or greater"

def ensure_directory_exists(the_path):
    '''Create the base cache directory if needed.'''
    real_path = os.path.abspath(str(the_path))
    if not os.path.exists(real_path):
        os.makedirs(real_path)

class LazyWriter(object):
    """Writable file which is not opened until needed.

    Directories needed to create the file are automatically created.
    """
    def __init__(self, filename):
        self.name = filename
        self.__handle = None

    def open_if_needed(self):
        """Create and open the file is hasn't been done yet."""
        if not self.__handle:
            dir_name = os.path.dirname(self.name)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            self.__handle = open(self.name, 'w')

    def __getattr__(self, attribute):
        self.open_if_needed()
        return getattr(self.__handle, attribute)

    def write(self, block):
        """Write to the handle.

        This is written out explicitly so that accessing the write
        method as an attribute avoids opening the handle.
        """
        self.open_if_needed()
        self.__handle.write(block)

    def close(self):
        """Close the handle.

        This is defined this way so that files remain untouched if this
        object is closed but was never written to.
        """
        if self.is_started():
            self.__handle.close()

    def is_started(self):
        """Have we started writing to the file yet?"""
        return bool(self.__handle)

def curl_set_ssl(curl_object):
    '''Turn off SSL verification if the user requested so.'''
    if 'PDK_SSL_NO_VERIFY' in os.environ:
        curl_object.setopt(curl_object.SSL_VERIFYPEER, False)

def curl_set_netrc(curl_object):
    '''Make curl check .netrc when a server gives a 401.'''
    curl_object.setopt(curl_object.NETRC, curl_object.NETRC_OPTIONAL)

def get_remote_file(remote_url, local_filename, trust_timestamp = False,
                    progress = None):
    '''Obtain a remote file via url.

    Copies the file to local_filename and attempts to set the last
    modified time.
    '''
    if os.path.exists(local_filename):
        mtime = os.stat(local_filename)[stat.ST_MTIME]
    else:
        mtime = None

    handle = LazyWriter(local_filename)

    curl = pycurl.Curl()
    curl.setopt(curl.URL, remote_url)
    curl.setopt(curl.USERAGENT, 'pdk')
    curl.setopt(curl.WRITEFUNCTION, handle.write)
    curl.setopt(curl.NOPROGRESS, False)
    curl.setopt(curl.FAILONERROR, True)
    curl.setopt(curl.OPT_FILETIME, True)
    if mtime is not None and trust_timestamp:
        curl.setopt(curl.TIMEVALUE, mtime)
        curl.setopt(curl.TIMECONDITION, curl.TIMECONDITION_IFMODSINCE)
    if not progress:
        progress = ConsoleProgress(remote_url)
    adapter = CurlAdapter(progress)
    curl.setopt(curl.PROGRESSFUNCTION, adapter.callback)
    curl_set_ssl(curl)
    curl_set_netrc(curl)

    progress.start()
    curl.perform()
    progress.done()
    handle.close()
    mtime = curl.getinfo(curl.INFO_FILETIME)
    curl.close()
    if mtime != -1:
        os.utime(local_filename, (mtime, mtime))

def get_remote_file_as_string(remote_url, progress = None):
    '''Returns the contents of a remote file as a string.'''
    result = StringIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, remote_url)
    curl.setopt(curl.USERAGENT, 'pdk')
    curl.setopt(curl.WRITEFUNCTION, result.write)
    curl.setopt(curl.NOPROGRESS, False)
    curl.setopt(curl.FAILONERROR, True)
    if not progress:
        progress = ConsoleProgress(remote_url)
    adapter = CurlAdapter(progress)
    curl.setopt(curl.PROGRESSFUNCTION, adapter.callback)
    curl_set_ssl(curl)
    curl_set_netrc(curl)

    try:
        progress.start()
        curl.perform()
        progress.done()
        curl.close()
    except pycurl.error, e:
        raise SemanticError, str(e)
    return result.getvalue()

def make_path_to(file_path):
    """Given a file path, create the directory up to the
    file location.
    """
    # Candidate for pdk.util?
    file_path = os.path.abspath(file_path)
    assert file_path.find('bin/cache') == -1
    #print('make_path_to', file_path, 'from', caller())
    path_part = os.path.split(file_path)[0]
    if path_part and not os.path.isdir(path_part):
        ensure_directory_exists(path_part)

class PrettyWriter(object):
    '''Handle low-level details of writing pretty indented xml.'''
    def __init__(self, handle, encoding):
        self.writer = XmlWriter(handle, encoding = encoding)
        self.indent = 0

    def start_document(self):
        '''Start the document.'''
        self.writer.startDocument()

    def end_document(self):
        '''End the document.'''
        self.writer.endDocument()

    def start_element(self, name, attributes):
        '''Start an element with children.'''
        self.tab()
        self.writer.startElement(name, attributes)
        self.newline()
        self.indent += 2

    def end_element(self, name):
        '''End an element with children.'''
        self.indent -= 2
        self.tab()
        self.writer.endElement(name)
        self.newline()

    def text_element(self, name, attributes, text):
        '''Start and end an element with no element children.'''
        self.tab()
        self.writer.startElement(name, attributes)
        for evil_char in '<&>':
            if evil_char in text:
                # we wish this wasn't buggy. We have to work around.
                #self.writer.handle_cdata(text)
                self.writer._check_pending_content()
                self.writer._write('<![CDATA[%s]]>' % text)
                break
        else:
            self.writer.characters(text, 0, len(text))
        self.writer.endElement(name)
        self.newline()

    def pi(self, target, text):
        '''Handle inserting a processing instruction.'''
        self.tab()
        self.writer.processingInstruction(target, text)
        self.newline()

    def comment(self, text):
        '''Insert a comment.'''
        self.tab()
        # work around the python xml writer weirdness
        save_packing = self.writer._packing
        self.writer._packing = 0
        self.writer.comment(text, 0, len(text))
        self.writer._packing = save_packing
        # self.newline()

    def tab(self):
        '''Insert whitespace characters representing an indentation.'''
        self.writer.characters(self.indent * ' ', 0, self.indent)

    def newline(self):
        '''Insert a \\n to end a line.'''
        self.writer.characters('\n', 0, 1)

def write_pretty_xml_to_handle(tree, handle):
    '''Helper function for write_pretty_xml.'''
    writer = PrettyWriter(handle, 'utf-8')
    writer.start_document()
    def _write_element(element, indent):
        '''Recursively write bits of the element tree to PrettyWriter.'''
        if element.text and element.text.strip():
            writer.text_element(element.tag, element.attrib, element.text)
        else:
            writer.start_element(element.tag, element.attrib)
            for item in element:
                if item.tag == et_comment:
                    writer.comment(item.text)
                elif item.tag == et_processing_instruction:
                    writer.pi(*item.text.split(' ', 1))
                else:
                    _write_element(item, indent + 2)
            writer.end_element(element.tag)
    _write_element(tree.getroot(), 0)
    writer.end_document()

def write_pretty_xml(tree, destination):
    '''Take an elementtree structure and write it as pretty indented xml.
    '''
    if hasattr(destination, 'write'):
        write_pretty_xml_to_handle(tree, destination)
    else:
        handle = open(destination, 'w')
        try:
            write_pretty_xml_to_handle(tree, handle)
        finally:
            handle.close()

class PDKXMLTreeBuilder(XMLTreeBuilder):
    '''Behave like the elementtree base but also add comments and pis.'''
    def __init__(self):
        XMLTreeBuilder.__init__(self)
        parser = self._parser
        parser.CommentHandler = self.comment
        parser.ProcessingInstructionHandler = self.pi

    def comment(self, text):
        '''Add a comment element'''
        comment = self._target.start(et_comment, {})
        comment.text = text
        self._target.end(et_comment)

    def pi(self, target, text):
        '''Add a processing instruction.'''
        pi = self._target.start(et_processing_instruction, {})
        pi.text = ' '.join([target, text])
        self._target.end(et_processing_instruction)

def parse_xml(source):
    '''Return an ElementTree.

    Includes comments and processing instructions.
    '''
    tree = ElementTree()
    pdk_parser = PDKXMLTreeBuilder()
    tree.parse(source, pdk_parser)
    return tree

def with_access_logging(instance, its_name):
    """Debugging Aid
    Class wrapper to log access to attributes
    """
    class add_in(object):
        """WithAccess add-in wrapper"""
        def __init__(self, log):
            self.log = log
        def __getattr__(self, name):
            """Return an attribute, after reporting it"""
            self.log.info(
                caller()
                , "Accessing %s.%s" % (its_name, name)
                )
            return getattr(instance, name)
        def __setattr__(self, name, value):
            """Set an attribute, after reporting it"""
            self.log.info(caller()
                , "Setting %s.%s to %s" % (
                    its_name, name, str(value)
                    )
                )
            setattr(instance, name, value)
    return add_in()

#-----------------------------------------------------------------------
# Path management

def relative_path(base_dir, file_path):
    """Modify a file path to be relative to another (base) path.
    throws ValueError if file is not in the base tree.

    base_dir = any local directory path
    file_path = any relative or absolute file path under base_dir
    """
    # localize some functions
    sep = os.path.sep
    absolute = os.path.abspath

    # Make lists of the paths
    base_parts = absolute(base_dir).split(sep)
    file_parts = absolute(file_path).split(sep)

    if len(base_parts) > len(file_parts):
        raise ValueError("%s not within %s" % (file_path, base_dir))

    # Bite off bits from the left, ensuring they're the same.
    while base_parts:
        base_bit = base_parts.pop(0)
        file_bit = file_parts.pop(0)
        if base_bit != file_bit:
            raise ValueError("%s not within %s" % (file_path, base_dir))

    if file_parts:
        result = os.path.join(*file_parts)
    else:
        result = '.'

    # git commands require trailing slashes on directories.
    if os.path.isdir(result):
        result += "/"
    return result

#-----------------------------------------------------------------------
# Process management

def get_pipe_ends():
    '''Wrap the output of os.pipe() in proper python file objects.'''
    read_fd, write_fd = os.pipe()
    return os.fdopen(read_fd), os.fdopen(write_fd, 'w')

def noop(*dummy):
    '''Do nothing.'''
    pass

def get_waiter(pid, command):
    '''Get a closure which waits on a pid and checks its status.

    Command is used for the error message in the exception raised if
    wait returns non-zero status.
    '''
    def _wait():
        '''A closure. Calling it waits on a remote process.

        If the remote process has non-zero status, an exception
        will be raised.
        '''
        dummy, status = os.waitpid(pid, 0)
        if status:
            message = 'command "%s" failed: %d' % (command, status)
            raise SemanticError, message

        return pid
    return _wait

def execv(execv_args, set_up = noop, pipes = True):
    '''Fork and exec.

    Returns pipes for input and output, and a closure which waits on
    the pid.

    The set_up function is called just before exec.

    Execv args should be a tuple/list in the form:
    [binary, [exec args]]
    '''
    if pipes:
        child_in_read, child_in_write = os.pipe()
        parent_in_read, parent_in_write = os.pipe()
    pid = os.fork()
    if pid:
        # parent
        _wait = get_waiter(pid, execv_args)
        if pipes:
            os.close(child_in_read)
            os.close(parent_in_write)
            return os.fdopen(child_in_write, 'w'), \
                   os.fdopen(parent_in_read), \
                   _wait
        else:
            return _wait
    else:
        # child
        if pipes:
            os.close(child_in_write)
            os.close(parent_in_read)
            os.dup2(child_in_read, 0)
            os.dup2(parent_in_write, 1)
        set_up()
        os.execv(*execv_args)

def shell_command(command, set_up = noop, pipes = True):
    '''Fork and execute a shell command.

    Returns pipes for input and output, and a closure which waits on
    the pid.

    The set_up function is called just before execing the shell.
    '''
    shell_cmd = '{ %s ; } ' % command
    execv_args = ('/bin/sh', ['/bin/sh', '-c', shell_cmd])
    return execv(execv_args, set_up, pipes)

class NullTerminated(object):
    '''Reads null terminated "lines" from a file handle'''
    def __init__(self, handle, block_size = 8096):
        self.handle = handle
        self.block_size = block_size
        self.block = None

    def __iter__(self):
        current = ''
        while 1:
            self.block = self.handle.read(self.block_size)
            if not self.block:
                if current:
                    yield current
                return
            start = 0
            while 1:
                index = self.block.find('\0', start)
                if index == -1:
                    current += self.block[start:]
                    break
                else:
                    current += self.block[start:index]
                    start = index + 1
                    yield current
                    current = ''

class Framer(object):
    '''Represents "frames" of data travelling over pipes.

    On close a framer closes its pipes and calls the waiter function.

    Frames sent should arrive intact on the remote end.

    Streams are a series of non-zero length frames followed by a zero
    length frame.

    Use of this class usually involves a pair of framers running in
    separate processes. The framers are given custody of the pipes
    between the processes and are responsible for marshalling well
    defined frames of data between the processes.
    '''
    def __init__(self, remote_in, remote_out, waiter):
        self.remote_in = remote_in
        self.remote_out = remote_out
        self.waiter = waiter

    def write_frame(self, data):
        '''Write the given to self.remote_out as a frame.'''
        self.remote_in.write('%s\n' % len(data))
        self.remote_in.write(data)
        self.remote_in.write('\n\n')

    def write_stream(self, iterable):
        '''Write and terminate a whole stream of frames.

        The iterable should return a series of strings.
        The iterable should never return a zero length string.
        '''
        for item in iterable:
            self.write_frame(str(item))
        self.end_stream()

    def write_handle(self, handle, size_callback = noop):
        '''Read data from a handle in blocks and send it as a stream.'''
        for fragment in gen_fragments(handle):
            self.write_frame(fragment)
            size_callback(len(fragment))
        self.end_stream()

    def end_stream(self):
        '''Send a frame which terminates a stream.'''
        self.write_frame('')
        self.remote_in.flush()

    def read_frame(self):
        '''Retreive a sent frame. This method blocks.'''
        len_line = self.remote_out.readline()
        if not len_line:
            raise InputError('Unexpected EOF')
        length = int(len_line.strip())
        data = self.remote_out.read(length)
        self.remote_out.read(2)
        return data

    def assert_frame(self, expected):
        '''Read a frame and assert that it matches an expected value.'''
        actual = self.read_frame()
        if expected != actual:
            message = 'expected "%s" got "%s"' % (expected, actual)
            raise InputError(message)

    def assert_end_of_stream(self):
        '''Read a frame and assert that it ends a stream.'''
        self.assert_frame('')

    def iter_stream(self):
        '''Yield all the non terminating blocks in a steam.'''
        while 1:
            frame = self.read_frame()
            if frame == '':
                break
            else:
                yield frame

    def close(self):
        '''Close the underlying pipes and call the waiter function.'''
        self.remote_in.close()
        self.remote_out.close()
        self.waiter()

def make_self_framer():
    '''Make a framer connected to stdin and stdout. Waiter is a noop.'''
    return Framer(sys.stdout, sys.stdin, noop)

def make_fs_framer(workspace_path):
    '''Make a framer running pdk remote listen on a remote workspace.'''
    command = "pdk remote listen %s" % workspace_path
    return Framer(*shell_command(command, noop))

def make_ssh_framer(host, remote_path):
    '''Make a framer using ssh to run pdk remote listen on a remote host.
    '''
    command = "ssh %s pdk remote listen %s" % (host, remote_path)
    return Framer(*shell_command(command, noop))

def moo(args):
    """our one easter-egg, used primarily for plugin testing"""
    print "This program has batcow powers"
    print " _____        "
    print " }    \  (__) "
    print " }_    \ (oo) "
    print "   / ---' lJ  "
    print "  / |    ||   "
    print " *  /\---/\   "
    print "    ~~   ~~   "
    print "Have you mooed today?"
    if args:
        print "You said '%s'" % ' '.join([str(x) for x in args])

def parse_domain(raw_string):
    """Parse the domain and value out of a raw meta value."""
    match = re.match(r'(.*?)\.(.*)', raw_string)
    if match:
        return (match.group(1), match.group(2))
    else:
        return ('pdk', raw_string)

def string_domain(domain, predicate):
    '''Reassemble a domain, predicate pair, leaving out "pdk." prefixes.'''
    if not domain or domain == 'pdk':
        return predicate
    else:
        return '%s.%s' % (domain, predicate)

# vim:set ai et sw=4 ts=4 tw=75:
