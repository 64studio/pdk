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

"""This module is an add-on to picax that provides support for CD-style
media."""

import os
import picax.config

# Standard parameters for CDs.  We could allow some of these to be
# controlled by module parameters at some point.

cd_size_multiplier = 1048576
mkisofs_std_args = "-R -J -T -joliet-long"

options = { "media-image-size": {"config-key": "image_size",
                                 "parameter": True,
                                 "parameter-type": "number",
                                 "parameter-default": 650,
                                 "parameter-desc": "megabytes",
                                 "doc": ("Image size in megabytes",)},
            "media-label": {"config-key": "label",
                            "parameter": True,
                            "parameter-desc": "label",
                            "doc": ("CD label to assign",)} }

def get_options():
    "Return the module's options for the configuration system."
    return options

def get_part_size():
    "Return the media size."
    return picax.config.get_config()["media_options"]["image_size"] \
           * cd_size_multiplier

def create_image(index, boot_image_path):
    "Create the image with the given index number."

    conf = picax.config.get_config()
    data_path = "%s/bin%d" % (conf["dest_path"], index)
    if not os.path.isdir(data_path):
        raise RuntimeError, "couldn't locate CD image source path"

    # If an image is provided, identify its type.

    boot_args = ""
    if boot_image_path is not None:
        if not os.path.exists(data_path + "/" + boot_image_path):
            raise RuntimeError, "could not find boot image"
        boot_args = "-b " + boot_image_path
        if boot_image_path[-12:] == "isolinux.bin" or \
           boot_image_path[-18:] == "isolinux-debug.bin":
            isolinux_path = os.path.dirname(boot_image_path)
            boot_args = boot_args + \
                        " -no-emul-boot -boot-load-size 4 -boot-info-table"
            boot_args = boot_args + " -c %s/boot.cat" % (isolinux_path,)
        elif boot_image_path[-8:] == "boot.img":
            boot_path = os.path.dirname(boot_image_path)
            boot_args = boot_args + " -no-emul-boot -c %s/boot.catalog" \
                        % (boot_path,)
        else:
            image_size = os.stat(data_path + "/" + boot_image_path).st_size
            if image_size not in (1228800, 1474560, 2949120):
                raise RuntimeError, "improper boot image specified"
            boot_args = boot_args + " -c boot.cat"

    # Write the apt label, if there is one.

    if conf.has_key("cd_label"):
        if not os.path.isdir(data_path + "/.disk"):
            os.mkdir("%s/.disk" % (data_path,))
        info_file = open("%s/.disk/info" % (data_path,), "w")
        info_file.write("%s (%d)\n" % (conf["cd_label"], index))
        info_file.close()

    # Handle CD label.

    label_options = ""
    if conf["media_options"].has_key("label"):
        label_options = "-V '%s %d'" % (conf["media_options"]["label"],
                                        index)

    if os.system("mkisofs -o %s/img-bin%d.iso %s %s %s %s" \
                 % (conf["dest_path"], index, mkisofs_std_args,
                    label_options, boot_args, data_path)):
        raise RuntimeError, "CD image generation failed"

# vim:set ai et sw=4 ts=4 tw=75:
