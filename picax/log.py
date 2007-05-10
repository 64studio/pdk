# $Progeny$
#
# Logging hooks.
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

"""All event logging is coordinated through this module.  Other modules
which need to log events should call the get_logger() function."""

import sys
import logging

import picax.config

logger = None

class StdoutFilter(logging.Filter):
    """This filter makes it possible to handle stdout/stderr in a more
    traditional way.  Set one stream handler each to stdout and stderr,
    with the stderr filter level set to WARNING and the stdout filter
    set to INFO or DEBUG, and attach this filter to stdout."""

    def filter(self, record):
        "Remove all the unimportant log messages."
        return record.levelno < logging.WARNING

class DebianFormatter(logging.Formatter):
    """Format log messages in a manner similar to other Debian utilities.
    """

    def format(self, record):
        """Write the log record in a manner similar to other
        Debian utilities."""

        level_letter = record.levelname[0]
        if level_letter == "C":
            level_letter = "E"
        result = level_letter + ": " + record.msg
        if record.exc_info:
            result = "%s (%s)" % (result,
                                  self.formatException(record.exc_info))
        return result

    def formatException(self, exc_info):
        "Report exceptions in a more traditional manner."

        return "%s, %s" % (exc_info[0].__name__,
                           str(exc_info[1]))

def get_logger():
    """Return the global logger.  This is intended to be API-compatible
    with PDK's logging facilities, so it can be replaced easily."""

    global logger

    if not logger:
        logger = logging.getLogger("picax")
        logger.setLevel(logging.DEBUG)

        # We have to be careful about our use of the configuration
        # system, since the config module uses the log module.
        # Basically, any configuration values we use here have to be
        # set before the config module calls get_logger().

        default_level = logging.INFO
        conf = picax.config.get_config()
        if conf["debug"]:
            default_level = logging.DEBUG
        elif conf["quiet"]:
            default_level = logging.WARNING

        errh = logging.StreamHandler(sys.stderr)
        errh.setLevel(logging.WARNING)
        errh.setFormatter(DebianFormatter())
        logger.addHandler(errh)

        infh = logging.StreamHandler(sys.stdout)
        infh.setLevel(default_level)
        infh.setFormatter(DebianFormatter())
        infh.addFilter(StdoutFilter())
        logger.addHandler(infh)

    return logger

# vim:set ai et sw=4 ts=4 tw=75:
