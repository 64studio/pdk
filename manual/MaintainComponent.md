This is where reality strikes back. You've built a new distribution, a whole five minutes passes, and it becomes necessary to upgrade some packages in your components. Security fixes are available, bugs have been fixed, and your community has proposed a few good patches.

At this point we assume you have some components on your filesystem, and some new packages rolled by yourself or others.

Put the packages in one of your channels. If you have a <type>dir</type> channel defined, just dump the source and binary packages in the directory. It's recursive, so feel free to organize in there.


	
	pdk channel update
	


This grabs new information from all you channels at once. So make sure you have channels for all your security updates etc.

Pick a component, or just use a wild card and run the upgrade command.


	
	pdk upgrade --dry-run 64studio.com/apache.xml
	


And you get back a snazzy report showing what would change if you were to apply upgrades to packages in the component from your channels.

You may want to run this command on more than one component at a time. You can also limit the upgrade to particular channels.


	
	pdk upgrade --dry-run -c lucid-updates 64studio.com/apache.xml
	


Once you are happy with what pdk says it is going to do, just remove the --dry-run and let the command actually modify the file.

*Resolve vs. Upgrade*

So we have two different commands for modifying component files in place. Resolve, which we used to build up new components, and upgrade, which we are using to maintain components. Why did we write two commands?

Early in PDK's life there was only one command, and it was resolve. As we gained experience with it, we discovered that building up components from scratch and maintaining them over time are two very different operations. We ended up with what we feel is an elegant division of responsibility between the two commands.

*PDK Resolve*
    Ignores already resolved package references. When it finds abstract references, it attempts to find concrete references to fill them.
 
*PDK Upgrade*
    Ignores abstract references, only operates on previously resolved references. When it finds concrete references, it tries to find packages that qualify as upgrades. When it has qualified packages, it deletes all the old child packages and replaces them with a newer group of packages. 

*Still with Us?*

The next document to read is:

[Tracking Your Changes Over Time](TrackingChanges.md)

We've been crowing about how this thing is supposed to be "Version Control for Distributions." It's implemented and working well. 

