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
This module contains functionality supporting the command line handling
framework.

The basic idea is two steps:

First, implement the meat of the commands as normal callables which accept
a CommandArgs object as a single parameter and return None or throw a
pdk.exceptions exception.

Each of these functions should be run through make_invokable. i.e.
  my_command = make_invokable(my_command)

The functions should have doc strings which can be run through groff.  The
usage/help methods are formatted with a combination of optparse and groff.

Second, create a Commands object and assign these invokables to it with the
various Commands mapping methods.

See pdk.pdk_commands for an example.
"""

__revision__ = '$Progeny$'

import os
import sys
import re
import optparse
import traceback
from itertools import chain
import pdk.log as log
from pdk.exceptions import CommandLineError, InputError, \
                    SemanticError, ConfigurationError, \
                    IntegrityFault
logger = log.get_logger()

def import_and_find(module_name, function_name):
    '''Import the module and locate the function within it.

    Returns the function.
    '''
    module = __import__(module_name, globals(), locals(), ["pdk"])
    function = getattr(module, function_name)
    return function

# These functions exist more for the benefit of unit testing than
# production work. assert_attr only supports add_cmpstr. add_cmpstr makes
# it easy to add simple __str__, __repr__ and __cmp__ methods to a class.

def assert_attr(cls, item, attr):
    '''Verify that a particular object has the given attr.

    The cls argument should be class which is only used for the error
    message.
    '''
    assert hasattr(item, attr), \
        '%r instance missing %r' % (cls, attr)

def add_cmpstr(cls, *slots):
    '''Add __cmp__, __str__, and __repr__ based on the named attributes.'''

    def __cmp__(self, other):
        '''Compare %r based on class and %r''' % (cls, slots)
        all_cmp = ('__class__',) + slots
        for cmp_attr in all_cmp:
            assert_attr(cls, self, cmp_attr)
            assert_attr(cls, other, cmp_attr)
            cmp_state = cmp(getattr(self, cmp_attr),
                            getattr(other, cmp_attr))
            if cmp_state:
                return cmp_state
        return 0

    def __str__(self):
        '''Represent %r based on %r.''' % (cls, slots)
        for attr in slots:
            assert_attr(cls, self, attr)
        parts = [ repr(getattr(self, s)) for s in slots ]
        return '%s <%s>' % (self.__class__.__name__, ' '.join(parts))

    cls.__cmp__ = __cmp__
    cls.__str__ = __str__
    cls.__repr__ = __str__

class CommandSpec(object):
    '''Factory for creating CommandArgs objects.

    function - Function to invoke, containg the meat of the command. The
               function will be assed a CommandArgs object upon invocation.
    spec     - A series of strings. For details of which strings are
               available read the source code to the __init__ method.
    '''
    def __init__(self, function, *spec):
        self.function = function
        self.usage = function.__doc__.strip()
        self.spec = spec

        self.parser = optparse.OptionParser(usage = self.usage,
                                            formatter = ManHelpFormatter())
        self.command_name = None
        op = self.parser.add_option
        for item in self.spec:
            if item == 'commit-msg':
                op('-f', '--commit-msg-file',
                   dest = 'commit_msg_file',
                   help = 'File containing a prewritten commit message.',
                   metavar = 'FILE')

                op("-m", "--commit-msg",
                   dest = "commit_msg",
                   help = "Commit message to use",
                   metavar = 'MESSAGE')

            elif item == 'channels':
                op("-c", "--channel",
                   action = "append",
                   dest = "channels",
                   type = "string",
                   help = "A channel name.")

            elif item == 'machine-readable':
                op("-m", "--machine-readable",
                   action = "store_true",
                   dest = "machine_readable",
                   default = False,
                   help = "Make the output machine readable.")

            elif item == 'no-report':
                op("-R", "--no-report",
                   action = "store_false",
                   dest = "show_report",
                   default = True,
                   help = "Don't bother showing the report.")

            elif item == 'dry-run':
                op("-n", "--dry-run",
                   action = "store_false",
                   dest = "save_component_changes",
                   default = True,
                   help = "Don't save changes after processing.")

            elif item == 'output-dest':
                op('-o', '--out-file', '--out-dest',
                   dest = 'output_dest',
                   help = "Destination for output.",
                   metavar = "DEST")

            elif item == 'show-unchanged':
                op('--show-unchanged',
                   action = "store_true",
                   dest = 'show_unchanged',
                   default = False,
                   help = "Show unchanged items in report.")

            elif item == 'force':
                op('-f', '--force',
                   action = "store_true",
                   dest = 'force',
                   default = False,
                   help = "Force the operation.")

            elif item == 'revision':
                op('-r', '--rev', '--revision',
                   dest = 'revision',
                   metavar = 'REV',
                   help = "Name of a revision, tag, or branch.")

            else:
                assert False, "Unknown command line specification. '%s'" \
                       % item

        self.parser.print_help = self.print_help


    def create_invoker(self, command_name, raw_args):
        '''Create a new CommandInvoker object, processing raw_args.

        The raw_args are processed into a CommandArgs object, and are
        available in the CommandInvoker object.
        '''

        self.set_command_name(command_name)
        command_args = \
            CommandArgs(*self.parser.parse_args(args = raw_args))
        return CommandInvoker(command_name, self, command_args)

    def get_command_name(self):
        '''Return the list representing the command name.'''
        return self.command_name

    def format_command_name(self):
        '''Return a string representing the command name.'''
        return ' '.join(self.command_name)

    def set_command_name(self, command_name):
        '''Change the command name associated with this invoker.'''
        self.command_name = command_name
        self.parser.prog = self.format_command_name()

    def format_help(self):
        '''Format a complete help message.'''
        # optparse insists on putting an extra \n after the options.
        return self.parser.format_help()[:-1]

    def print_help(self):
        '''Print the help message to standard out.'''
        command_name = self.get_command_name()
        full_man = '.TH "%s" "1.%s"\n' \
            % (self.format_command_name(), command_name[0]) \
            + self.format_help()
        display_via_man(full_man)

add_cmpstr(CommandSpec, 'function', 'spec')

make_invokable = CommandSpec

class CommandInvoker(object):
    """A ready to invoke command, complete with arguments.

    This object roughly represents a closure for invoking a given command
    spec with given args. The command will be run in an exception handler
    and will sys.exit with an appropriate exit code.

    command_name  - List of command segments leading to the creation of
                    this invoker.
    spec          - CommandSpec object representing the command to invoke.
    args          - The processed arguments for the command.
    """
    def __init__(self, command_name, spec, args):
        self.spec = spec
        self.spec.set_command_name(command_name)
        self.args = args

    def apply_and_exit(self):
        '''Execute function with args in an exception handler.

        The handler will automatically take care of displaying any error
        messages and exiting if necessary.
        '''
        failure_type = 0
        try:
            return self.spec.function(self.args)
        except IntegrityFault, message:
            logger.error("Integrity Fault Noted: %s" % message)
            failure_type = 1
        except CommandLineError, message:
            logger.error("Syntax Error: %s" % message)
            self.spec.print_help()
            failure_type = 2
        except InputError, message:
            logger.error("Invalid input: %s" % message)
            failure_type = 3
        except SemanticError, message:
            logger.error("Operation cannot be performed: %s" % message)
            failure_type = 4
        except ConfigurationError, message:
            logger.error("Configuration/setup error: %s" % message)
            failure_type = 5
        except SystemExit, status:
            failure_type = status
        except:
            traceback.print_exc(sys.stderr)
            logger.error("Unknown error")
            failure_type = 6
        sys.exit(failure_type)

    def print_help(self):
        '''Print the help message.'''
        self.spec.print_help()

    def run(self):
        '''Invoke the command, wraps apply_and_exit.'''
        self.apply_and_exit()

add_cmpstr(CommandInvoker, 'spec', 'args')

class HelpInvoker(object):
    '''Like the CommandInvoker class but shows help instead of invoking.
    '''
    def __init__(self, command_name, spec):
        self.command_name = command_name
        self.spec = spec

    def run(self):
        '''Show help instead of trying to invoke a command.'''
        self.spec.set_command_name(self.command_name)
        self.spec.print_help()
        sys.exit(0)

add_cmpstr(HelpInvoker, 'command_name', 'spec')

class HelpMultiInvoker(object):
    '''Like the HelpInvoker class but shows help for multiple commands.
    '''
    def __init__(self, command_name, commands_obj, fail = False):
        self.command_name = command_name
        self.commands = commands_obj
        self.fail = fail

    def run(self):
        '''Display the help message instead of trying to invoke.'''
        self.print_help()
        if self.fail:
            raise CommandLineError(self.fail)

    def format_command_name(self):
        '''Return a string representing the command name.'''
        return ' '.join(self.command_name)

    def print_help(self):
        '''Return a help message listing my sub commands.'''
        lines = []
        lines.append('.TH "%s" "1.%s"' \
            % (self.format_command_name(), self.command_name[0]))
        lines.append('.TP')
        lines.append('Command %s contains subcommands:' \
            % gbold(self.format_command_name()))
        sub_commands = [ ' '.join(t[0][1:]) for t in self.commands ]
        sub_commands.sort()
        for sub_command in sub_commands:
            lines.append(gbold(sub_command))
            lines.append('.br')
        display_via_man(''.join([ l + '\n' for l in lines ]))

add_cmpstr(HelpMultiInvoker, 'command_name', 'commands')

class Command(object):
    '''Represents a user command as a module/spec pair.

    The CommandSpec will be loaded lazily on get_spec.
    module_name   - string, name of a module.
    function_name - string, name of an invokable.
    '''

    def __init__(self, module_name, function_name):
        self.module_name = module_name
        self.function_name = function_name

    def get_spec(self):
        '''Get the CommandSpec for this Command.'''
        return import_and_find(self.module_name, self.function_name)

    def create_invoker(self, command_name, args):
        '''Load the spec and return an invoker for it.'''
        spec = self.get_spec()
        return spec.create_invoker(command_name, args)

add_cmpstr(Command, 'module_name', 'function_name')

class DirectCommand(object):
    '''Represents a user command as a direct reference to a command spec.
    '''
    def __init__(self, spec):
        self.spec = spec

    def get_spec(self):
        '''Just returns the spec.'''
        return self.spec

    def create_invoker(self, command_name, args):
        '''Return an invoker for the spec.'''
        return self.spec.create_invoker(command_name, args)

add_cmpstr(DirectCommand, 'spec')

class CommandAlias(object):
    '''Represents a command alias.'''
    def __init__(self, commands, segments):
        self.commands = commands
        self.segments = segments
        self.command_name = self.segments[:]

    def create_invoker(self, dummy, args):
        '''Find the intended invoker for this alias.'''
        return self.commands.find(list(chain(self.segments, args)))

    def get_spec(self):
        '''Return self and pretend to be a spec for help purposes.'''
        return self

    def set_command_name(self, command_name):
        '''Just set the internal variable.'''
        self.command_name = command_name

    def format_help(self):
        '''Minimal alias pointer for the man page.'''
        message = 'alias for %s' % \
            gbold('%s %s' % (self.commands.command_name,
                             ' '.join(self.segments)))
        return message

add_cmpstr(CommandAlias, 'commands', 'segments')

class Commands(object):
    '''Hold references to multiple command objects.

    Takes care of parsing command line data to locate and invoke a user
    command. When necessary uses Help variants of Command classes.
    '''
    def __init__(self, command_name):
        self.command_name = command_name
        self.commands = {}
        self.magic_help = 'help'

    def __iter__(self):
        items = self.commands.items()
        items.sort()
        for sub_command_name, command in items:
            if isinstance(command, Commands):
                for deeper_segments, deeper_command in command:
                    deeper_segments = \
                        (self.command_name,) + deeper_segments
                    yield deeper_segments, deeper_command
            else:
                segments = (self.command_name, sub_command_name)
                yield segments, command

    def easy_map(self, command_name, module, function):
        '''Map a single word command to a module and function name.'''
        self.map((command_name,), Command(module, function))

    def map_direct(self, segments, invokable):
        '''Map a multi word command directly to a invokable reference.'''
        self.map(segments, DirectCommand(invokable))

    def map(self, segments, command):
        '''Map a multi word command to a Command object.'''
        key, tail = segments[0], segments[1:]
        if len(tail) > 0:
            sub_command = self.commands.setdefault(key, Commands(key))
            sub_command.map(tail, command)
        else:
            self.commands[key] = command

    def alias(self, segments, command_segments):
        '''Make the first multi word command an alias for the second one.
        '''
        self.map(segments, CommandAlias(self, command_segments))

    def find_help(self, args, previous = None):
        '''Find a help command for the given args.

        This is invoked when help appears before or within command args.
        --help is handled by optparse directly.
        '''
        if previous is None:
            previous = []
        current = previous + [self.command_name]

        if len(args) < 1:
            return HelpMultiInvoker(current, self)

        key, tail = args[0], args[1:]
        if key not in self.commands:
            return HelpMultiInvoker(current, self,
                                    'Tried to execute nonexistent command')

        command = self.commands[key]
        if isinstance(command, Commands):
            return command.find_help(tail, current)
        else:
            return HelpInvoker(current + [key], command.get_spec())

    def find(self, args, previous = None):
        '''Find the appropriate command object for the given args.'''
        if previous is None:
            previous = []
        current = previous + [self.command_name]

        if len(args) < 1:
            return HelpMultiInvoker(current, self,
                                    'Tried to execute partial command')
        key, tail = args[0], args[1:]

        if key == self.magic_help:
            return self.find_help(tail, previous)

        if key not in self.commands:
            raise InputError, 'No command found for given arguments'

        value = self.commands[key]
        if isinstance(value, Commands):
            return value.find(tail, current)
        else:
            return value.create_invoker(current, tail)

    def run(self, raw_args):
        '''Invoke the proper user invokable or help for the given args.'''
        try:
            invoker = self.find(raw_args)
            invoker.run()
            failure_type = 0
        except CommandLineError, message:
            logger.error("Syntax Error: %s" % message)
            failure_type = 2
        except InputError, message:
            logger.error("Invalid input: %s" % message)
            failure_type = 3
        sys.exit(failure_type)

add_cmpstr(Commands, 'command_name', 'commands')

class CommandArgs(object):
    '''Represents common operations on results from optparse.'''
    def __init__(self, opts, args):
        self.opts = opts
        self.args = args

    def get_new_directory(self):
        '''Get a new directory.

        The directory must not already exist.
        '''
        new_dir = self.pop_arg('new directory')
        if os.path.exists(new_dir):
            raise SemanticError('Already exists: "%s"' % new_dir)
        return new_dir

    def get_one_reoriented_file(self, workspace):
        '''Get exactly one filename, reoriented to the workspace. '''
        if len(self.args) != 1:
            raise CommandLineError('requires a single filename')
        return workspace.reorient_filename(self.pop_arg('filename'))

    def get_reoriented_files(self, workspace, minimum = 1):
        '''Get a minimum number of filenames, reoriented to the workspace.
        '''
        if len(self.args) < minimum:
            message = 'Must provide at least %d filename.' % minimum
            raise CommandLineError(message)
        return [ workspace.reorient_filename(f) for f in self.args ]

    def pop_arg(self, description):
        '''Remove an argument from self.args.

        description is used to form more friendly error messages.
        '''
        if len(self.args) == 0:
            raise CommandLineError('required argument: %s', description)
        return self.args.pop(0)

    def assert_no_args(self):
        '''Assert that no arguments have been given.'''
        if len(self.args) != 0:
            raise CommandLineError('command takes no arguments')

    def __cmp__(self, other):
        return cmp(self.__class__, other.__class__) or \
            cmp(self.args, other.args) or \
            False

    def __str__(self):
        return '%s <%r %r>' \
            % (self.__class__.__name__, self.opts, self.args)

def gitalic(string):
    '''Escape the string and surround it with groff for italics.'''
    return '\\fI%s\\fP' % gescape(string)

def gbold(string):
    '''Escape the string and surround it with groff for bolding.'''
    return '\\fB%s\\fP' % gescape(string)

def gescape(string):
    '''Escape - and " in the string for making groff quoted args.'''
    return re.sub(r'([-"])', r'\\\1', string)

class ManHelpFormatter(optparse.IndentedHelpFormatter):
    '''Format a help string using groff.'''

    def format_heading(self, heading):
        '''Handle the "option" string. Bolds it.'''
        return '.PP\n.B "%s"\n' % gescape(heading)

    def format_usage(self, usage):
        '''Prepends "usage :" and passes through.'''
        return 'usage: ' + usage

    def format_option(self, option):
        '''Put the option and help into a tagged paragraph.'''

        # Ick. This was probably a bug in python 2.3, fixed in 2.4.
        if hasattr(option, 'option_strings'):
            # The python 2.3 way
            option_strings = option.option_strings
        else:
            # The python 2.4 way
            option_strings = self.option_strings[option]

        return '.TP\n%s\n%s\n' \
            % (option_strings, option.help)

    def format_one_option(self, option, separator, metavar):
        '''Bold the literals, italicize the metavariables.'''
        if metavar:
            return gbold(option) + gescape(separator) + gitalic(metavar)
        else:
            return gbold(option)

    def format_option_strings(self, option):
        '''Assemble the individual options strings.

        The result is a sinle line, appropriate for the tag of a tagged
        paragraph.
        '''
        if option.takes_value():
            metavar = option.metavar or option.dest.upper()
        else:
            metavar = None

        short_opts = [ self.format_one_option(o, ' ', metavar)
                       for o in option._short_opts ]
        long_opts = [ self.format_one_option(o, '=', metavar)
                      for o in option._long_opts ]

        opts = short_opts + long_opts
        return ', '.join(opts)

def display_via_man(string):
    '''Run the string through groff with man macros and print to stdout.'''
    handle = os.popen('groff -m mandoc -t -Tutf8', 'w')
    handle.write(string)
    handle.close()

# vim:set ai et sw=4 ts=4 tw=75:
