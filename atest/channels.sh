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

# Try to update from channels of various types.
#
# Also test a regression where comments in channels.xml would bomb pdk.

. atest/test_lib.sh

create_lighttpd_conf <<EOF
server.document-root = "$tmp_dir"
alias.url = ( "/rpm-md/" => "$tmp_dir/test-repogen/rpm-md/",
              "/repo/" => "$tmp_dir/test-repogen/repo/",
              "/repo-nodists/" => "$tmp_dir/repo-nodists/" )
EOF

start_lighttpd

. atest/utils/repogen-fixture.sh

mkdir repo-nodists
cp \
    $PACKAGES/apache2_2.0.53-5.diff.gz \
    $PACKAGES/apache2_2.0.53-5.dsc \
    $PACKAGES/apache2_2.0.53.orig.tar.gz \
    $PACKAGES/apache2-common_2.0.53-5_i386.deb \
    repo-nodists
pushd repo-nodists;
    apt-ftparchive packages . >Packages
    gzip <Packages >Packages.gz
    apt-ftparchive sources . >Sources
    gzip <Sources >Sources.gz
popd

set_up_repogen_fixture test-repogen
cd test-repogen

pdk repogen product.xml

mkdir rpm-md
cp $PACKAGES/adjtimex-1.13-12.*.rpm rpm-md
createrepo rpm-md

cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <!-- This comment stands to trigger an old bug. -->
  <local>
    <type>dir</type>
    <path>repo/pool</path>
  </local>
  <apt-deb>
    <type>apt-deb</type>
    <path>http://localhost:$HTTP_PORT/repo/</path>
    <dist>stable</dist>
    <components>main</components>
    <archs>source i386</archs>
  </apt-deb>
  <nodists>
    <type>apt-deb</type>
    <path>http://localhost:$HTTP_PORT/repo-nodists/</path>
    <dist>./</dist>
    <archs>source binary</archs>
  </nodists>
  <rpm-md-small>
    <type>rpm-md</type>
    <path>http://localhost:$HTTP_PORT/rpm-md/</path>
  </rpm-md-small>
</channels>
EOF

pdk channel update || sh

maybe_gunzip() {
    local file="$1"
    if file -b "$file" | grep -q ^gzip; then
        gunzip <"$file"
    else
        cat "$file"
    fi
}

compare_files() {
    maybe_gunzip "$1" >"$1.diff"
    maybe_gunzip "$2" >"$2.diff"
    diff -u -a "$1.diff" "$2.diff"
    compare_timestamps "$1" "$2"
}

prefix=http_localhost_${HTTP_PORT}_repo_dists
compare_files \
    repo/dists/stable/main/binary-i386/Packages.gz \
    etc/channels/${prefix}_stable_main_binary-i386_Packages.gz

compare_files \
    repo/dists/stable/main/source/Sources.gz \
    etc/channels/${prefix}_stable_main_source_Sources.gz

prefix=http_localhost_${HTTP_PORT}_repo-nodists_.
compare_files \
    $tmp_dir/repo-nodists/Packages.gz \
    etc/channels/${prefix}_Packages.gz

compare_files \
    $tmp_dir/repo-nodists/Sources.gz \
    etc/channels/${prefix}_Sources.gz

compare_files \
    $tmp_dir/test-repogen/rpm-md/repodata/repomd.xml \
    etc/channels/http_localhost_8110_rpm-md_repodata_repomd.xml

compare_files \
    $tmp_dir/test-repogen/rpm-md/repodata/primary.xml.gz \
    etc/channels/http_localhost_8110_rpm-md_repodata_primary.xml.gz

# this tests the "already downloaded" code.
pdk channel update

prefix=http_localhost_${HTTP_PORT}_repo_dists
compare_files \
    repo/dists/stable/main/binary-i386/Packages.gz \
    etc/channels/${prefix}_stable_main_binary-i386_Packages.gz

compare_files \
    repo/dists/stable/main/source/Sources.gz \
    etc/channels/${prefix}_stable_main_source_Sources.gz

prefix=http_localhost_${HTTP_PORT}_repo-nodists_.
compare_files \
    $tmp_dir/repo-nodists/Packages.gz \
    etc/channels/${prefix}_Packages.gz

compare_files \
    $tmp_dir/repo-nodists/Sources.gz \
    etc/channels/${prefix}_Sources.gz

compare_files \
    $tmp_dir/test-repogen/rpm-md/repodata/repomd.xml \
    etc/channels/http_localhost_8110_rpm-md_repodata_repomd.xml

compare_files \
    $tmp_dir/test-repogen/rpm-md/repodata/primary.xml.gz \
    etc/channels/http_localhost_8110_rpm-md_repodata_primary.xml.gz

# vim:set ai et sw=4 ts=4 tw=75:
