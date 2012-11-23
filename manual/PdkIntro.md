You can think of PDK as version control for distributions - it's intended to be a full suite of tools for building and maintaining a GNU/Linux distribution, from assembling a full distro using a set of prebuilt components to incorporating upstream changes, building your own custom components, specifying global configuration such as branding, integrating distro-specific patches, and managing the evolution of these changes over time.

TODO: add TOC macro here

# Our Vision

The Platform Development Kit (PDK) is intended to be a collection of tools that enables the developer to (1) easily and efficiently assemble Community/64 Studio supplied components and the developer's own custom components into the desired platform configuration (a.k.a. a _Custom Distribution'' or a ''product_), and (2) manage and customize that product more effectively after release to end-users.

As such, our overall vision for the PDK is that it enables:

*Easy Assembly of Your Platform*

Building Linux Distributions can be tricky. Upstream distributions tend to be delicate. Packages relate in ways that transcend their declared relationships. PDK allows us to put together and test feature sets called components. These proven, pre-built building blocks facilitate the assembly process of a product and quicken the integration of desired features (as components play nicer in more combinations than "raw" packages). 

*Easy Implementation of Your Platform*

The PDK can generate an APT-repo (for a platform or subcomponent) from a component descriptor, which describes an entire distribution or a select feature set. Also, the PDK can produce an installable system image using the `mediagen` command to create an ISO that includes your distribution, configured to your specifications, and the Debian Installer.

*Efficient Continuous Evolution of Your Platform*

Linux distribution maintenance is tedious and time consuming. Upgrading a distribution to incorporate feature improvements, to fix bugs and to eliminate security vulnerabilities typically requires more effort than assembling a new product. Add to this mix the fast pace of upstream activity and the task to produce stable releases in a timely manner can be an arduous one. Furthermore the diversity of upstream distribution releases might require unique procedures for delivering your customized releases. 

*Flexible, Extensible and Ever Improving Tools*

The PDK's Command Line Interface does not predispose or impose a particular work style, as a GUI can, and enables script-ability. Its Plugin architecture and exposed API offer flexibility and encourage extensibility. We are committed to improving the PDK over time, and allowing you to use a newer version of the PDK even on your stable releases. We believe that this iterative approach will make maintaining your stable releases easier over time. 

# Assembly

*Components*

The PDK community and 64 Studio provide developers the choice from a number of proven feature sets and technologies, organized as Components, for rapidly creating or enhancing their distribution rather than dealing with tens of thousands of packages. 

* Components closely track upstream project changes, allowing them to evolve independently of each other, while providing additional flexibility.
* PDK provides fine-grained control over the features and technologies included in a custom distribution. This allows PDK based distributions to scale down to limited storage and memory configurations, minimizes product complexity, and enhances security by allowing the removal of unnecessary software and services. 


*Repository Generation*

PDK makes assembling a package repository per your recipe an easy task. Once you've modified a component (descriptor), you can quickly translate any abstract package references into physical file representations using data channels, generate a repository and validate your changes via your own test procedures. PDK makes the "edit-compile-debug" cycle quick and painless.

Our Hierarchical Component Model delivers powerful building blocks for your platform. Component descriptors are self-describing and use simple XML syntax. In their simplest form these contain an identifier for the component (a name) and a list of packages. In more complex forms these:

* Can contain/refer to other components--creating a nested set of subcomponents (feature sets)--with outer layers having precedence over inner layers (hierarchical containment).
* Can specify packages in an abstract form (by name) or by a concrete reference (a checksum that identifies a concrete package mapping in context of a particular source).
* Can contain arbitrary metadata that is interpreted by various parts of the PDK tool suite to perform specific actions or to capture component properties of interest to the developer(s). 

# Version Control

From the onset, the PDK was designed to support constructing distributions using geographically separated, version controlled components. Consequently, the PDK provides the ability to manage/track the evolution of a distribution (or a component) using an embedded "distributed version control" system.

*Workspace*

The PDK operates within an established local development space which contains the information about a platform (or component). The fundamental parts of a workspace are the Component Descriptor files and the Package Cache. 

*Package Cache*

Packages are collected in a separate file store (a simple "look-aside cache" within the PDK workspace) and are referenced by hashes. They are considered immutable for all time and are not checked into version control, but instead are referenced from within version controlled components. 

*Basic Version Control Operations*

Basic commands like `add`, `revert`, `commit`, etc. that are familiar to CVS and SVN users are available. 

*Distributed Version Control (DVC) Operations*

The `push` and `pull` can move whole chunks of history and packages in the cache between workspaces, even between a local and a remote host. 

*Backup/Deployment Infrastructure*

The DVC operations, while not perfectly atomic always keep the target workspace in a consistent state, so it is safe to push to a staging machine for backup/deployment. 

*Git Works*

Git is a well thought out infrastructure, and lends itself to building a DVC project like PDK. PDK's version control operations currently wrap git and expand on it. At this time, while PDK provides a more familiar command interface over git for basic operations, you are free to use git's more advanced features as you see fit. When pushing to remote repositories you will want to use PDK's command as it also synchronizes the remote package cache. 

*Component Updating*

* _Pull_: If you trust certain upstream providers to do work on certain components, you can pull directly from their published workspaces. This includes 64 Studio. In the grand scheme of things we are just a provider of finshed components which you can directly pull. This results in you getting the complete version control history of the components pulled. You can revert changesets, roll back, etc. 

* _Channels_: Locally indexed local/remote sources of package files are built and maintained by the PDK to facilitate resolving abstract package references, downloading and upgrading operations. 

* _Semantic Analysis_: The PDK provides the ability to compare the current workspace against the version control index, to diff two arbitrary components, or to compare a component with a set of data channels, while presenting meaningful contextual information. 

* _Upgrading_: Using the specified channels, the PDK automates the process of tracking/reporting package revisions of upstream sources and upgrading components as instructed by the developer. 

# Convinced?


If this sounds interesting to you, you can start playing with the software immediately.

[HowTo How to build a GNU/Linux distro with PDK]
