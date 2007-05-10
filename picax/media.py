# $Progeny$
#
#   Copyright 2004, 2005 Progeny Linux Systems, Inc.
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

"""This module provides a public interface to the add-on media modules,
as well as providing a mechanism for loading such modules."""

import os
import picax.config
import picax.installer
import picax.modload

loaded_module_name = None
inst = None

class MediaError(StandardError):
    "Media exception class."
    pass

class MediaBuilder:
    """This class controls the order in which media are built.  Often,
    it's necessary to build the media out of order; for example, the
    first medium might need to be built last to include information
    about the other media on it.  By default, we just create the media
    in order."""

    def __init__(self):
        pass

    def create_media(self):
        "Create the media."

        index = 1
        while can_create_image(index):
            create_image(index)
            index = index + 1

def is_media():
    "Check if there is a media module loaded."

    return inst != None

def _check_inst():
    "Raise an exception if no media module has been loaded."

    if not is_media():
        raise MediaError, "no media type has been set"

def create_media():
    """Create a MediaBuilder object, and use it to drive the media creation
    process."""

    if not is_media():
        return

    conf = picax.config.get_config()

    media_builder = None
    if "installer_component" in conf:
        media_builder = picax.installer.get_media_builder()
    if media_builder is None:
        media_builder = MediaBuilder()

    media_builder.create_media()

def set_media(name, module_dir = None):
    "Load the requested media module."

    global loaded_module_name
    global inst

    if inst is not None:
        if name != loaded_module_name:
            raise MediaError, "cannot load two different media modules"
    else:
        try:
            inst = picax.modload.load_module(name, module_dir)
        except ImportError:
            raise MediaError, "cannot find media modules for %s" \
                  % (name,)

        loaded_module_name = name

def get_options():
    "Retrieve the media module's options."

    _check_inst()

    return inst.get_options()

def get_part_size():
    "Retrieve the media size defined by the module."

    _check_inst()

    return inst.get_part_size()

def can_create_image(index):
    "Check if we're ready to start creating images."

    _check_inst()

    config = picax.config.get_config()
    path = "%s/bin%d" % (config["dest_path"], index)
    if not os.path.isdir(path):
        return False

    return True

def create_image(index, boot_image_path = None):
    "Create the media image associated with the given index."

    _check_inst()

    if not can_create_image(index):
        raise MediaError, "cannot create image for index %d" % (index,)

    return inst.create_image(index, boot_image_path)

# vim:set ai et sw=4 ts=4 tw=75:
