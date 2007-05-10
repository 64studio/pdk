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

# pdk can handle udebs.

cat >expected-discover.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
      <name>discover</name>
      <deb ref="md5:bea537e82e9fcbf345e640caaef95b9a">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>alpha</arch>
      </deb>
      <deb ref="md5:2845009617ffa98d3e8b93713155ecb7">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>arm</arch>
      </deb>
      <deb ref="md5:319fdd581aafdbbbd22e714ea147d7e4">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>hppa</arch>
      </deb>
      <deb ref="md5:b48ce675bc779dd64793601a021b0d66">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:93a5ebbd7f783d41851f2716bba16bb8">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:5c31dd8e1760967c3e16d791590bfcaa">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>m68k</arch>
      </deb>
      <deb ref="md5:aaed2efe840695731fb97dc3641f1907">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>mips</arch>
      </deb>
      <deb ref="md5:18d887eac44cf346f652b8e6c01c91ec">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>mipsel</arch>
      </deb>
      <deb ref="md5:105a7570c0a1d7b43ae6fc1861e73f36">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>powerpc</arch>
      </deb>
      <deb ref="md5:3ed664aca47ff31bdc92b237c97a39b1">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>s390</arch>
      </deb>
      <deb ref="md5:ee77b9cb8e4c2858ea86b82db647fa63">
        <name>discover</name>
        <version>2.0.7-2.1</version>
        <arch>sparc</arch>
      </deb>
      <deb ref="md5:dcb568879d79b7cbf6e2b38d61404b11">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>alpha</arch>
      </deb>
      <deb ref="md5:da2bf3ff3af479a654a64bac3f93247b">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>arm</arch>
      </deb>
      <deb ref="md5:8c0f26f1448ad9797363819410a9937c">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>hppa</arch>
      </deb>
      <deb ref="md5:484a15641a89edf5601489c92f28cf13">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:1561ce1ea579f2d8b881fe466bfd4766">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:19c9f7c63070d3ceb0be949d923b04d6">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>m68k</arch>
      </deb>
      <deb ref="md5:089b2c009cade5b2a4e0be245f27c081">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>mips</arch>
      </deb>
      <deb ref="md5:856adffbbc69584f68ab8df2cc144e5d">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>mipsel</arch>
      </deb>
      <deb ref="md5:c1c661b487681830d4481333fc64504a">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>powerpc</arch>
      </deb>
      <deb ref="md5:198a06dafe17b2ec6d08a2928086ec72">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>s390</arch>
      </deb>
      <deb ref="md5:89ca876054fb502b42a5ae107963475d">
        <name>libdiscover-dev</name>
        <version>2.0.7-2.1</version>
        <arch>sparc</arch>
      </deb>
      <deb ref="md5:165280276b567f778933c392771a7c4b">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>alpha</arch>
      </deb>
      <deb ref="md5:4e844869832c9458daca51d29f103c71">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>arm</arch>
      </deb>
      <deb ref="md5:05db206d13b9864904fd1efc702cf3c2">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>hppa</arch>
      </deb>
      <deb ref="md5:2baead1595c11a4a44c170285d939035">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:b6db49c627f1ee258ec9c260be75e213">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:796a624c7d8ce4eabf596ad91e8cb267">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>m68k</arch>
      </deb>
      <deb ref="md5:b27f3488048ab51cc35a4185a630f376">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>mips</arch>
      </deb>
      <deb ref="md5:0b22625b9ade25b4f8c346597c504993">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>mipsel</arch>
      </deb>
      <deb ref="md5:77995d450a9d2ebde97aa510df1d688f">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>powerpc</arch>
      </deb>
      <deb ref="md5:a787e38669caa7a4db27fc9ef9745903">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>s390</arch>
      </deb>
      <deb ref="md5:3ef965019dcfae25c58aec64651bccde">
        <name>libdiscover2</name>
        <version>2.0.7-2.1</version>
        <arch>sparc</arch>
      </deb>
      <udeb ref="md5:4a16dbbae4754ee2ed073a9ec6802a51">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>alpha</arch>
      </udeb>
      <udeb ref="md5:fe39e6a0c5deb1dac7525e82cfa073d6">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>arm</arch>
      </udeb>
      <udeb ref="md5:bae14c1a5e8e9f64c65f26d314ba8fbc">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>hppa</arch>
      </udeb>
      <udeb ref="md5:d77e63828102e16040c737087e3fc8a1">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>i386</arch>
      </udeb>
      <udeb ref="md5:894319ca611d76dd7f71c051cffb5158">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>ia64</arch>
      </udeb>
      <udeb ref="md5:bc71ed9a953be08390398e1160d77fff">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>m68k</arch>
      </udeb>
      <udeb ref="md5:3f27fe91d83134676c0d8131055d0999">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>mips</arch>
      </udeb>
      <udeb ref="md5:b1d6ccab7266360c0255023f6109d1d6">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>mipsel</arch>
      </udeb>
      <udeb ref="md5:3728d48947fcc197ab1065750e662d5b">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>powerpc</arch>
      </udeb>
      <udeb ref="md5:6d8884a2ddcbb31d90900718503e3371">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>s390</arch>
      </udeb>
      <udeb ref="md5:339755aad10cac5e5fbb6f5988291f08">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>sparc</arch>
      </udeb>
      <dsc ref="md5:b1fde6241bc84c6bde5ce9172465142c">
        <name>discover</name>
        <version>2.0.7-2.1</version>
      </dsc>
    </dsc>
  </contents>
</component>
EOF

cat >expected-discover-udeb-only.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <udeb>
      <name>discover-udeb</name>
      <udeb ref="md5:4a16dbbae4754ee2ed073a9ec6802a51">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>alpha</arch>
      </udeb>
      <udeb ref="md5:fe39e6a0c5deb1dac7525e82cfa073d6">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>arm</arch>
      </udeb>
      <udeb ref="md5:bae14c1a5e8e9f64c65f26d314ba8fbc">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>hppa</arch>
      </udeb>
      <udeb ref="md5:d77e63828102e16040c737087e3fc8a1">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>i386</arch>
      </udeb>
      <udeb ref="md5:894319ca611d76dd7f71c051cffb5158">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>ia64</arch>
      </udeb>
      <udeb ref="md5:bc71ed9a953be08390398e1160d77fff">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>m68k</arch>
      </udeb>
      <udeb ref="md5:3f27fe91d83134676c0d8131055d0999">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>mips</arch>
      </udeb>
      <udeb ref="md5:b1d6ccab7266360c0255023f6109d1d6">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>mipsel</arch>
      </udeb>
      <udeb ref="md5:3728d48947fcc197ab1065750e662d5b">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>powerpc</arch>
      </udeb>
      <udeb ref="md5:6d8884a2ddcbb31d90900718503e3371">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>s390</arch>
      </udeb>
      <udeb ref="md5:339755aad10cac5e5fbb6f5988291f08">
        <name>discover-udeb</name>
        <version>2.0.7-2.1</version>
        <arch>sparc</arch>
      </udeb>
      <dsc ref="md5:b1fde6241bc84c6bde5ce9172465142c">
        <name>discover</name>
        <version>2.0.7-2.1</version>
      </dsc>
    </udeb>
  </contents>
</component>
EOF

pdk workspace create test-with-dir-channel
pushd test-with-dir-channel
    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <discover>
    <type>dir</type>
    <path>discover-pkg</path>
  </discover>
</channels>
EOF

    mkdir discover-pkg
    cp $PACKAGES/discover/* discover-pkg

    pdk channel update

    cat >discover.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>discover</dsc>
  </contents>
</component>
EOF

    cat >discover-udeb-only.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <udeb>discover-udeb</udeb>
  </contents>
</component>
EOF

    pdk resolve discover.xml
    pdk resolve discover-udeb-only.xml

    diff -u $tmp_dir/expected-discover.xml discover.xml
    diff -u $tmp_dir/expected-discover-udeb-only.xml discover-udeb-only.xml

    pdk download discover.xml
    pdk repogen discover.xml

    base=repo/dists/discover/main
    grep -q discover-udeb $base/debian-installer/binary-i386/Packages \
        || fail 'discover-udeb should be in debian-installer data.'
    grep -q discover-udeb $base/debian-installer/binary-mips/Packages \
        || fail 'discover-udeb should be in debian-installer data.'
    grep discover-udeb $base/binary-i386/Packages \
        && fail 'discover-udeb should not be with regular binaries.'
    grep discover-udeb $base/binary-mips/Packages \
        && fail 'discover-udeb should not be with regular binaries.'
    grep -q "^Package: discover$" $base/binary-i386/Packages \
        || fail 'discover should still be with regular binaries.'
    grep -q "^Package: discover$" $base/binary-mips/Packages \
        || fail 'discover should still be with regular binaries.'

    grep -q debian-installer repo/dists/discover/Release \
        || fail 'debian-installer files should be in Release'
popd

pdk workspace create test-with-apt-deb-channel
pushd test-with-apt-deb-channel
    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <discover>
    <type>apt-deb</type>
    <path>file://$tmp_dir/test-with-dir-channel/repo/</path>
    <archs>
      alpha arm hppa i386 ia64 m68k mips
      mipsel powerpc s390 sparc source
    </archs>
    <dist>discover</dist>
    <components>main main/debian-installer</components>
  </discover>
</channels>
EOF

    mkdir discover-pkg
    cp $PACKAGES/discover/* discover-pkg

    pdk channel update

    cat >discover.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>discover</dsc>
  </contents>
</component>
EOF

    cat >discover-udeb-only.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <udeb>discover-udeb</udeb>
  </contents>
</component>
EOF

    pdk resolve discover.xml
    pdk resolve discover-udeb-only.xml

    diff -u $tmp_dir/expected-discover.xml discover.xml
    diff -u $tmp_dir/expected-discover-udeb-only.xml discover-udeb-only.xml

    pdk download discover.xml
    pdk repogen discover.xml

popd

# vim:set ai et sw=4 ts=4 tw=75:
