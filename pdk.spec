# $Progeny$
Summary: Componentized Linux Platform Development Kit (PDK)
Name: pdk
%define version 0.9.3
Version: %{version}
Release: 1
License: GPL
Group: Development/Tools
URL: http://componentizedlinux.org/index.php/Main_Page
Source: http://archive.progeny.com/progeny/pdk/pool/main/p/pdk/pdk_%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: python, git-core, python-curl, smart, python-elementtree, egenix-mx-base, PyXML, python-elementtree
BuildRequires: python, python-devel, funnelweb

%description
Componentized Linux is a platform for building specialized Linux
distributions.  Componentized Linux provides developers with a set of
reusable building blocks, called components, which can be easily assembled
into a wide variety of configurations and customized as necessary.  It
combines this componentized platform with a set of technologies (covering
installation, software management, and hardware detection, with more on the
way) that span traditional distribution boundaries and transform the
assembled components into a complete distribution.

This package contains the Componentized Linux Platform Development Kit (PDK).
Essentially, you can think of the PDK as "version control for
distributions"--it's intended to be a full suite of tools for building and
maintaining a CL-based distribution, from assembling a full distro from a set
of pre-built components to managing the evolution of the distro over time to
incorporate upstream changes to building your own custom components to
specifying global configuration like branding to integrating distro-specific
patches and managing the changes over time.

%prep
%setup


%build
python setup.py build_ext
python makeman.py >pdk.1

%install
rm -rf %{buildroot}
python setup.py install --root=%{buildroot}
sh run_atest -d
tar c --exclude=atest/packages --exclude=.svn atest \
    run_atest utest.py doc/*.fw >atest.tar
mkdir -p %{buildroot}/usr/share/man/man1/pdk.1pdk
cp pdk.1 %{buildroot}/usr/share/man/man1/pdk.1pdk
%clean
rm -rf %{buildroot} %{_builddir}/*


%files
%defattr(-, root, root, 0755)
%doc atest.tar doc/ README
%{_bindir}/*
%{_libdir}/python?.?/site-packages/pdk
%{_libdir}/python?.?/site-packages/picax
%{_libdir}/python?.?/site-packages/hashfile.py*
%{_mandir}/man1/*


%changelog
* Fri Oct 13 2006 Darrin Thompson <darrint@progeny.com> - 0.9.3-1
- Use newer Debian policy for building.
- Use versioned dep for git-core.
- Update to use newer pylint.
- Fix push command.
* Fri Jul 21 2006 Darrin Thompson <darrint@progeny.com> - 0.9.1-1
- In conditional includes, s/narrow/limit/, s/mask/exclude/.

* Fri Jul 14 2006 Darrin Thompson <darrint@progeny.com> - 0.9.0-1
- Change dep from python-mx-base to egenix-mx-base.
- Bump version to 0.9.0, since we are _way_ past 0.0.x.
- Add mv command.
- Add aliases create workspace and rm.
- Clean up diagnostics.
- Add rpm-md channels.

* Tue Jun 27 2006 Darrin Thompson <darrint@progeny.com> - 0.0.37-1
- Fill out pdk dependencies in pdk.spec.
- Groffify all built in documentation.
- Be more picky about excluding files in release-source.sh -E
- Heavily rework command framework for help system.
- Rip out the old comand shell.

* Fri Jun 9 2006 Darrin Thompson <darrint@progeny.com> - 0.0.36-1
- Make receiving a push more reliable.
- Bump protocol version number to 1.
- Try to filter # lines from commit messages.

* Wed May 25 2006 Darrin Thompson <darrint@progeny.com> - 0.0.35-1
- Make pdk work over https and Basic Auth.
- Expose find_upgrade and find_newest to api.

* Thu May 11 2006 Darrin Thompson <darrint@progeny.com> - 0.0.34-1
- Some api changes to support Progney internal projects.
- Fix upgrade bug, where sometimes downgrades happened.

* Fri May 5 2006 Darrin Thompson <darrint@progeny.com> - 0.0.33-1
- Fix bugs affecting RPM distros.
- Fix bug where entities weren't preserved when writing components.

* Fri Apr 21 2006 Darrin Thompson <darrint@progeny.com> - 0.0.32-1
- Initial rpm release.
- Incorporate changes needed to run pdk and tests in CentOS 4
- Original spec file via twisted packaging from Jeremy Katz.
