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

# Utility functions
#
# XXX - Move methods?
# Common enough to require movement up into the base test, or maybe
# to be dotted-in from a common file? It's nice to be able to refactor
# tests, not to mention have a single maintenance point.
# Imagine that!
#

pdk_init() {
    # TEMPORARY -- to be replaced with 'pdk init' when that is ready
    pdk init || {
        mkdir cache
        mkdir wip
    }
}

inode_of() {
    # Get the inode number for a given file
    stat --format='%i' $1
}

# This is the only place we should have to maintain the
# algorithm for cache placement outside of PDK proper.
# Use only this method to find files in cache
cachepath() {
    cache_dir=${cache_base:-"etc/cache"}
    if [ $(echo $1 | grep :) ]; then
        method=$(echo $1 | cut -f1 -d:)
        raw_cksum=$(echo $1 | cut -f2 -d:)
        shortpath=$(echo $raw_cksum | cut -c1-2)
        echo ${cache_dir}/$method/$shortpath/$1
    else
        echo ${cache_dir}/$1
    fi
}

check_file() {
    # XXX - to what can we rename this function?
    local expected_hash="$1"
    local repo_filename="$2"
    [ -e $repo_filename ] || fail "missing package $repo_filename"

    local cache_filename=$(cachepath "sha-1:$expected_hash")

    # Check that the hashes match
    [ $expected_hash = "$(cat $cache_filename | openssl sha1)" ] \
        || fail "incorrect hash: ${cache_filename}, got ${expected_hash}"

    # Check that the file is hard linked
    [ "$(stat --format='%h' $repo_filename)" -gt 1 ] \
        || fail "package not hard linked $repo_filename"

    # Check that the file has the same inode in/out of cache
    [ "$(inode_of $repo_filename)" = "$(inode_of ${cache_filename})" ] \
        || fail "package not hard linked $repo_filename"
}

compare_timestamps() {
    file1="$1"
    file2="$2"

    time1=$(stat -c '%Y' $file1)
    time2=$(stat -c '%Y' $file2)

    if [ "$time1" != "$time2" ]; then
        difference=$(($time2 - $time1))
        bail "timestamp mismatch $file1 $time1 -- $file2 $time2 -- $difference"
    fi
}

assert_exists() {
    local file="$1"
    [ -e $file ] || fail "Missing $file"
}

assert_not_exists() {
    local file="$1"
    [ -e $file ] && fail "Including $file" || true
}

bail() {
    msg="$*"
    if [ -n "${DEBUG}" ]; then
        echo $msg
        bash
    fi
    fail "$msg"
}

create_lighttpd_conf() {
    : ${HTTP_PORT:=8110}
    : ${HTTPS_PORT:=8111}
    mkdir -p etc
    cat <<EOF | openssl req -new -x509 -keyout etc/self.pem \
        -out etc/self.pem -nodes
.
.
.
.
.
localhost
.
EOF
    cat >etc/lighttpd.conf <<EOF
server.modules              = (
                                "mod_access",
                                "mod_alias",
                                "mod_accesslog" )

server.pid-file             = "$tmp_dir/run/lighttpd.pid"

server.dir-listing          = "enable"

server.port                 = $HTTP_PORT

\$SERVER["socket"] == "localhost:$HTTPS_PORT" {
    ssl.engine              = "enable"
    ssl.pemfile             = "etc/self.pem"
}

EOF
    PDK_SSL_NO_VERIFY=1
    export PDK_SSL_NO_VERIFY
    cat >>etc/lighttpd.conf
}

start_lighttpd() {
    : ${lighttpd_bin:=$(PATH=$PATH:/sbin:/usr/sbin:/usr/local:sbin which lighttpd)}
    $lighttpd_bin -f $(pwd)/etc/lighttpd.conf -t
    $lighttpd_bin -f $(pwd)/etc/lighttpd.conf -D &
}

# vim:set ai et sw=4 ts=4 tw=75:
