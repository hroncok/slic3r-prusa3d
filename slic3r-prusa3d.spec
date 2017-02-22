%global orig slic3r
Name:           %{orig}-prusa3d
Version:        1.33.8
Release:        1%{?dist}
Summary:        G-code generator for 3D printers (RepRap, Makerbot, Ultimaker etc.)
License:        AGPLv3 and CC-BY
# Images are CC-BY, code is AGPLv3
Group:          Applications/Engineering
URL:            https://github.com/prusa3d/Slic3r
Source0:        https://github.com/prusa3d/Slic3r/archive/version_%{version}.tar.gz

# Modify Build.PL so we are able to build this on Fedora
Patch0:         %{orig}-buildpl.patch

# Use /usr/share/slic3r as datadir
Patch1:         %{orig}-datadir.patch
Patch2:         %{orig}-english-locale.patch
Patch3:         %{orig}-linker.patch
#Patch4:         %%{orig}-clipper.patch

Source1:        %{name}.desktop
Source2:        %{name}.appdata.xml

BuildRequires:  perl-devel
BuildRequires:  perl-generators
BuildRequires:  perl(Class::XSAccessor)
BuildRequires:  perl(Devel::CheckLib)
BuildRequires:  perl(Encode::Locale) >= 1.05
BuildRequires:  perl(ExtUtils::MakeMaker) >= 6.80
BuildRequires:  perl(ExtUtils::ParseXS) >= 3.22
BuildRequires:  perl(ExtUtils::Typemaps::Default) >= 1.05
BuildRequires:  perl(ExtUtils::Typemaps) >= 1.00
BuildRequires:  perl(File::Basename)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(Getopt::Long)
BuildRequires:  perl(Growl::GNTP) >= 0.15
BuildRequires:  perl(IO::Scalar)
BuildRequires:  perl(List::Util)
BuildRequires:  perl(Math::PlanePath) >= 53
BuildRequires:  perl(Module::Build::WithXSpp) >= 0.14
BuildRequires:  perl(Moo) >= 1.003001
BuildRequires:  perl(parent)
BuildRequires:  perl(POSIX)
BuildRequires:  perl(Scalar::Util)
BuildRequires:  perl(Storable)
BuildRequires:  perl(SVG)
BuildRequires:  perl(Test::Harness)
BuildRequires:  perl(Test::More)
BuildRequires:  perl(Thread::Semaphore)
BuildRequires:  perl(threads) >= 1.96
BuildRequires:  perl(Time::HiRes)
BuildRequires:  perl(Unicode::Normalize)
BuildRequires:  perl(Wx)
BuildRequires:  perl(XML::SAX)
BuildRequires:  perl(XML::SAX::ExpatXS)

#BuildRequires:  admesh-devel >= 0.98.1
BuildRequires:  boost-devel
BuildRequires:  desktop-file-utils
BuildRequires:  poly2tri-devel
#BuildRequires:  polyclipping-devel >= 6.2.0
BuildRequires:  ImageMagick

Requires:       perl(XML::SAX)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
#Requires:       admesh-libs >= 0.98.1

# For faster slicing
Recommends:     perl(Thread::Queue)

# Fedora polyclipping version is not compatible
Provides:       bundled(polyclipping) = 6.2.9

# Upstream has custom patches, reluctant to send to upstream
Provides:       bundled(admesh-libs) = 0.98.1

%description
This is Slic3r Prusa Edition, a modified version of Slic3r adding more features
not only useful for the Prusa printers.

Slic3r is a G-code generator for 3D printers. It's compatible with RepRaps,
Makerbots, Ultimakers and many more machines.
See the project homepage at slic3r.org and the documentation on the Slic3r wiki
for more information.

%prep
%setup -qn Slic3r-version_%{version}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
#%%patch4 -p1

# Remove bundled libs
#rm -rf xs/src/admesh
#rm xs/src/clipper.*pp
rm -rf xs/src/poly2tri
rm -rf xs/src/boost
rm -rf xs/src/glew
# There is also Shiny, a profiler. But it's basically ifdefed out.

# Fix the version
sed -i 's/#define SLIC3R_VERSION .*$/#define SLIC3R_VERSION "%{version}"/' xs/src/libslic3r/libslic3r.h

# Fix the shebang
sed -i 's|#!/usr/bin/env perl|#!%{__perl}|' %{orig}.pl

#####################
# Move it to a separate namespace, so it does not conflict with the slic3r package
mv lib/Slic3r lib/Slic3rPrusa
mv lib/Slic3r.pm lib/Slic3rPrusa.pm
mv xs/lib/Slic3r xs/lib/Slic3rPrusa

# Perl
find . \( -name '*.pm' -o -name '*.t' -o -name '*.pl' -o -name '*.PL' -o -name '*.xsp'  -o -name '*.map' \) -exec \
  sed -i -e 's/Slic3r::/Slic3rPrusa::/g' \
         -e 's/package Slic3r;/package Slic3rPrusa;/g' \
         -e 's/{Slic3r};/{Slic3rPrusa};/g' \
         -e 's/use Slic3r;/use Slic3rPrusa;/g' \
  {} \;

# C++
find xs/src \( -name '*.cpp' -o -name '*.c' -o -name '*.hpp' -o -name '*.h' \) -exec \
  sed -i -e 's/Slic3r::/Slic3rPrusa::/g' \
         -e 's/namespace Slic3r/namespace Slic3rPrusa/g' \
  {} \;

# Settings directory
sed -i 's/GetUserDataDir)/GetUserDataDir)."Prusa"/' lib/Slic3rPrusa/GUI.pm

#####################

%build
cd xs
perl ./Build.PL installdirs=vendor optimize="$RPM_OPT_FLAGS"
./Build
cd -
# Building non XS part only runs test, so skip it and run it in tests

# prepare pngs in mutliple sizes
for res in 16 24 32 48 128; do
  mkdir -p hicolor/${res}x${res}/apps
done
cd hicolor
convert ../var/Slic3r.ico %{name}.png
cp %{name}-0.png 128x128/apps/%{name}.png
cp %{name}-2.png 48x48/apps/%{name}.png
cp %{name}-3.png 32x32/apps/%{name}.png
cp %{name}-4.png 24x24/apps/%{name}.png
cp %{name}-5.png 16x16/apps/%{name}.png
rm %{name}-*.png
cd -

# To avoid "iCCP: Not recognized known sRGB profile that has been edited"
cd var
find . -type f -name "*.png" -exec convert {} -strip {} \;
cd -

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
mkdir -p %{buildroot}%{_datadir}/icons
mkdir -p %{buildroot}%{_datadir}/appdata

cp -a %{orig}.pl %{buildroot}%{_bindir}/%{name}
cp -ar lib/* %{buildroot}%{perl_vendorlib}

cp -a var/* %{buildroot}%{_datadir}/%{name}
cp -r hicolor %{buildroot}%{_datadir}/icons
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE1}

cp %{SOURCE2} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml

%{_fixperms} %{buildroot}*

%check
cd xs
./Build test verbose=1
cd -
SLIC3R_NO_AUTO=1 perl Build.PL installdirs=vendor
# the --gui runs no tests, it only checks requires

%post
/sbin/ldconfig
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc README.md
%{_bindir}/%{name}
%{perl_vendorlib}/Slic3rPrusa*
%{perl_vendorarch}/Slic3rPrusa*
%{perl_vendorarch}/auto/Slic3rPrusa*
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/%{name}

%changelog
* Wed Feb 22 2017 Miro Hrončok <mhroncok@redhat.com> - 1.33.8-1
- Update to 1.33.8
- Mention it's a fork in the description

* Sat Dec 17 2016 Miro Hrončok <mhroncok@redhat.com> - 1.31.6-1
- Update to 1.31.6
- Bundle admesh
- Recommend Thread::Queue for faster slicing
- Unbundle glew

* Fri Nov 11 2016 Miro Hrončok <mhroncok@redhat.com> - 1.31.4-1
- New package adapted from the slic3r package
