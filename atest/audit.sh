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

# Make sure that pdk audit catches problems.

# get Utility functions
. atest/test_lib.sh
. atest/utils/test_channel.sh

packages=$(pwd)/packages
test_root=$(pwd)
work_root=$(pwd)/audit
cache_base=${work_root}/etc/cache

pdk workspace create audit

#from test_channel.sh
make_channel apache2*.deb apache2*.dsc \
    emacs-defaults*.dsc emacs-defaults*.deb

cd audit

#from test_channel.sh
config_channel

pdk channel update

#note: this will become an effect of the pdk channel command above,
# pdk channel add --dir $PACKAGES progeny.com
mkdir progeny.com

cp ${tmp_dir}/atest/abstract_comps/apache.xml progeny.com
cp ${tmp_dir}/atest/abstract_comps/emacs.xml progeny.com

pdk resolve progeny.com/apache.xml
pdk resolve progeny.com/emacs.xml

pdk download progeny.com/apache.xml progeny.com/emacs.xml

pdk audit progeny.com/apache.xml progeny.com/emacs.xml \
    >pdk_audit.txt || {
    cat pdk_audit.txt
    bail "Early audit did not pass"
}

diff -u - pdk_audit.txt <<EOF
EOF

# Reinstall emacs-defaults without its source.
cat >progeny.com/emacs.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <name>emacs-defaults</name>
      <version>1.1</version>
      <arch>all</arch>
      <deb ref="md5:de0c6608cca3750129e62573d42e5c0a">
        <name>emacs-defaults</name>
        <version>1.1</version>
        <arch>all</arch>
      </deb>
    </deb>
  </contents>
</component>
EOF

# Make one file go AWOL.
CACHE_BASE=${work_root}/cache/
rm $(cachepath 'md5:0d060d66b3a1e6ec0b9c58e995f7b9f7')

# Corrupt a file.
echo asdfasdfadsf >> $(cachepath 'sha-1:b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b')

# Add an unknown file.
echo asdf >${cache_base}/duh

cd ${work_root}
pdk audit progeny.com/apache.xml progeny.com/emacs.xml \
    >pdk_audit.raw.txt && bail 'pdk audit should fail' || status=$?
test "$status" = "1" || bail 'pdk audit should return exit code 1.'
LANG=C sort <pdk_audit.raw.txt >pdk_audit.txt
echo ""

cat > expected.txt <<EOF
('duh',)|('2b00042f7481c7b056c4b410d28f33cf', '7d97e98f8af710c7e7fe703abc8f639e0ee507c4')|not hard linked properly
('sha-1:9f4be3925441f006f8ee2054d96303cdcdac9b0a',)|('0d060d66b3a1e6ec0b9c58e995f7b9f7', '9f4be3925441f006f8ee2054d96303cdcdac9b0a')|not hard linked properly
deb,emacs-defaults,1.1||missing source
duh|('md5:', 'sha-1:')|unknown prefix
duh||checksum mismatch
md5:0d060d66b3a1e6ec0b9c58e995f7b9f7|progeny.com/apache.xml|missing from cache
md5:5acd04d4cc6e9d1530aad04accdc8eb5|md5:3d9189fb30f41480dec2d513dc800a70|checksum mismatch
sha-1:b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b|sha-1:bbf4c316da08357663c706ecd0eec65e7c73a97a|checksum mismatch
EOF

cat pdk_audit.raw.txt
cat pdk_audit.txt

diff -u expected.txt pdk_audit.txt  || bail "unexpected diff results"

# vim:set ai et sw=4 ts=4 tw=75:
