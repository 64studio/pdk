*Table of contents*

1 Our Vision

2 Assembly

2.1 Component Description Language

2.2 Metadata

3 Implementation

4.1 Version Control

4.2 Component Updating

5 Convinced?

*Our Vision*

The Platform Development Kit (PDK) is intended to be a collection of tools that enables the developer to (1) easily and efficiently assemble Community/Progeny supplied components and the developer's own custom components into the desired platform configuration (a.k.a. a Componentized Linux Distribution or a product), and (2) manage and customize that product more effectively after release to end-users.

As such, our overall vision for the PDK is that it enables:

Easy Assembly of Your Platform
    Building Linux Distributions can be tricky. Upstream distributions tend to be delicate. Packages relate in ways that transcend their declared relationships, especially in the RPM world. PDK allows us to put together and test feature sets called components. These proven, pre-built building blocks facilitate the assembly process of a product and quicken the integration of desired features (as components play nicer in more combinations than "raw" packages). 

Easy Implementation of Your Platform
    The PDK can generate an APT-repo (for a platform or subcomponent) from a component descriptor(s), which describes an entire distribution or a select feature set. Also, the PDK can produce an installable system image using the mediagen tool to create an ISO that includes your distribution, configured to your specifications, and the Debian Installer (for a Debian-based product) or the Anaconda installer (for a RPM-based product). Likewise, in the future other deployment/provisioning mechanisms are planned to be implemented. 

Efficient Continuous Evolution of Your Platform
    Linux distribution maintenance is tedious and time consuming. Upgrading a distribution to incorporate feature improvements, to fix bugs and to eliminate security vulnerabilities typically requires more effort than assembling a new product. Add to this mix the fast pace of upstream activity and the task to produce stable releases in a timely manner can be an arduous one. Furthermore the diversity of upstream distribution releases might require unique procedures for delivering your customized releases. 

Flexible, Extensible and Ever Improving Tools
    The PDK's Command Line Interface does not predispose or impose a particular work style, as a GUI can, and enables script-ability. Its Plugin architecture and exposed API offer flexibility and encourage extensibility. We are committed to improving the PDK over time, and allowing you to use a newer version of the PDK even on your stable releases. We believe that this iterative approach will make maintaining your stable releases easier over time. 

*Assembly*

Components
    The Componentized Linux community and Progeny’s planned Subscription Services will provide developers the choice from hundred’s of proven feature sets and technologies, organized as Components, for rapidly creating or enhancing their distribution rather than dealing with tens of thousands of packages. 

        * Components closely track upstream project changes, allowing them to evolve independently of each other, while providing additional flexibility.
        * Components allow the formation of both Debian and RPM based distributions, providing additional choice to developers and allowing them to leverage existing skill sets and to more easily migrate from legacy custom platforms.
        * Componentized Linux supports leading industry standards, including the Linux Standard Base (LSB) certification and compatibility with Red Hat Enterprise Linux (RHEL). Componentized Linux is an open alternative to the increasingly proprietary nature of competing platforms.
        * Componentized Linux provides fine-grained control over the features and technologies included in a custom distribution. This allows Componentized Linux based distributions to scale down to limited storage and memory configurations, minimizes product complexity, and enhances security by allowing the removal of unnecessary software and services. 

Component Selection
    An unmet goal of the PDK, as yet, is your ability to effortlessly explore existing components to identify those that can form the foundation for your product or to add desired features. 

Repository Generation
    PDK makes assembling a package repository per your recipe an easy task. Once you've modified a component (descriptor), you can quickly translate any abstract package references into physical file representations using data channels, generate a repository and validate your changes via your own test procedures. PDK makes the "edit-compile-debug" cycle quick and painless. 

*Component Description Language*

Easy to Type
    The ability to define a Linux distribution or to specify a component with ease can't be overemphasized. 

Fosters Reusability and Enables Implementation Flexibility
    Our Hierarchical Component Model delivers powerful building blocks for your platform. Component descriptors are self-describing and use simple XML syntax. In their simplest form these contain an identifier for the component (a name) and a list of packages. In more complex forms these:

        * Can contain/refer to other components--creating a nested set of subcomponents (feature sets)--with outer layers having precedence over inner layers (hierarchical containment).
        * Can specify packages in an abstract form (by name) or by a concrete reference (a checksum that identifies a concrete package mapping in context of a particular source).
        * Can contain arbitrary metadata that is interpreted by various parts of the PDK tool suite to perform specific actions or to capture component properties of interest to the developer(s). 

Continuously Evolving
    While we seek to preserve backward compatibility, components are described in a formal language, and languages can undergo controlled change over time. 

*Metadata*

Arbitrary
    It is easy to associate bits of metadata and special entities with components and packages. 

Properties and Relationships
    Metadata can specify various package attributes, component relationships, interface requirements, architectures supported (indicating the type of binaries to include), languages supported (translations), etc. Conditional dependencies can be stated that are interpreted by the PDK, or tools outside the PDK (e.g. installers), to conditionally include, install, etc. certain packages based on the surrounding environment. 

Directives
    Metadata could be added to exert greater control over the layout of the APT repo to be generated, to specify package defaults, to add custom branding, to insert annotations, etc. Implementation of consumers of metadata are still being developed. One such consumer is the mediagen tool that makes it possible to build an ISO image complete with an installer using a single PDK command (think "pdk mediagen progeny.com/dccri-3.0.xml"). 

Version Ranges
    Instead of associating data with specific packages, you can associate data with names and version ranges. For instance, you could state that apache (>=2.0 <<2.0.55) is vulnerable to CAN-2005-2088. This association is applicable to any apache package in that version range. You would not need to keep updating the association as your distribution changes. 

Scope
    As stated earlier, multiple levels of scope allow you to modify what an upstream metadata provider (such as Progeny) asserts about certain packages. For instance, you may have backported the fix for CAN-2005-2088 to apache 2.0.48. Then, you can assert in a closer dynamic scope that apache (>=2.0.48) is not vulnerable to CAN-2005-2088. Your revised range will override the Progeny provided one (in a further dynamic scope) and if your package is greater than or equal to version 2.0.48, it will not be associated with the vulnerability. 

*Implementation*

Media Generation
    (Current work in process) PDK is currently undergoing a major change in this functional area. We intend to make generating installable ISO's very easy. Currently it is possible with the existing tool(s), but not in a convenient way. Our present focus is strengthening this feature set. 

Alternative Deployment Methods
    In the future, the PDK will also offer network-based methods of installing system platforms, along with system provisioning (change propagation) services. 

*Version Control*

From the onset, the PDK was designed to support constructing distributions using geographically separated, version controlled components. Consequently, the PDK provides the ability to manage/track the evolution of a distribution (or a component) using an embedded "distributed version control" system.

Workspace
    The PDK operates within an established local development space which contains the information about a platform (or component). The fundamental parts of a workspace are the Component Descriptor files and the Package Cache. 

Package Cache
    Packages are collected in a separate file store (a simple "look-aside cache" within the PDK workspace) and are referenced by hashes. They are considered immutable for all time and are not checked into version control, but instead are referenced from within version controlled components. 

Basic Version Control Operations
    add, revert, commit, etc. Basic commands that are familiar to CVS and SVN users are available. 

Distributed Version Control (DVC) Operations
    push, pull. These move whole chunks of history and packages in the cache between workspaces, even between a local and a remote host. 

Backup/Deployment Infrastructure
    The DVC operations, while not perfectly atomic always keep the target workspace in a consistent state, so it is safe to push to a staging machine for backup/deployment. 

Git Works
    Git is a well thought out infrastructure, and lends itself to building a DVC project like PDK. PDK's version control operations currently wrap git and expand on it. At this time, while PDK provides a more familiar command interface over git for basic operations, you are free to use git's more advanced features as you see fit. When pushing to remote repositories you will want to use PDK's command as it also synchronizes the remote package cache. 

*Component Updating*

Pull
    If you trust certain upstream providers to do work on certain components, you can pull directly from their published workspaces. This includes Progeny. In the grand scheme of things we are just a provider of finshed components which you can directly pull. This results in you getting the complete version control history of the components pulled. You can revert changesets, roll back, etc. 

Channels
    Locally indexed local/remote sources of package files are built and maintained by the PDK to facilitate resolving abstract package references, downloading and upgrading operations. 

Semantic Analysis
    The PDK provides the ability to compare the current workspace against the version control index, to diff two arbitrary components, or to compare a component with a set of data channels, while presenting meaningful contextual information. 

Upgrading
    Using the specified channels, the PDK automates the process of tracking/reporting package revisions of upstream sources and upgrading components as instructed by the developer. Progeny’s future Subscription Services will offer:

        * Detailed security information and relevant security updates.
        * Support for software versions not aligned with the current commercial and free distributions.
        * Long-term support for products/appliances with a useful life measured in years instead of months. 

Auditing
    The PDK ensures that the development space is valid by allowing you to audit the current workspace for data consistency. 

*Convinced?*

If this sounds interesting to you, you can start playing with the software immediately.

    * [GettingStarted Getting started with the Platform Development Kit (PDK)]
 