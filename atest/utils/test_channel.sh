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

# a utility to create a product and some component descriptor files

# get Utility functions
. atest/test_lib.sh

make_channel() {
    channel_name=$1
    mkdir $channel_name
    shift
    while [ "$1" ]
    do
        cp -a ${PACKAGES}/$1 $channel_name
        shift
    done
}

config_channel() {
    # Add a channel for the package directory
    # note: this will migrate to a proper pdk command, like:
    # pdk channel add --dir $PACKAGES progeny.com
    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <channel>
    <type>dir</type>
    <path>${PACKAGES}</path>
  </channel>
</channels>
EOF
}

# vim:set ai et sw=4 ts=4 tw=75:
