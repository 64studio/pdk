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

# Check that the available test data is up to date.  Also check that the
# required software is available.

(cd packages && find * -type f | xargs openssl sha1) \
    | LANG=C sort >catalog.txt
diff -u - catalog.txt <<EOF
SHA1(abook_0.5.3-2.diff.gz)= 4f069d2b926621964216125a1cce4ece213f177e
SHA1(abook_0.5.3-2.dsc)= c585ffdbf641a6f4d5d895314af2826a0a4421c0
SHA1(abook_0.5.3-2_s390.deb)= d4ac2bfffd4c06dda613c32293b8cf5c9dcb102b
SHA1(abook_0.5.3.orig.tar.gz)= a6c4b7f9d25f3f0b0a67d0ffb0456a0e19018e8f
SHA1(adjtimex-1.13-12.i386.rpm)= 02ac15163b67c7af4b1b188b5015e6fdef2ca871
SHA1(adjtimex-1.13-12.src.rpm)= 42013a0008921e9b344cc07823392fbbc4ec080d
SHA1(adjtimex-1.13-13.i386.rpm)= 519da15c87652669b707ab49e2a6294d7aea1c1f
SHA1(adjtimex-1.13-13.src.rpm)= 5f5e2555c8294e68d06bf61aad10daa05dca2516
SHA1(apache2-common_2.0.53-5_i386.deb)= b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b
SHA1(apache2_2.0.53-5.diff.gz)= 9f4be3925441f006f8ee2054d96303cdcdac9b0a
SHA1(apache2_2.0.53-5.dsc)= 9d26152e78ca33a3d435433c67644b52ae4c670c
SHA1(apache2_2.0.53.orig.tar.gz)= 214867c073d2bd43ed8374c9f34fa5532a9d7de0
SHA1(centos-release-4-1.2.i386.rpm)= 664bad7feb664492d9bdb497528db590dcd9021b
SHA1(ddetect/archdetect_1.14_alpha.udeb)= 31667caec2d7caf28425720f200e0d1d654427c1
SHA1(ddetect/archdetect_1.14_arm.udeb)= 0c9a98329e9c943381bec1e604921e6b26265459
SHA1(ddetect/archdetect_1.14_hppa.udeb)= b5830631cbb79d3af317cbb562f720dc532d4b54
SHA1(ddetect/archdetect_1.14_i386.udeb)= 6c0205608f16bc6c91c0761a224af1861fd2ef05
SHA1(ddetect/archdetect_1.14_ia64.udeb)= 196eeac71ad64b9cb7392c0f8d833651b52b34ca
SHA1(ddetect/archdetect_1.14_m68k.udeb)= 046457c62be9e06f84aaa5714e3872b30310718b
SHA1(ddetect/archdetect_1.14_mips.udeb)= 0d59cfc8a57f63c4b8d67df2354d22881901f367
SHA1(ddetect/archdetect_1.14_mipsel.udeb)= 088d05a5c56dcd95b7c0036417df0027f2b6dabe
SHA1(ddetect/archdetect_1.14_powerpc.udeb)= 37886969c7f06e37585a030ad2296dec092a05d4
SHA1(ddetect/archdetect_1.14_s390.udeb)= 02d9335d30ff873992b2e490036c2d82b3b83d13
SHA1(ddetect/archdetect_1.14_sparc.udeb)= fbd6f10de415fc4f646b09558e0cb5d6f7b38d9c
SHA1(ddetect/ddetect_1.14.dsc)= aa940c9de4b2df7efa520c3780237f3316e3dd72
SHA1(ddetect/ddetect_1.14.tar.gz)= 062ff9f5cea3ef59f4859c6851321c211d591ce7
SHA1(ddetect/ethdetect_1.14_all.udeb)= 1e4ff13a8411b925f09969d72bc57a1b71ce2e73
SHA1(ddetect/hw-detect-full_1.14_all.udeb)= dad7eeabfec2f6818fb36d0b4f881e6b61a95052
SHA1(ddetect/hw-detect_1.14_alpha.udeb)= 5b297747135f81015c0a741c220f5cbe00048e2e
SHA1(ddetect/hw-detect_1.14_arm.udeb)= 8b5a35dad4989e7c919179bb10bb78d41281eb7e
SHA1(ddetect/hw-detect_1.14_hppa.udeb)= a133ae0ec7a22b21bf386983693409380b0180b5
SHA1(ddetect/hw-detect_1.14_i386.udeb)= 6bb0bb35fa37f352536b0e123f37467c618e6daf
SHA1(ddetect/hw-detect_1.14_ia64.udeb)= aadcbfc2f89dbd1735595caf629a021db4cc7387
SHA1(ddetect/hw-detect_1.14_m68k.udeb)= 9aea2da7cf49f0dfc39f6de3103ac7e6940234cf
SHA1(ddetect/hw-detect_1.14_mips.udeb)= 109abd281bbacc858b64905b92cd04595cbab61d
SHA1(ddetect/hw-detect_1.14_mipsel.udeb)= 41f95a9616f12090f612161dd0842357194f4f23
SHA1(ddetect/hw-detect_1.14_powerpc.udeb)= a42cbbe66ca5d19e3d5be1fafa226f6f29bdbee1
SHA1(ddetect/hw-detect_1.14_s390.udeb)= 8d4a3999e9b65ce5a829a0517b508ddc4c70c39c
SHA1(ddetect/hw-detect_1.14_sparc.udeb)= eae278afc85aaff69dd4c9af93644fe922b5f10a
SHA1(discover/discover-udeb_2.0.7-2.1_alpha.udeb)= 205b0cb9ebd350b78cba275d3aaba064867e4500
SHA1(discover/discover-udeb_2.0.7-2.1_arm.udeb)= 4e3070c28d4b511a4ccc30a3f679fc664b19f181
SHA1(discover/discover-udeb_2.0.7-2.1_hppa.udeb)= dd219775694cb2ff2269830eac0ec60d52d97066
SHA1(discover/discover-udeb_2.0.7-2.1_i386.udeb)= 60380ed45b9db43b4d120d08bb395ccd4126035e
SHA1(discover/discover-udeb_2.0.7-2.1_ia64.udeb)= 7e1bcc93526fca55d01e60d08cb4e24d45172036
SHA1(discover/discover-udeb_2.0.7-2.1_m68k.udeb)= ca7f70f24a25e5beb730e21b54d9321bb605b3e3
SHA1(discover/discover-udeb_2.0.7-2.1_mips.udeb)= 47f9ccd7366c176648f1fea4d15dbca6b540c9f4
SHA1(discover/discover-udeb_2.0.7-2.1_mipsel.udeb)= 013c30387419a8ea8174453e47ce2801873a519a
SHA1(discover/discover-udeb_2.0.7-2.1_powerpc.udeb)= 6a41dbccb55b5daf0af0ce5b81ffe39b8b725050
SHA1(discover/discover-udeb_2.0.7-2.1_s390.udeb)= 15e49d6ce91a8d6c8ab4ed6237eb99807833c40c
SHA1(discover/discover-udeb_2.0.7-2.1_sparc.udeb)= ad21b380d01a119b55d2e7a295a14707bcb49726
SHA1(discover/discover_2.0.7-2.1.diff.gz)= e30c402ab34a4dd9fc9a7e5aa164dc57ddeb44ae
SHA1(discover/discover_2.0.7-2.1.dsc)= 6239400144e4f4fcf89d476c44a1b6795a5857e5
SHA1(discover/discover_2.0.7-2.1_alpha.deb)= 0a06c901a40c57ce868d8cbc7c0e1f798ac1c65e
SHA1(discover/discover_2.0.7-2.1_arm.deb)= 6b9088922c961953e5aa02b9d404e19508d03713
SHA1(discover/discover_2.0.7-2.1_hppa.deb)= 159b1948501188e5a11bd065a9b10de51e96f818
SHA1(discover/discover_2.0.7-2.1_i386.deb)= 9d85fb240f097ef1ee07f84aad9c48e4fe286e71
SHA1(discover/discover_2.0.7-2.1_ia64.deb)= a8574a789b9df13d40cd0116df9287f7b7d6647c
SHA1(discover/discover_2.0.7-2.1_m68k.deb)= 612d3f2947f5f2ec7e15001c38277c11e8058602
SHA1(discover/discover_2.0.7-2.1_mips.deb)= 7811baa1fa4fa610020688c8dd2208c5d9d21eb4
SHA1(discover/discover_2.0.7-2.1_mipsel.deb)= 9de1a8ba08049ede29748eb356d79cf150dad5d8
SHA1(discover/discover_2.0.7-2.1_powerpc.deb)= fe5ca1a63af62f8d4c3b956b461e79c602208b83
SHA1(discover/discover_2.0.7-2.1_s390.deb)= 3037825da6772c33c1bd5607da328b740d76f9e3
SHA1(discover/discover_2.0.7-2.1_sparc.deb)= 887ea11e165520223d3ad035e12e6435c8597237
SHA1(discover/discover_2.0.7.orig.tar.gz)= bd18ac1b93408b670e97fd163f25fb3c21b92952
SHA1(discover/libdiscover-dev_2.0.7-2.1_alpha.deb)= 0639ab8edfafd0b7e7a69a6d91086922494c4c37
SHA1(discover/libdiscover-dev_2.0.7-2.1_arm.deb)= 6cd104640646b3256f5b4040a7d770f7e04a9d8e
SHA1(discover/libdiscover-dev_2.0.7-2.1_hppa.deb)= 99b5fd6d6446b76478ddc52f8f62250fa068063a
SHA1(discover/libdiscover-dev_2.0.7-2.1_i386.deb)= 535c48e76ea81c094ff99aaeca0a103c9d53d897
SHA1(discover/libdiscover-dev_2.0.7-2.1_ia64.deb)= 39e4e5a1d2cc6ed56954958aa60f703e4f5496fe
SHA1(discover/libdiscover-dev_2.0.7-2.1_m68k.deb)= 8385ddafb17098739219b990708be56e0c23b827
SHA1(discover/libdiscover-dev_2.0.7-2.1_mips.deb)= b7b2b9de863d2200791563027325522aa9b6ef45
SHA1(discover/libdiscover-dev_2.0.7-2.1_mipsel.deb)= 53b1039286277bbc71ef46ae9464451daaf74076
SHA1(discover/libdiscover-dev_2.0.7-2.1_powerpc.deb)= e96319a0521d5130895d3a1525dd853d51c514fd
SHA1(discover/libdiscover-dev_2.0.7-2.1_s390.deb)= 1890609354230a433bf5a443417429a6defee418
SHA1(discover/libdiscover-dev_2.0.7-2.1_sparc.deb)= 964f791b59ab943cf06e4fdf12a0696fa5d0812e
SHA1(discover/libdiscover2_2.0.7-2.1_alpha.deb)= 48b5493dbf0255fcee3eb205076226deb5ea40ec
SHA1(discover/libdiscover2_2.0.7-2.1_arm.deb)= 029640e277d41f0df8f02f3eff1e4e9a54f6b590
SHA1(discover/libdiscover2_2.0.7-2.1_hppa.deb)= a425bec9afd8ddcef135cbf4c380b4d826fdd9d9
SHA1(discover/libdiscover2_2.0.7-2.1_i386.deb)= 85e580d1c4dad388aa7100df999e28f277167f33
SHA1(discover/libdiscover2_2.0.7-2.1_ia64.deb)= 6217b7ad6c3d059c292c6df4ce6e3cc9db1d324e
SHA1(discover/libdiscover2_2.0.7-2.1_m68k.deb)= 1c9e2c2606585ce937e6245e370415cb9705b42c
SHA1(discover/libdiscover2_2.0.7-2.1_mips.deb)= bc3c38378ae036cb4f31a82b58c861b9d4b218df
SHA1(discover/libdiscover2_2.0.7-2.1_mipsel.deb)= a9434c53e576443aeb8e879a659b2ca68dabfdac
SHA1(discover/libdiscover2_2.0.7-2.1_powerpc.deb)= 8158b047e9f3317067997057979492dc0dad5b36
SHA1(discover/libdiscover2_2.0.7-2.1_s390.deb)= c6b082cd3558fe3f0c40b6125b31c339e44655d4
SHA1(discover/libdiscover2_2.0.7-2.1_sparc.deb)= 512ca5395d1e40987e312e37b7d46f8a99fff97e
SHA1(emacs-defaults_1.1.dsc)= 9f4468e5a0f9a99df82083ba856483ba66f007a8
SHA1(emacs-defaults_1.1.tar.gz)= 9ec95718a49fd7f1a8a745c3673b5386349f3f77
SHA1(emacs-defaults_1.1_all.deb)= 95155bda2cb225f94401e6f82ec3261f094111f0
SHA1(ethereal-common_0.9.13-1.0progeny1_ia64.deb)= be25deecace20fc2a0dfc46af08e366e8b1e4ad9
SHA1(ethereal-common_0.9.13-1.0progeny2_ia64.deb)= 9ca2ad70d846b739ee43532f6727ee2b341d23b9
SHA1(ethereal-common_0.9.4-1woody2_i386.deb)= f886a14e62bb7b54b860881690945ccfbbf0efa8
SHA1(ethereal-common_0.9.4-1woody2_ia64.deb)= f0aaf2b11c324a0988fc843e1180185c67d0afcc
SHA1(ethereal-common_0.9.4-1woody3_i386.deb)= 0f9669e90b350e5a5e5174ab1c13920999d100db
SHA1(ethereal-common_0.9.4-1woody3_ia64.deb)= 51e3e5df292057a78f961d759cbdc51f91f76b5f
SHA1(ethereal-common_0.9.4-1woody4_i386.deb)= aec67968dfb60398ebe7ca1ea67f5590bf5cddfe
SHA1(ethereal-common_0.9.4-1woody4_ia64.deb)= b423fe0986766fcfcbb6179c76998fb67706d693
SHA1(ethereal-common_0.9.4-1woody5_i386.deb)= 34ed86e39369c8dc0f37d006c1891c476b7f2b60
SHA1(ethereal-common_0.9.4-1woody5_ia64.deb)= 1b0303d6fb110647362219668081ecec346f866b
SHA1(ethereal-common_0.9.4-1woody6_i386.deb)= f954ea9d9857d5ab6e6f469bcd815bd88d5aa13c
SHA1(ethereal-common_0.9.4-1woody6_ia64.deb)= 51c0b857913b43469610d888e59ee7b71f9ea997
SHA1(ethereal-dev_0.9.13-1.0progeny1_ia64.deb)= 3e331cba9cd69417e174dbf2c7313845794f9cdb
SHA1(ethereal-dev_0.9.13-1.0progeny2_ia64.deb)= 9fca9287fa2d59fe7e723ec81892194e621999ab
SHA1(ethereal-dev_0.9.4-1woody2_i386.deb)= 28ab50857371288e291203d3e1fd066befbf438b
SHA1(ethereal-dev_0.9.4-1woody2_ia64.deb)= 4a6561816968bc4ff9268aeeea8da7d80326ec55
SHA1(ethereal-dev_0.9.4-1woody3_i386.deb)= b0d5bfdc595bfa6367e845afb796c7e349db505b
SHA1(ethereal-dev_0.9.4-1woody3_ia64.deb)= 440a267d95e691d4a77dcddd5e15065b2b9bff48
SHA1(ethereal-dev_0.9.4-1woody4_i386.deb)= f7d28d6410145f7772478f71bdacee92acdf5603
SHA1(ethereal-dev_0.9.4-1woody4_ia64.deb)= 45362dd9444134fff8ae079124cd95bc18debe91
SHA1(ethereal-dev_0.9.4-1woody5_i386.deb)= e66edc893c759f96703139a9c9d64d5a93e734ed
SHA1(ethereal-dev_0.9.4-1woody5_ia64.deb)= 8e008adecd3dea3cfec59e65c56d27739afc9a8f
SHA1(ethereal-dev_0.9.4-1woody6_i386.deb)= cb3e75189c65eabd80934ab03687ba6f34dea03a
SHA1(ethereal-dev_0.9.4-1woody6_ia64.deb)= 98dc6e90f6df487deac9224ea2ba75aaf386fa7a
SHA1(ethereal_0.9.13-1.0progeny1.diff.gz)= 3c9d1bf57d723ec1d11d55c0b7f5f9d170295d45
SHA1(ethereal_0.9.13-1.0progeny1.dsc)= 5d6449397b815b214b7f40c4ba138368be7069c9
SHA1(ethereal_0.9.13-1.0progeny1_ia64.deb)= 9683e93170a1c7459147d86605e72346b212c791
SHA1(ethereal_0.9.13-1.0progeny2.diff.gz)= e883c53c585557c99d9eb2c31465303493aee39a
SHA1(ethereal_0.9.13-1.0progeny2.dsc)= 726bd9340f8b72a2fbf7e4b70265b56b125e525d
SHA1(ethereal_0.9.13-1.0progeny2_ia64.deb)= 9a264269606ea451c762eeb91f3f0e68db447887
SHA1(ethereal_0.9.13.orig.tar.gz)= 88a7160a1bfe9b6e8d2438b1822ba53c89b3990a
SHA1(ethereal_0.9.4-1woody2.diff.gz)= a96b06273a623ccf8f781b8d6d208bc4d763457f
SHA1(ethereal_0.9.4-1woody2.dsc)= ea00a60a3340c614dc603601e60309a4498e6fb0
SHA1(ethereal_0.9.4-1woody2_i386.deb)= ce6649092d875819a04362d005c6657349d6b59d
SHA1(ethereal_0.9.4-1woody2_ia64.deb)= b8a3dd9a19e9b548f843986a336650fcb6f7a061
SHA1(ethereal_0.9.4-1woody3.diff.gz)= 559fb3fb124dea661a56c75a5ba2575cc3f545cf
SHA1(ethereal_0.9.4-1woody3.dsc)= a2d332a1ef554459e33295768392d213144478ef
SHA1(ethereal_0.9.4-1woody3_i386.deb)= bf05309448b42b6b2f5f3b16e996266d9555eabb
SHA1(ethereal_0.9.4-1woody3_ia64.deb)= 3b5e62b8b71505f56a6251c7cefc17b4a78bac57
SHA1(ethereal_0.9.4-1woody4.diff.gz)= 6a6e1af69c365a4558ae36b225262f4b80e1bf9c
SHA1(ethereal_0.9.4-1woody4.dsc)= 0ff48db2ccfcb0fe67bd1792f6d8299fdb5001ab
SHA1(ethereal_0.9.4-1woody4_i386.deb)= 2a3854d8c1c9aa674421df79c067fc328f15f016
SHA1(ethereal_0.9.4-1woody4_ia64.deb)= 0c49d6dcbdbad58556c3d6b6b77f25f25384ac03
SHA1(ethereal_0.9.4-1woody5.diff.gz)= b65361b328f2b4d06083247e351838bd4d5a0e4f
SHA1(ethereal_0.9.4-1woody5.dsc)= 33b088f120bcfc79fe88b38d46291c87772d3588
SHA1(ethereal_0.9.4-1woody5_i386.deb)= fdc64ffee8337ab1c9b2f6791d59101a940307de
SHA1(ethereal_0.9.4-1woody5_ia64.deb)= 47228d5bea5dd9c80ab545407534c325656728ca
SHA1(ethereal_0.9.4-1woody6.diff.gz)= 424e1ee6dd1b43fd359e13ede18a3a451cf7a637
SHA1(ethereal_0.9.4-1woody6.dsc)= 6f60a42ff7f498014d31e99f376cf8ce80c7d8c6
SHA1(ethereal_0.9.4-1woody6_i386.deb)= 409f381945676afcbb183c2fadf35c47d5660f20
SHA1(ethereal_0.9.4-1woody6_ia64.deb)= 62ededcc960a3ff55f989cb5a4885148cae3373c
SHA1(ethereal_0.9.4.orig.tar.gz)= c2582bf4ae8432f076c73e4d781146ef928a1032
SHA1(gcc-defaults_1.30.dsc)= 6c9ec1d163487260bcba3f0c3fc0356798c2cb8b
SHA1(gcc-defaults_1.30.tar.gz)= ecba06b2c078631c033f4071c8456a9284cef5f9
SHA1(gcc_4.0.2-2_i386.deb)= de319422a903b979c206f25e582020fae5a1e0b1
SHA1(gtk-engines-industrial_0.2.36.4_i386.deb)= 3c59b72760e3f0aa5cb2c0b7c9f4bd21d99d7148
SHA1(gtk-industrial-engine_0.2.36.4.dsc)= 699f36155ba0871f82ab82dea58ab0d737b3e5fc
SHA1(gtk-industrial-engine_0.2.36.4.tar.gz)= 50cc4a985be03c06676ad19c5f6e81b70034a253
SHA1(ida_2.01-1.2.diff.gz)= 48c0c56acbeb90f06be38da82f194c63d937b9a8
SHA1(ida_2.01-1.2.dsc)= 5758b8cd6b604e872d60a257777cc9d3018c84c8
SHA1(ida_2.01-1.2_arm.deb)= a5b9ebe5914fa4fa2583b1f5eb243ddd90e6fbbe
SHA1(ida_2.01.orig.tar.gz)= 000874ad1e2bbf975b5eb157e8d2e4dbe87cb006
SHA1(kerberos4kth-dev_1.2.2-11.1_i386.deb)= aa98f6d7eff08f9c94296defa3e8915798014699
SHA1(large-metadata-files/dists/sarge/main/binary-amd64/Packages.gz)= 34f856436ace3ffa5546dc108a617232653c2075
SHA1(large-metadata-files/dists/sarge/main/binary-i386/Packages.gz)= 6ac6dd51b0943b99d422550d111c9d17e5be2f47
SHA1(large-metadata-files/dists/sarge/main/binary-ia64/Packages.gz)= 5f09f9aacc1494fbadf61dff91a2c69e591868ce
SHA1(large-metadata-files/dists/sarge/main/source/Sources.gz)= a72b740ea99d341d5bf43471ff4e66d19921def2
SHA1(large-metadata-files/pool/main/h/hello-debhelper/hello-debhelper_2.1.1.orig.tar.gz)= e213c508d307e9d67f4eb2c2d075532d7dd8aa8b
SHA1(large-metadata-files/pool/main/h/hello/hello_2.1.1-4.diff.gz)= 6c7509355ae0d997a8c138b19cb6b56e065ba7e3
SHA1(large-metadata-files/pool/main/h/hello/hello_2.1.1-4.dsc)= c6d833b5bd79f68d8255aac64197e6f4a4211e6c
SHA1(large-metadata-files/pool/main/h/hello/hello_2.1.1-4_amd64.deb)= cde3cdda7f24323f35f8fc44329a230765cb457e
SHA1(large-metadata-files/pool/main/h/hello/hello_2.1.1-4_i386.deb)= dbb91d7638b890693d61f933d53106d1cdf1f428
SHA1(large-metadata-files/pool/main/h/hello/hello_2.1.1-4_ia64.deb)= 698c904d05236e23438a65e6766f1cb7280c204b
SHA1(large-metadata-files/pool/main/h/hello/hello_2.1.1.orig.tar.gz)= e213c508d307e9d67f4eb2c2d075532d7dd8aa8b
SHA1(libapache-mod-ssl-doc_2.8.22-1_all.deb)= 283c47003e6c4277a2a9393b89086b026d5353f7
SHA1(mount_2.12p-4_amd64.deb)= fc41168234980b578e511887658b76dd43f6746b
SHA1(mount_2.12p-4sarge1_amd64.deb)= 7b78ae62799b141fb1b5ce538cdd711b04972757
SHA1(nosrc-test-1-1.i386.rpm)= a8580963983466c18fb19c36be7ffca2e00cfa25
SHA1(nosrc-test-1-1.nosrc.rpm)= f5eb0e1eac97cb1c6178fd759c4d17efaf224183
SHA1(passwd-0.68-10.i386.rpm)= ee009700fc1e49b48b299dbc8edd2793310a9a9e
SHA1(python-defaults_2.3.3-6.dsc)= ff9e54736ff8bb385c053a006c3a550c8f20674c
SHA1(python-defaults_2.3.3-6.tar.gz)= 312786f3e9946e9bd52667e379d1d59b58f4426a
SHA1(python-defaults_2.3.5-2.dsc)= baf7a3b88f2a542205c8c03643651873da1f8ca3
SHA1(python-defaults_2.3.5-2.tar.gz)= 014a8dd7fbbb65be9d3b21a6d765875d9717d34b
SHA1(python_2.3.3-6_all.deb)= 6d7cf6eeaa67da461a35ebfba9351a7c1a7720eb
SHA1(python_2.3.5-2_all.deb)= 73ff2f8176e703be1946b6081386193afb25c620
SHA1(tethereal_0.9.13-1.0progeny1_ia64.deb)= 0de6b9634732b7c44e5bae0afb6667425c1d271c
SHA1(tethereal_0.9.13-1.0progeny2_ia64.deb)= 67920db12b0097c88619f80d9de2ce07fd7d1558
SHA1(tethereal_0.9.4-1woody2_i386.deb)= bcdca94c60da3fbe50517f0e931abda810f611ec
SHA1(tethereal_0.9.4-1woody2_ia64.deb)= d321ebb423c6f8464d81f7bb1aa8f8e438c91dad
SHA1(tethereal_0.9.4-1woody3_i386.deb)= d038af8d769c0038bb9ae06072a845ba0fc3a42a
SHA1(tethereal_0.9.4-1woody3_ia64.deb)= c665753ed99efb828bfe808c4d467321eb7a606d
SHA1(tethereal_0.9.4-1woody4_i386.deb)= f2226b632b6e75e22ac3685ef416ff6b5cb5917d
SHA1(tethereal_0.9.4-1woody4_ia64.deb)= d477ac16a219950c483e76a2b713a459f9efaf1d
SHA1(tethereal_0.9.4-1woody5_i386.deb)= e523bac517dbd67dc4a6b04df471bfec0ae236f8
SHA1(tethereal_0.9.4-1woody5_ia64.deb)= 6ab156568134bfada1f76f8029f8dc266fb33174
SHA1(tethereal_0.9.4-1woody6_i386.deb)= 53acfadd4a67105669e1f2a7cc69fdcb8e16ebd5
SHA1(tethereal_0.9.4-1woody6_ia64.deb)= 1623e22c9bc0557ac615208c64a3b3e687be449d
SHA1(util-linux_2.12p-4.diff.gz)= 7775662cdf9ff535839258751815cda484eb3c5e
SHA1(util-linux_2.12p-4.dsc)= 70ce7b988391f42a327195d254e2486c580423b1
SHA1(util-linux_2.12p-4_amd64.deb)= e3c390c1c5074494d8fa33fd6a45e3a75f07ab64
SHA1(util-linux_2.12p-4sarge1.diff.gz)= 9fcb638eca31cb95b6dcf4956502be5993e08a0d
SHA1(util-linux_2.12p-4sarge1.dsc)= e1350a8c8c1b4044e433d5a4eb15189e4a169707
SHA1(util-linux_2.12p-4sarge1_amd64.deb)= df338591bd24972043c8e2b2a03533646f6b8b25
SHA1(util-linux_2.12p.orig.tar.gz)= 9c9919a3d34bd5ff1f8d9c74700ac8682caff3dd
SHA1(xsok_1.02-9.diff.gz)= 175b0791f232eb5b6365a6f5f0b49f7a4fb53697
SHA1(xsok_1.02-9.dsc)= eafa977d05f949c72071aa08560286cfd67ed47a
SHA1(xsok_1.02-9_i386.deb)= 1b6e276bb7addccccefe2476915559f50c535e3b
SHA1(xsok_1.02-9_ia64.deb)= a8c30a9b47947144e31c890d3c800747e237c28c
SHA1(xsok_1.02-9woody2.diff.gz)= 166bd86840469d06eba4a93da33aaf2e47a10e93
SHA1(xsok_1.02-9woody2.dsc)= 689ea93800891a1c6bde52901c066a9e95a07f21
SHA1(xsok_1.02-9woody2_i386.deb)= 344d8008d9380d5a8df10eeed76664e4eb8d90e5
SHA1(xsok_1.02-9woody2_ia64.deb)= ccb1749f9055511f1be9fab4d7081c4b51387d42
SHA1(xsok_1.02.orig.tar.gz)= beac1309aeddff5f15148879de766289a68dd2f6
EOF

# test python modules
for module in pycurl xml.sax.saxutils apt_pkg rpm
do
  python -c "import ${module}" || fail "could not import ${module}"
done

# test required programs
for program in git
do
  which ${program} || fail "could not find program ${program}"
done

# vim:set ai et sw=4 ts=4 tw=75:
