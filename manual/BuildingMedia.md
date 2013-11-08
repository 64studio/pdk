To build up installation media you can use the `mediagen` command. First of all you have to add some meta information to your `mylinux.xml` descriptor, like where to find the boot images, which label to use for the media, and so on. This can be done by adding a `<meta>` xml block with the proper options. Here's an example of the modified `mylinux.xml`:

	
	<?xml version="1.0" encoding="utf-8"?>
	<component>
	  <id>hardy</id>
	  <meta>
	    <mediagen.media>cd</mediagen.media>
	    <mediagen.media-label>MyLinux 0.1</mediagen.media-label>
	    <mediagen.installer>debian-installer</mediagen.installer>
	    <mediagen.arch>i386</mediagen.arch>
	    <mediagen.inst-preseed-file>file:mypreseed</mediagen.inst-preseed-file>
	    <mediagen.inst-base-url>file:64studio.com/boot/cdrom/</mediagen.inst-base-url>
	    <mediagen.inst-cdrom-path>i386</mediagen.inst-cdrom-path>
	    <mediagen.inst-udeb-include-list>pcmcia-cs-udeb</mediagen.inst-udeb-include-list>
	    <mediagen.repository>hardy:main hardy:main/debian-installer</mediagen.repository>
	    <mediagen.source>none</mediagen.source>
	    <mediagen.no-order>True</mediagen.no-order>
	    <mediagen.no-split>True</mediagen.no-split>
	  </meta>
	  <contents>
	    <component>64studio.com/minimal.xml</component>
	    <component>64studio.com/standard.xml</component>
	    <component>64studio.com/d-i.xml</component>
	    <component>64studio.com/linux.xml</component>
	    <component>64studio.com/grub.xml</component>
	    <component>64studio.com/openssh-server.xml</component>
	    <component>64studio.com/augeas.xml</component>
	    <component>64studio.com/xorg.xml</component>
	    <component>64studio.com/gnome.xml</component>
	  </contents>
	</component>
	

The first four options of the `<meta>` should be easy to understand. They instruct the `mediagen` command to build up an i386 CD iso image, labelled "My Linux 0.1", using the debian-installer. The fifth option:

	
	    <mediagen.inst-preseed-file>file:mypreseed</mediagen.inst-preseed-file>
	

tells `mediagen` to include in the media the `mypreseed` file you created in the previous step and use it as preseed file. The rest of the options are used to set various parameters, like the path of the APT repository generated with the `repogen` command and where to find the boot images.

You can now run

	
	pdk mediagen mylinux.xml
	

and enjoy your new ISO image in `images/img-bin1.iso`.
