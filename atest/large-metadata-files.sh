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

# Test that pdk can operate on large metadata files in resonable time.
# This isn't asserted in any particular way, but a long run should annoy
# us into keeping the test reasonably fast.

pdk workspace create large-meta

pushd large-meta
    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
   <sarge>
     <type>apt-deb</type>
     <path>file://$PACKAGES/large-metadata-files/</path>
     <archs>amd64 i386 ia64 source</archs>
     <dist>sarge</dist>
     <components>main</components>
   </sarge>
</channels>
EOF

    time pdk channel update
    ls -lh etc/outside-world.cache
    mkdir progeny.com
    cat >progeny.com/hello.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
   <id>hello</id>
   <name>Hello, world!</name>
   <description>
     The hello component produces a familiar, friendly greeting.
   </description>
   <contents>
     <deb>
       <name>hello</name>
       <deb ref="md5:7dee5a121dd08ac8e8c85cf87fa0bbf8">
         <name>hello</name>
         <version>2.1.1-4</version>
         <arch>amd64</arch>
       </deb>
       <deb ref="md5:b9967c4a0491e2567b0d16a8e0b42208">
         <name>hello</name>
         <version>2.1.1-4</version>
         <arch>i386</arch>
       </deb>
       <deb ref="md5:1a1b8df0cbf62d5571d8a0af1628077f">
         <name>hello</name>
         <version>2.1.1-4</version>
         <arch>ia64</arch>
       </deb>
       <dsc ref="md5:6d92a81b5e72c1f178c1285313a328df">
         <name>hello</name>
         <version>2.1.1-4</version>
       </dsc>
     </deb>
   </contents>
</component>
EOF

cat >many.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>3dchess</dsc>
    <dsc>3ddesktop</dsc>
    <dsc>44bsd-rdist</dsc>
    <dsc>6tunnel</dsc>
    <dsc>855resolution</dsc>
    <dsc>9menu</dsc>
    <dsc>9wm</dsc>
    <dsc>a2ps</dsc>
    <dsc>a2ps-perl-ja</dsc>
    <dsc>a52dec</dsc>
    <dsc>aa3d</dsc>
    <dsc>aalib</dsc>
    <dsc>aap</dsc>
    <dsc>aatv</dsc>
    <dsc>abc2ps</dsc>
    <dsc>abcde</dsc>
    <dsc>abcm2ps</dsc>
    <dsc>abcmidi</dsc>
    <dsc>abicheck</dsc>
    <dsc>abind</dsc>
    <dsc>abiword</dsc>
    <dsc>abntex</dsc>
    <dsc>abook</dsc>
    <dsc>aboot</dsc>
    <dsc>aboot-installer</dsc>
    <dsc>aca</dsc>
    <dsc>acct</dsc>
    <dsc>ace</dsc>
    <dsc>ace-of-penguins</dsc>
    <dsc>acepack</dsc>
    <dsc>acfax</dsc>
    <dsc>acheck</dsc>
    <dsc>acheck-rules</dsc>
    <dsc>acheck-rules-fr</dsc>
    <dsc>achilles</dsc>
    <dsc>achims-guestbook</dsc>
    <dsc>acidlab</dsc>
    <dsc>acidwarp</dsc>
    <dsc>ack</dsc>
    <dsc>acl</dsc>
    <dsc>acl2</dsc>
    <dsc>aclock.app</dsc>
    <dsc>acm</dsc>
    <dsc>acm4</dsc>
    <dsc>aconnectgui</dsc>
    <dsc>acorn-fdisk</dsc>
    <dsc>acovea</dsc>
    <dsc>acovea-results</dsc>
    <dsc>acpi</dsc>
    <dsc>acpid</dsc>
    <dsc>ada-mode</dsc>
    <dsc>ada-reference-manual</dsc>
    <dsc>adabrowse</dsc>
    <dsc>adacgi</dsc>
    <dsc>adasockets</dsc>
    <dsc>addresses-for-gnustep</dsc>
    <dsc>adduser</dsc>
    <dsc>adduser-ng</dsc>
    <dsc>adesklets</dsc>
    <dsc>adjtimex</dsc>
    <dsc>admesh</dsc>
    <dsc>adns</dsc>
    <dsc>adolc</dsc>
    <dsc>adtool</dsc>
    <dsc>advi</dsc>
    <dsc>adzapper</dsc>
    <dsc>aee</dsc>
    <dsc>aegis</dsc>
    <dsc>aegis-virus-scanner</dsc>
    <dsc>aeromail</dsc>
    <dsc>aespipe</dsc>
    <dsc>aewan</dsc>
    <dsc>aewm</dsc>
    <dsc>aewm++</dsc>
    <dsc>aewm++-goodies</dsc>
    <dsc>af</dsc>
    <dsc>afbackup</dsc>
    <dsc>affiche</dsc>
    <dsc>affix</dsc>
    <dsc>affix-kernel</dsc>
    <dsc>afio</dsc>
    <dsc>aft</dsc>
    <dsc>afterstep</dsc>
    <dsc>agenda.app</dsc>
    <dsc>aget</dsc>
    <dsc>aggregate</dsc>
    <dsc>agistudio</dsc>
    <dsc>agsync</dsc>
    <dsc>aide</dsc>
    <dsc>aiksaurus</dsc>
    <dsc>aime</dsc>
    <dsc>aime-doc</dsc>
    <dsc>aircrack</dsc>
    <dsc>airsnort</dsc>
    <dsc>airstrike</dsc>
    <dsc>aish</dsc>
    <dsc>akregator</dsc>
    <dsc>aladin</dsc>
    <dsc>alamin</dsc>
    <dsc>albatross</dsc>
  </contents>
</component>
EOF

    time pdk download progeny.com/hello.xml
    time pdk resolve many.xml
    time pdk upgrade many.xml

popd

# vim:set ai et sw=4 ts=4 tw=75:
