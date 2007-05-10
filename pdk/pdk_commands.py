# $Progeny$
#
#   Copyright 2006 Progeny Linux Systems, Inc.
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

'''
This module contains the official pdk commands hierarchy and the plug in
loader.
'''

from pdk.command_base import Commands, Command

from pdk.exceptions import InputError

def load_addins(config_files):
    """
    Load the configuration files and load
    the command plugins that they define.
    """
    for config_file in config_files:
        for linenominus, line in enumerate(iter(open(config_file))):
            lineno = linenominus + 1
            # Strip comments
            x = line.find('#')
            if x >= 0:
                line = line[:x]
            # See if there's anything left
            line.strip()
            if not line:
                continue
            line_list = line.split()
            if len(line_list) != 1:
                msg = "Syntax Error %s:%d: %s" \
                    % (config_file, lineno, line)
                raise InputError(msg)
            module_name = line_list[0]
            __import__(module_name, globals(), locals())

commands = Commands('pdk')
ws = 'pdk.workspace'
commands.easy_map('audit', 'pdk.audit','audit')
commands.easy_map('push', ws, 'push')
commands.easy_map('pull', ws, 'pull')
commands.easy_map('status', ws, 'status')
commands.easy_map('log', ws, 'log')
commands.easy_map('update', ws, 'update')
commands.easy_map('commit', ws, 'commit')
commands.easy_map('add', ws, 'add')
commands.easy_map('remove', ws, 'remove')
commands.easy_map('revert', ws, 'revert')
commands.easy_map('cat', ws, 'cat')
commands.easy_map('repogen', ws,'repogen')
commands.easy_map('mediagen', ws, 'mediagen')
commands.easy_map('dumpmeta', ws, 'dumpmeta')
commands.easy_map('semdiff', ws, 'semdiff')
commands.easy_map('resolve', ws, 'resolve')
commands.easy_map('upgrade', ws, 'upgrade')
commands.easy_map('download', ws, 'download')
commands.easy_map('dumplinks', ws, 'dumplinks')
commands.easy_map('migrate', ws, 'migrate')
commands.easy_map('mv', ws, 'mv')

commands.alias(['rm'], ['remove'])
commands.alias(['create', 'workspace'], ['workspace', 'create'])

commands.map(('workspace', 'create'), Command(ws, 'create'))
commands.map(('channel', 'update'), Command(ws, 'world_update'))
commands.map(('remote', 'listen'), Command(ws, 'listen'))

# vim:set ai et sw=4 ts=4 tw=75:
