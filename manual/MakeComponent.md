This document assumes that you've already installed PDK and have a workspace to work in. One way to reach that state is to follow the steps in [Workspace Setup](GettingStarted.md).

Don't miss the page about component maintenance, as it is going to be a bigger part of your world after you put together your initial components. The link is at the bottom of this page. 

Fire up your favorite editor to create an "abstract" component. The filename will be apache.xml:


	
	<?xml version="1.0"?>
	  <component>
	    <id>apache</id>
	      <name>Apache Web Server</name>
	        <contents>
	          <dsc>apache2</dsc>
	        </contents>
	  </component>
	


Obviously this isn't particularly useful information yet. These references need to be made concrete for the component to be useful. Resolving a component translates its abstract references to concrete ones. Resolving needs a source of candidate packages for resolving references.

Channels specify the sources for resolving. Define them with a channels.xml file, which will look something like this:

	
	<?xml version="1.0"?>
	  <channels>
	    <lucid>
	      <type>apt-deb</type>
	        <path>http://archive.ubuntu.com/ubuntu/</path>
	          <archs>i386 amd64 source</archs>
	            <dist>lucid</dist>
	              <components>main</components>
	    </lucid>
	  </channels>
	

This defines a single channel named "lucid" which refers to an Ubuntu apt repository.

To prepare the channels for use, run:


	
	pdk channel update
	


This downloads metadata for all the configured channels and stores it. Now that information on Ubuntu Lucid is available, resolve abstract package references like this:


	
	pdk resolve apache.xml

or

	pdk resolve -c lucid apache.xml
	


apache.xml should now look something like this:


	
	<?xml version="1.0" encoding="utf-8"?>
	<component>
	  <id>apache</id>
	  <name>Apache Web Server</name>
	  <contents>
	    <dsc>
	      <name>apache2</name>
	      <dsc ref="md5:d94c995bde2f13e04cdd0c21417a7ca5">
	        <name>apache2</name>
	        <version>2.0.53-5</version>
	      </dsc>
	      <deb ref="md5:5acd04d4cc6e9d1530aad04accdc8eb5">
	        <name>apache2-common</name>
	        <version>2.0.53-5</version>
	        <arch>i386</arch>
	      </deb>
	      <!-- many more binaries -->
	    </dsc>
	  </contents>
	</component>
	

Add and commit the components you have created with:

	
	find -type f | xargs pdk add
	pdk commit -m "Prototype"
	

Notice that both the source and binary packages are present. See below for more information on sticks and stars.

The component can now be used in products like any other. See [HowTo How to build a Linux distribution using PDK].

Note, however, that the remote packages have not been downloaded to your local system. To actually use pdk on the component or one that includes it, you must run pdk download on the component.


	
	pdk download apache.xml
	


Last, to do something useful, run this command to build an apt repository:


	
	pdk repogen apache.xml
	


The repsitory will show up in a directory called "repo". In the future the location of the built repository may change.

*Multiple channels*

To use multiple channels at once, add to the channels.xml file:


	
	<?xml version="1.0"?>
	<channels>
	  <lucid>
	    <type>apt-deb</type>
	    <path>http://localhost:$SERVER_PORT/</path>
	    <archs>i386 source</archs>
	    <dist>apache</dist>
	    <components>main</components>
	  </lucid>
	  <local>
	    <type>dir</type>
	    <path>/var/pbuilder/...</path>
	  </local>
	</channels>
	


To resolve against just one of these channels, specify it with the -c option:


	
	pdk resolve -c local apache.xml
	


To use all the channels at once, use no -c options. You can use more than one -c option at the same time to specify multiple specific channels. The channels will be checked in the order given.

*Sticks and Stars*

Resolving abstract references of a component descriptor offers two modes of operation called "sticks" and "stars":

A "Sticks" approach is indicated by the presence of an abstract binary package reference in the descriptor. At resolve time pdk will search channels for sources which appear to satisfy source closure for the newly resolved binary. 

A "Stars" approach is indicated by the presence of an abstract source package reference. At resolve time pdk will search for binaries which appear to be built from that source. 

The big idea behind these terms is that when assembling components, you find two kinds of packages, those you explicitly want, and those which are strictly present to provide the most primitive kinds of closure.

As pdk finds packages that match the requested sticks or stars approach, they are added to the component descriptor along with the requested package. All the concrete references are children of the original abstract reference.

NOTE: Don't specify abstract package references for both source and binaries in the same component. While it won't cause errors (perhaps it should) you will get a bunch of duplicate package references, which is not likely what you want.

The following document describes the real work in distribution maintenance. It's really easy to maintain components with PDK.

[How to Maintain Your Component](MaintainComponent.md)
 
 
