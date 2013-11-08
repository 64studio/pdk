Before you actually build your installation ISO, you need to prepare a [preseed file](http://d-i.alioth.debian.org/manual/en.i386/apb.html)
to be passed to debian-installer, in order to set some of its parameters and automatically answer its questions.

Open your editor and create a new `mypreseed` file in your workspace containing the following lines:

	
	d-i             apt-setup/uri_type      select cdrom
	d-i             apt-setup/country       select enter information manually
	d-i             apt-setup/another       boolean false
	d-i             apt-setup/security_host string
	d-i             apt-setup/use_mirror    boolean false
	d-i             clock-setup/utc         boolean true
	
	d-i             grub-installer/with_other_os    boolean true
	d-i             grub-installer/only_debian      boolean true
	d-i             grub-installer/skip             boolean false
	d-i             pkgsel/install-language-support boolean false
	
	tasksel         tasksel/first multiselect standard
	

This example preseed file instructs the debian installer to use the CDROM drive as main APT source media and to automatically install the `standard` task, which will pull all packages of your Ubuntu/hardy remix.

You can now actually [BuildingMedia build your installation media].
