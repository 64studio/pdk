# Installation

First of all you have to install the `pdk` package. You may install it on any recent Ubuntu or Debian system.

If you are running Ubuntu/hardy or greater add the following line to your `/etc/apt/sources.list`:

	
	deb http://apt.64studio.com/backports hardy-backports main
	

while if you are running Debian/lenny or greater:

	
	deb http://apt.64studio.com/backports lenny-backports main
	

Then install the pdk package:

	
	apt-get update
	apt-get install pdk
	

# Create a new workspace

Now you are ready to create a PDK workspace:

	
	pdk workspace create <path>
	

e.g.,

	
	pdk workspace create ~/mylinux
	

then cd into the newly created workspace:

	
	cd <path>
	

e.g.,
	
	cd ~/mylinux
	

# Add your channels

Inside the `etc/` directory of your newly created workspace create a file called `channels.xml` that specifies the upstream channels that PDK should use to resolve abstract package references and download packages (see [MakeComponent How to build and maintain a component] for more information about abstract package references and pdk resolve).

For example, the following `channels.xml` defines a channel called "components", which contains pre-made components developed and tested by 64 Studio Ltd and used in our projects:
	
	<?xml version="1.0"?>
	<channels>
	  <components>
	    <type>source</type>
	    <path>http://pdk.64studio.com/channels/ubuntu/hardy/</path>
	  </components>
	</channels>
	

As the value of `<path>` element suggests, these components are targeted to Ubuntu/hardy, and include support for the i386 and amd64 architectures.

Note: Until you are familiar with the use of channels.xml, we suggest you try the above example unmodified.

Change back to the workspace directory.

Now run pdk channel update to update the channel cache (using the `channels.xml` present):

	
	pdk channel update
	

# Pull from channels

You are ready to pull the channel's components:

	
	pdk pull components
	

The PDK is now set up and ready to use. For more information, please see the following document:

* [MakingRepo Making Repository]
