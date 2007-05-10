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

# The ethereal/tethereal packages have had trouble matching sources
# to binaries.
#
# The xsok packages are also hard. Why?

. atest/test_lib.sh

file_in_pool() {
    file="$1"
    name=$(basename $file)
    [ '1' = $(find repo/pool -name $name | wc -l) ] \
        || fail "Can't find $name."
}

plumb_files() {
    files="$@"
    rm -rf channel
    mkdir channel
    cp $files channel/

    pushd rchp
    pdk channel update
    cat >a.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc/>
    <deb/>
    <deb/>
    <deb/>
    <deb/>
    <deb/>
    <deb/>
    <deb/>
    <deb/>
  </contents>
</component>
EOF
    pdk resolve a.xml
    pdk download a.xml

    rm -rf repo
    pdk repogen a.xml

    [ $# = $(find repo/pool -type f | wc -l) ] \
        || fail 'found wrong number of files in pool'
    for file in $files; do
        file_in_pool $file
    done
    popd
}

pdk workspace create rchp
dir_channel=$(pwd)/channel
pushd rchp
cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <a>
    <type>dir</type>
    <path>${dir_channel}</path>
  </a>
</channels>
EOF
popd

plumb_files \
    packages/gcc_4.0.2-2_i386.deb \
    packages/gcc-defaults_1.30.dsc \
    packages/gcc-defaults_1.30.tar.gz

file1=packages/ethereal_0.9.13-1.0progeny1.dsc
file2=packages/ethereal_0.9.13-1.0progeny1.diff.gz
file3=packages/ethereal_0.9.13.orig.tar.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.13-1.0progeny1_ia64.deb \
    packages/ethereal-dev_0.9.13-1.0progeny1_ia64.deb \
    packages/ethereal_0.9.13-1.0progeny1_ia64.deb \
    packages/tethereal_0.9.13-1.0progeny1_ia64.deb

file1=packages/ethereal_0.9.13-1.0progeny2.dsc
file2=packages/ethereal_0.9.13-1.0progeny2.diff.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.13-1.0progeny2_ia64.deb \
    packages/ethereal-dev_0.9.13-1.0progeny2_ia64.deb \
    packages/ethereal_0.9.13-1.0progeny2_ia64.deb \
    packages/tethereal_0.9.13-1.0progeny2_ia64.deb

file1=packages/ethereal_0.9.4-1woody2.dsc
file2=packages/ethereal_0.9.4-1woody2.diff.gz
file3=packages/ethereal_0.9.4.orig.tar.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.4-1woody2_i386.deb \
    packages/ethereal-common_0.9.4-1woody2_ia64.deb \
    packages/ethereal-dev_0.9.4-1woody2_i386.deb \
    packages/ethereal-dev_0.9.4-1woody2_ia64.deb \
    packages/ethereal_0.9.4-1woody2_i386.deb \
    packages/ethereal_0.9.4-1woody2_ia64.deb \
    packages/tethereal_0.9.4-1woody2_i386.deb \
    packages/tethereal_0.9.4-1woody2_ia64.deb

file1=packages/ethereal_0.9.4-1woody3.dsc
file2=packages/ethereal_0.9.4-1woody3.diff.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.4-1woody3_i386.deb \
    packages/ethereal-common_0.9.4-1woody3_ia64.deb \
    packages/ethereal-dev_0.9.4-1woody3_i386.deb \
    packages/ethereal-dev_0.9.4-1woody3_ia64.deb \
    packages/ethereal_0.9.4-1woody3_i386.deb \
    packages/ethereal_0.9.4-1woody3_ia64.deb \
    packages/tethereal_0.9.4-1woody3_i386.deb \
    packages/tethereal_0.9.4-1woody3_ia64.deb

file1=packages/ethereal_0.9.4-1woody4.dsc
file2=packages/ethereal_0.9.4-1woody4.diff.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.4-1woody4_i386.deb \
    packages/ethereal-common_0.9.4-1woody4_ia64.deb \
    packages/ethereal-dev_0.9.4-1woody4_i386.deb \
    packages/ethereal-dev_0.9.4-1woody4_ia64.deb \
    packages/ethereal_0.9.4-1woody4_i386.deb \
    packages/ethereal_0.9.4-1woody4_ia64.deb \
    packages/tethereal_0.9.4-1woody4_i386.deb \
    packages/tethereal_0.9.4-1woody4_ia64.deb

file1=packages/ethereal_0.9.4-1woody5.dsc
file2=packages/ethereal_0.9.4-1woody5.diff.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.4-1woody5_i386.deb \
    packages/ethereal-common_0.9.4-1woody5_ia64.deb \
    packages/ethereal-dev_0.9.4-1woody5_i386.deb \
    packages/ethereal-dev_0.9.4-1woody5_ia64.deb \
    packages/ethereal_0.9.4-1woody5_i386.deb \
    packages/ethereal_0.9.4-1woody5_ia64.deb \
    packages/tethereal_0.9.4-1woody5_i386.deb \
    packages/tethereal_0.9.4-1woody5_ia64.deb

file1=packages/ethereal_0.9.4-1woody6.dsc
file2=packages/ethereal_0.9.4-1woody6.diff.gz
plumb_files $file1 $file2 $file3 \
    packages/ethereal-common_0.9.4-1woody6_i386.deb \
    packages/ethereal-common_0.9.4-1woody6_ia64.deb \
    packages/ethereal-dev_0.9.4-1woody6_i386.deb \
    packages/ethereal-dev_0.9.4-1woody6_ia64.deb \
    packages/ethereal_0.9.4-1woody6_i386.deb \
    packages/ethereal_0.9.4-1woody6_ia64.deb \
    packages/tethereal_0.9.4-1woody6_i386.deb \
    packages/tethereal_0.9.4-1woody6_ia64.deb

file1=packages/xsok_1.02-9.dsc
file2=packages/xsok_1.02-9.diff.gz
file3=packages/xsok_1.02.orig.tar.gz
plumb_files $file1 $file2 $file3 \
    packages/xsok_1.02-9_i386.deb \
    packages/xsok_1.02-9_ia64.deb

file1=packages/xsok_1.02-9woody2.dsc
file2=packages/xsok_1.02-9woody2.diff.gz
plumb_files $file1 $file2 $file3 \
    packages/xsok_1.02-9woody2_i386.deb \
    packages/xsok_1.02-9woody2_ia64.deb

# vim:set ai et sw=4 ts=4 tw=75:
