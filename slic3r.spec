Name:           slic3r
Version:        1.0.0
%global rcrc    RC3
%global verrc   %{version}%{rcrc}
Release:        0.4.%{rcrc}%{?dist}
Summary:        G-code generator for 3D printers (RepRap, Makerbot, Ultimaker etc.)
License:        AGPLv3 and CC-BY
# Images are CC-BY, code is AGPLv3
Group:          Applications/Engineering
URL:            http://slic3r.org/
Source0:        https://github.com/alexrj/Slic3r/archive/%{verrc}.tar.gz

# This is blocked by https://bugzilla.redhat.com/show_bug.cgi?id=1047914
%global         with_clipper 0

# Modify Build.PL so we are able to build this on Fedora
Patch0:         %{name}-buildpl.patch

# Don't warn for Perl >= 5.16
# Use /usr/share/slic3r as datadir
# Those two are located at the same place at the code, so the patch is merged
Patch1:         %{name}-nowarn-datadir.patch

%if %with_clipper
# Unbundle clipper
Patch2:         %{name}-clipper.patch
%endif

Source1:        %{name}.desktop
BuildRequires:  perl(Boost::Geometry::Utils) >= 0.15
BuildRequires:  perl(Class::XSAccessor)
BuildRequires:  perl(Encode::Locale)
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(ExtUtils::Typemaps::Default) >= 1.03
BuildRequires:  perl(ExtUtils::Typemap)
BuildRequires:  perl(File::Basename)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(Getopt::Long)
BuildRequires:  perl(Growl::GNTP)
BuildRequires:  perl(IO::Scalar)
BuildRequires:  perl(List::Util)
BuildRequires:  perl(Math::ConvexHull::MonotoneChain)
BuildRequires:  perl(Math::ConvexHull) >= 1.0.4
BuildRequires:  perl(Math::Geometry::Voronoi) >= 1.3
BuildRequires:  perl(Math::PlanePath) >= 53
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Module::Build::WithXSpp)

%if 0%{?fedora} > 19
BuildRequires:  perl(Moo) >= 1.003001
%else
BuildRequires:  perl(Moo)
%endif

BuildRequires:  perl(parent)
BuildRequires:  perl(Scalar::Util)
BuildRequires:  perl(Storable)
BuildRequires:  perl(SVG)
BuildRequires:  perl(Test::Harness)
BuildRequires:  perl(Test::More)
BuildRequires:  perl(Time::HiRes)
BuildRequires:  perl(Wx)
BuildRequires:  perl(XML::SAX)
BuildRequires:  perl(XML::SAX::ExpatXS)

%if %with_clipper
BuildRequires:  polyclipping-devel
%endif

BuildRequires:  desktop-file-utils
Requires:       perl(Class::XSAccessor)
Requires:       perl(Growl::GNTP)

%if 0%{?fedora} > 19
Requires:       perl(Moo) >= 1.003001
%endif

Requires:       perl(XML::SAX)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))

# Temporary bundling exception https://fedorahosted.org/fpc/ticket/368
Provides:       bundled(admesh) = 0.95

%description
Slic3r is a G-code generator for 3D printers. It's compatible with RepRaps,
Makerbots, Ultimakers and many more machines.
See the project homepage at slic3r.org and the documentation on the Slic3r wiki
for more information.

%prep
%setup -qn Slic3r-%{verrc}

%patch0 -p1
%patch1 -p1

%if %with_clipper
%patch2 -p1
# Remove bundled clipper
rm xs/src/clipper.*pp
%endif

%build
cd xs
perl ./Build.PL installdirs=vendor optimize="$RPM_OPT_FLAGS"
./Build
cd -
# Building non XS part only runs test, so skip it and run it in tests

%install
cd xs
./Build install destdir=%{buildroot} create_packlist=0
cd -
find %{buildroot} -type f -name '*.bs' -size 0 -exec rm -f {} \;

# I see no way of installing slic3r with it's build script
# So I copy the files around manually
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{perl_vendorlib}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/pixmaps

cp -a %{name}.pl %{buildroot}%{_bindir}/%{name}
cp -ar lib/* %{buildroot}%{perl_vendorlib}

cp -a var/* %{buildroot}%{_datadir}/%{name}
ln -s ../%{name}/Slic3r.ico %{buildroot}%{_datadir}/pixmaps/%{name}.ico
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE1}

%{_fixperms} %{buildroot}*

%check
cd xs
./Build test
cd -
SLIC3R_NO_AUTO=1 perl Build.PL installdirs=vendor
# the --gui runs no tests, it only checks requires

%files
%doc README.md
%{_bindir}/%{name}
%{perl_vendorlib}/Slic3r*
%{perl_vendorarch}/Slic3r*
%{perl_vendorarch}/auto/Slic3r*
%{_datadir}/pixmaps/%{name}.ico
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}

%changelog
* Wed Mar 05 2014 Miro Hrončok <mhroncok@redhat.com> - 1.0.0-0.4.RC3
- New RC version

* Thu Jan 02 2014 Miro Hrončok <mhroncok@redhat.com> - 1.0.0-0.3.RC2
- New RC version
- Remove already merged patches
- Only require Module::Build::WithXSpp 0.13 in Build.PL

* Fri Dec 13 2013 Miro Hrončok <mhroncok@redhat.com> - 1.0.0-0.2.RC1
- Backported several bugfixes

* Wed Nov 20 2013 Miro Hrončok <mhroncok@redhat.com> - 1.0.0-0.1.RC1
- 1.0.0RC1 version
- refactor build and install
- become arched
- bundle admesh

* Fri Oct 18 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.10b-5
- For F20+, require Moo >= 1.003001

* Fri Oct 18 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.10b-4
- Remove all filtering from provides, it is not needed anymore
- Don't add MANIFEST to %%doc
- Fix crash when loading config (#1020802)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.10b-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun 25 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.10b-2
- Filter perl(Wx::GLCanvas) from requires, it's optional and not yet in Fedora

* Mon Jun 24 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.10b-1
- New upstream release
- Removed some already merged patches

* Tue Apr 23 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.9-5
- Added BR perl(Encode::Locale)

* Tue Apr 23 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.9-4
- Removed (optional) Net::DBus usage, that causes crashes

* Tue Apr 23 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.9-3
- Added second patch to fix upstream issue 1077

* Tue Apr 23 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.9-2
- Added patch to fix upstream issue 1077

* Wed Apr 03 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.9-1
- New upstream release
- Added version to perl(Boost::Geometry::Utils) BR
- Sort (B)Rs alphabetically   
- Added (B)R perl(Class::XSAccessor)

* Wed Mar 20 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.8-4
- Comments added about patches

* Mon Mar 11 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.8-3
- In-file justification provided for patches

* Mon Jan 21 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.8-2
- Added patch to grab icons from %%{datadir}/%%{name}
- Added patch to avoid bad locales behavior
- Removed no longer needed filtering perl(Wx::Dialog) from Requires
- Filter perl(XML::SAX::PurePerl) only in F17
- Removed Perl default filter
- Removed bash launcher
- Renamed slic3r.pl to slic3r

* Thu Jan 17 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.8-1
- New version
- (Build)Requires Math::Clipper 1.17

* Thu Jan 17 2013 Miro Hrončok <mhroncok@redhat.com> - 0.9.7-3
- Updated source to respect GitHub rule
- Dropped mkdir, ln -s, cp, mv, perl macros
- Reorganized %%install section a bit
- Added version to Require perl(Math::Clipper)

* Sat Jan 05 2013 Miro Hrončok <miro@hroncok.cz> - 0.9.7-2
- Added Require perl(Math::Clipper)

* Sun Dec 30 2012 Miro Hrončok <miro@hroncok.cz> - 0.9.7-1
- New version
- Do not download additional sources from GitHub
- Removed deleting empty directories

* Fri Nov 16 2012 Miro Hrončok <miro@hroncok.cz> - 0.9.5-2
- Removed BRs provided by perl package

* Wed Nov 14 2012 Miro Hrončok <miro@hroncok.cz> 0.9.5-1
- New version
- Requires perl(Math::Clipper) >= 1.14
- Requires perl(Math::ConvexHull::MonotoneChain)
- Requires perl(XML::SAX::ExpatXS)

* Thu Oct 04 2012 Miro Hrončok <miro@hroncok.cz> 0.9.3-1
- New package
