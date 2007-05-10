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

# The resolve command should transform abstract references to concrete
# references.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

# Add some concrete and abstract package references to a new component.
cat >apache-meta.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb>
      <name>apache2-common</name>
      <meta>
        <answer>42</answer>
      </meta>
    </deb>
    <rpm>
      <name>not-present</name>
      <meta>
         <this>shouldn't-show-up</this>
      </meta>
    </rpm>
    <rpm>
      <name>adjtimex</name>
      <meta>
         <this>very-much-should</this>
      </meta>
    </rpm>
  </contents>
</component>
EOF


cat >report.xml <<EOF
<?xml version="1.0"?>
<component>
  <meta>
    <repo-type>report</repo-type>
    <format>%(name)s %(version.epoch)s %(version.version)s %(version.release)s %(filename)s %(cache_location)s %(blob_id)s %(answer)s %(this)s</format>
  </meta>
  <contents>
    <component>progeny.com/apache.xml</component>
    <component>progeny.com/time.xml</component>
    <component>apache-meta.xml</component>
  </contents>
</component>
EOF

pdk repogen report.xml >report.txt

cat >control.txt <<EOF
adjtimex  1.13 13 adjtimex-1.13-13.i386.rpm $tmp_dir/test-repogen/etc/cache/md5/2c/md5:2c0376dce66844970269876d1e09fea9 md5:2c0376dce66844970269876d1e09fea9  very-much-should
adjtimex  1.13 13 adjtimex-1.13-13.src.rpm $tmp_dir/test-repogen/etc/cache/md5/ad/md5:adf064bd5d34ee4522a01fd15176d9b6 md5:adf064bd5d34ee4522a01fd15176d9b6  
apache2  2.0.53 5 apache2_2.0.53-5.dsc $tmp_dir/test-repogen/etc/cache/md5/d9/md5:d94c995bde2f13e04cdd0c21417a7ca5 md5:d94c995bde2f13e04cdd0c21417a7ca5  
apache2-common  2.0.53 5 apache2-common_2.0.53-5_i386.deb $tmp_dir/test-repogen/etc/cache/md5/5a/md5:5acd04d4cc6e9d1530aad04accdc8eb5 md5:5acd04d4cc6e9d1530aad04accdc8eb5 42 

EOF

diff -u control.txt report.txt

# vim:set ai et sw=4 ts=4 tw=75:
