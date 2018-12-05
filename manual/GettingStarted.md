# Installation

First of all you can install the `pdk` package for Debian Stretch/Buster/Sid:

```
echo 'deb https://apt.64studio.net stretch main' | sudo tee /etc/apt/sources.list.d/64studio.list
wget -qO - https://apt.64studio.net/archive-keyring.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install pdk pdk-mediagen
```

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

Inside the `etc/` directory of your newly created workspace create a file called `channels.xml` that specifies the upstream channels that PDK should use to resolve abstract package references and download packages (see [How to build and maintain a component](MakeComponent.md) for more information about abstract package references and pdk resolve).

For example, the following `channels.xml` defines a channel called "components", which contains pre-made components for Debian systems:
	
	<?xml version="1.0"?>
	<channels>
	  <components>
	    <type>source</type>
	    <path>http://pdk.example.com/channels/debian/stretch/</path>
	  </components>
	</channels>
	
As the value of the `<path>` element suggests, these components are targeted to Debian 9 'stretch'.

Change back to the workspace directory.

Now run pdk channel update to update the channel cache (using the `channels.xml` present):
	
	pdk channel update
	
# Pull from channels

You are ready to pull the channel's components:
	
	pdk pull components
	
The PDK is now set up and ready to use. For more information, please see the following document:

* [Making Repository](MakingRepo.md)
