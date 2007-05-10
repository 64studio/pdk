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
Exceptions

This module defines the type of exceptions which the PDK executable
('pdk') will recognize.
"""


class PdkException(Exception):
    """Base class for all PDK exception classes.
    """
    pass

class CommandLineError(PdkException):
    """Type of exception to be raised (and caught by PDK) when
    a command-line is ill-formed (parse error).
    """
    pass

class InputError(PdkException):
    """Type of exception to be raised (and caught) when the data provided
    to a command (xml files, list files, etc) are incorrect or ill-formed.

    Note: Your message in this case should include the source of input,
    or the message will be less-than-useful.
    """

class SemanticError(PdkException):
    """The exception type to raised (and caught by PDK) when a command
    was well-formed, but the operation is impossible due to the state
    or non-existence of other objects in the system.
    """

class ConfigurationError(PdkException):
    """The exception type to be raised (and caught by PDK) when the
    local system is not correctly configured, even though the the
    command was syntactically correct (and may have been semantically
    correct.
    """

class IntegrityFault(PdkException):
    """The exception type to be raised when the workspace is not
    in a consistent state
    """

# vim:set ai et sw=4 ts=4 tw=75:
