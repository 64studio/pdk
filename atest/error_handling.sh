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

. atest/test_lib.sh

set_up() {
    message="$1"
    expected_error="$2"
    status="(missing or zero status!)"
    echo "test: $message"
    pdk workspace create error-handling
    pushd error-handling
}

tear_down() {
    [ -e errors.txt ] && cat errors.txt
    [ "$status" = $expected_error ] \
        || fail "$message [ $expected_error $status ]"
    popd
    rm -rf error-handling
}


set_up "Ill-formed command line - semdiff" 2
pdk semdiff  || status=$?
tear_down

set_up "Ill-formed command line - resolve" 2
pdk resolve || status=$?
tear_down

set_up "Ill-formed command line - channel update" 2
pdk channel update z || status=$?
tear_down

set_up "Ill-formed command line - download" 2
pdk download || status=$?
tear_down

set_up "Working with missing components is an error." 3
cat >exists.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <component>doesnt-exist.xml</component>
  </contents>
</component>
EOF
pdk repogen exists.xml 2>errors.txt || status=$?
grep -i exist errors.txt \
    || { cat errors.txt;
         fail "The word exist should appear in error."; }
tear_down

set_up "Process ill-formed channels file" 3
cat > etc/channels.xml << EOF
<?xml version="1.0"?>
<channels>
  <blow-up-here>
</channels>
EOF
pdk channel update || status=$?
tear_down

set_up "Need to update channel data." 4
cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <remote>
    <type>apt-deb</type>
    <path>http://localhost/</path>
    <archs>arm i386 source</archs>
    <dist>apache</dist>
    <components>main</components>
  </remote>
</channels>
EOF
cat >empty.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>apache2</dsc>
  </contents>
</component>
EOF
pdk resolve empty.xml || status=$?
tear_down


set_up "Process even worse ill-formed (non)XML" 3
cat > etc/channels.xml << EOF
not ex emm ell at all
EOF
pdk channel update || status=$?
tear_down

set_up "Bad path in apt-deb channel" 3
cat > etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <foo>
    <type>apt-deb</type>
    <path>http://example.com/bar</path>
    <archs>i386 source</archs>
    <dist>foo</dist>
    <components>main</components>
  </foo>
</channels>
EOF
pdk channel update || status=$?
tear_down

set_up "Process an ill-formed component descriptor" 3
cat > bad_component.xml << EOF
<?xml version="1.0"?>
EOF
pdk semdiff ./bad_component.xml ./bad_component.xml  || status=$?
tear_down

set_up "Process a more reasonable ill-formed component descriptor" 3
cat > ethereal.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc ref="sha-1:726bd9340f8b72a2fbf7e4b70265b56b125e525d">
      <name>ethereal</name>
      <version>0.9.13-1.0progeny2</version>
    </dsc>

</component>
EOF
pdk semdiff ethereal.xml ethereal.xml || status=$?
tear_down

set_up "Cache miss" 4
cat > cache-miss.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb ref="sha-1:cantpossiblyexist"/>
  </contents>
</component>
EOF

pdk semdiff cache-miss.xml empty.xml || status=$?
tear_down

set_up "Download non-existent package from channel" 4
cat > cache-miss.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb ref="sha-1:cantpossiblyexist"/>
  </contents>
</component>
EOF
cat > etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <foo>
    <type>dir</type>
    <path>.</path>
  </foo>
</channels>
EOF
pdk channel update
pdk download cache-miss.xml || status=$?
tear_down

set_up "Use nonexistant channel" 3
cat > component.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb/>
  </contents>
</component>
EOF

cat > etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <foo>
    <type>dir</type>
    <path>.</path>
  </foo>
</channels>
EOF
pdk channel update
pdk resolve component.xml -c bar || status=$?
tear_down

set_up "repogen an empty component" 3
cat > empty.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
  </contents>
</component>
EOF

pdk repogen empty.xml || status=$?
tear_down

set_up "push with no upstream name" 2
pdk push || status=$?
tear_down

set_up "pull with no upstream name" 2
pdk pull || status=$?
tear_down

# vim:set ai et sw=4 ts=4 tw=75:
