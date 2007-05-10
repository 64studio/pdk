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

# Test the workspace migration tool.

schema_target=6
check_schema_target() {
    [ $schema_target = "$(cat etc/schema)" ] || fail 'schema number incorrect'
}

# manually set up a workspace in schema 1 layout
mkdir -p schema1/work/.git
mkdir -p schema1/cache/md5
ln -s $tmp_dir/schema1/work/.git schema1/VC
touch schema1/work/somefile
touch schema1/channels.xml
GIT_DIR=schema1/work/.git git-init-db
touch schema1/work/.git/remotes/some-source

pushd schema1/work
    pdk migrate && fail 'pdk migrate should fail when in a schema1 work dir'
    touch somefile
    pdk add somefile 2>errors || true
    cat errors
    grep -q 'pdk migrate' errors \
        || fail 'pdk commands should complain about migrating when in schema1.'
popd

pushd schema1
    pdk migrate
    # stuff that should be gone.
    [ -e work ] && fail 'work directory should no longer exist'
    [ -e VC ] && fail 'VC symlink should no longer exist'
    [ -e channels.xml ] && fail 'channels.xml should not be in base dir.'
    [ -e sources ] && fail 'sources should not be in base dir.'

    # stuff that should be present
    [ -d etc/cache/md5 ] || fail 'cache was not migrated properly'
    [ -e etc/channels.xml ] || fail 'channels.xml was not migrated.'
    [ -d etc/channels ] || fail 'channels dir not created.'
    [ -e somefile ] || fail 'work dir content should be in base dir.'
    [ -L etc/git  ] && fail 'etc/git should not be a symlink'
    [ -d etc/git/objects ] || fail 'etc/git should contain git info'
    [ -L .git ] || fail '.git should be a symlink'
    [ 'etc/git' = "$(readlink .git)" ] || '.git should point to etc/git'
    check_schema_target
popd

mkdir -p schema2/etc
pushd schema2
    echo 2 >etc/schema
    touch etc/outside_world.cache
    pdk migrate
    [ -d etc/channels ] || fail 'channels dir not created.'
    [ -e etc/outside_world.cache ] \
        && fail 'outside_world.cache not removed.'
    check_schema_target
popd

mkdir -p schema3/etc/git/remotes
pushd schema3
    echo 3 >etc/schema
    ln -s $(pwd)/etc/git/remotes etc/sources
    pdk migrate
    [ -e etc/sources ] && fail 'sources should be removed from etc/'
    check_schema_target
popd

mkdir -p schema4/etc/cache/md5/d4
pushd schema4
    touch etc/cache/md5/d4/md5:d41d8cd98f00b204e9800998ecf8427e
    echo md5:d41d8cd98f00b204e9800998ecf8427 \
        md5/d4/md5:d41d8cd98f00b204e9800998ecf8427e | gzip \
        >etc/cache/blob_list.gz
    echo 4 >etc/schema
    pdk migrate
    gunzip <etc/cache/blob_list.gz >blob_list
    diff -u - blob_list <<EOF
md5:d41d8cd98f00b204e9800998ecf8427e md5/d4/md5:d41d8cd98f00b204e9800998ecf8427e 0
EOF
    check_schema_target
popd

mkdir -p schema5/etc
pushd schema5
    echo zzz_hello >etc/MIGRATION_NOTES.txt
    echo 5 >etc/schema
    pdk migrate > migration_output
    [ -d 'etc/git/pdk' ] || fail 'git/pdk directory not created'
    grep -i add etc/MIGRATION_NOTES.txt \
        || fail 'missing expected message in migration notes.'
    diff -u etc/MIGRATION_NOTES.txt migration_output
    grep -i zzz_hello etc/MIGRATION_NOTES.txt \
        || fail 'missing existing migration notes.'
    grep etc/ etc/git/info/exclude
    check_schema_target
popd

# vim:set ai et sw=4 ts=4 tw=75:
