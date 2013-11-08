Create a new file in your workspace called for example `mylinux.xml`, and include in it all the components you want to use in your distribution. The following example assembles a basic desktop system featuring Xorg and Gnome, using components provided by 64studio.com:

	
	<?xml version="1.0" encoding="utf-8"?>
	<component>
	  <id>hardy</id>
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
	

Your Ubuntu-based distribution needs a repository to store all its packages. This is done easily in PDK.

	
	pdk repogen mylinux.xml
	

In this case the component `mylinux.xml` that we just created, simply refers to components that come from pulling all the `components` channel. In the next sections you learn how to make components from scratch. Any component with packages in it may be passed to repogen.

In some cases you may just want to download the packages referred by the component, without actually building the APT repo. Use the `download` command for that:

	
	pdk download mylinux.xml
	

You may now wonder where all the files went when you run the `repogen` or `download` commands. They go to a workspace place called the "cache". Inside your workspace/etc directory, run a find on the `etc/cache` directory to see the contents. 

At this point you have a proper APT repository in a directory called: repo/. (See pdk repogen --help to change the default behavior.)

	
	find repo/
	

outputs the structure of nice poolified apt repository.

Once the download has completed (a long long process, sorry) you should find that the repogen runs too quickly considering that hundreds of megabytes, maybe even gigabytes of packages have been deposited in the repository. This is because we use hard links to put the packages in the repository. It is, therefore, safe to delete the whole repository, and repository creation can be done quickly once the packages are in your local cache.


Next: [PreseedFile Write a preseed file]