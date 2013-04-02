# See http://bugzilla.redhat.com/223663
%define multilib_archs x86_64 %{ix86} ppc64 ppc s390x s390 sparc64 sparcv9
%define multilib_basearchs x86_64 ppc64 s390x sparc64

# support qtchooser (adds qtchooser .conf file)
#define qtchooser 1

%define pre rc1

Summary: Qt5 - QtBase components
Name:    qt5-qtbase
Version: 5.0.2
Release: 0.1.%{pre}%{?dist}

# See LGPL_EXCEPTIONS.txt, LICENSE.GPL3, respectively, for exception details
License: LGPLv2 with exceptions or GPLv3 with exceptions
Url: http://qt-project.org/
Source0: http://releases.qt-project.org/qt5/%{version}%{?pre:-%{pre}}/submodules_tar/qtbase-opensource-src-%{version}.tar.xz

# help build on some lowmem archs, e.g. drop hard-coded -O3 optimization on some files
Patch1: qtbase-opensource-src-5.0.1-lowmem.patch

# support multilib optflags
Patch2: qtbase-multilib_optflags.patch

##upstream patches
Patch1341: 0341-Rename-qAbs-Function-for-timeval.patch

# macros
%define _qt5 %{name}
%define _qt5_prefix %{_libdir}/qt5
%define _qt5_archdatadir %{_libdir}/qt5
# -devel bindir items (still) conflict with qt4
# at least until this is all implemented,
# http://lists.qt-project.org/pipermail/development/2012-November/007990.html
#define _qt5_bindir %{_bindir}
%define _qt5_bindir %{_qt5_prefix}/bin
%define _qt5_datadir %{_datadir}/qt5
%define _qt5_docdir %{_docdir}/qt5
%define _qt5_examplesdir %{_qt5_prefix}/examples
%define _qt5_headerdir %{_includedir}/qt5
%define _qt5_importdir %{_qt5_archdatadir}/imports 
%define _qt5_libdir %{_libdir}
%define _qt5_libexecdir %{_qt5_archdatadir}/libexec
%define _qt5_plugindir %{_qt5_archdatadir}/plugins
%define _qt5_settingsdir %{_sysconfdir}/xdg
%define _qt5_sysconfdir %{_qt5_settingsdir} 
%define _qt5_translationdir %{_datadir}/qt5/translations

BuildRequires: cups-devel
BuildRequires: desktop-file-utils
BuildRequires: findutils
BuildRequires: firebird-devel
BuildRequires: freetds-devel
BuildRequires: libjpeg-devel
BuildRequires: libmng-devel
BuildRequires: libtiff-devel
BuildRequires: mysql-devel
BuildRequires: pkgconfig(atspi-2)
BuildRequires: pkgconfig(dbus-1)
BuildRequires: pkgconfig(fontconfig)
BuildRequires: pkgconfig(glesv2) pkgconfig(gl)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(gtk+-2.0)
BuildRequires: pkgconfig(icu-i18n)
BuildRequires: pkgconfig(NetworkManager)
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(libpng)
%if 0%{?fedora} > 17
BuildRequires: pkgconfig(libpcre) >= 8.30
%define pcre -system-pcre
%else
%define pcre -qt-pcre
%endif
BuildRequires: pkgconfig(sqlite3) 
BuildRequires: pkgconfig(xcb) pkgconfig(xcb-icccm) pkgconfig(xcb-image) pkgconfig(xcb-keysyms) pkgconfig(xcb-renderutil)
BuildRequires: pkgconfig(zlib)
BuildRequires: postgresql-devel
BuildRequires: unixODBC-devel

%description 
Qt is a software toolkit for developing applications.

This package contains base tools, like string, xml, and network
handling.

%package devel
Summary: Development files for %{name} 
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconfig(gl)
%description devel
%{summary}.

%package static 
Summary: Static library files for %{name}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
Requires: pkgconfig(fontconfig)
Requires: pkgconfig(glib-2.0)
Requires: pkgconfig(zlib)
%description static 
%{summary}.

%package ibase
Summary: IBase driver for Qt5's SQL classes
Requires: %{name}%{?_isa} = %{version}-%{release}
%description ibase
%{summary}.

%package mysql
Summary: MySQL driver for Qt5's SQL classes
Requires: %{name}%{?_isa} = %{version}-%{release}
%description mysql 
%{summary}.

%package odbc 
Summary: ODBC driver for Qt5's SQL classes
Requires: %{name}%{?_isa} = %{version}-%{release}
%description odbc 
%{summary}.

%package postgresql 
Summary: PostgreSQL driver for Qt5's SQL classes
Requires: %{name}%{?_isa} = %{version}-%{release}
%description postgresql 
%{summary}.

%package tds
Summary: TDS driver for Qt5's SQL classes
Requires: %{name}%{?_isa} = %{version}-%{release}
%description tds
%{summary}.

# debating whether to do 1 subpkg per library or not -- rex
%package x11
Summary: Qt5 GUI-related libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
%description x11
Qt5 libraries used for drawing widgets and OpenGL items.


%prep
%setup -q -n qtbase-opensource-src-%{version}

%patch2 -p1 -b .multilib_optflags
# drop backup file(s), else they get installed too, http://bugzilla.redhat.com/639463
rm -fv mkspecs/linux-g++*/qmake.conf.multilib-optflags

#patch1341 -p1 -b .0341

# drop -fexceptions from $RPM_OPT_FLAGS
RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed 's|-fexceptions||g'`

# lowmem hacks
%ifarch %{arm} s390
## FIXME, -O2 still injected somewhere it seems -- rex
#RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed 's|-O2|-O1|g'`
%patch1 -p1 -b .lowmem
%endif

%define platform linux-g++
%ifarch %{multilib_archs}
%if "%{?__isa_bits}" == "64"
%define platform linux-g++-64
%endif
%endif

sed -i -e "s|-O2|$RPM_OPT_FLAGS|g" \
  mkspecs/%{platform}/qmake.conf 

sed -i -e "s|^\(QMAKE_LFLAGS_RELEASE.*\)|\1 $RPM_LD_FLAGS|" \
  mkspecs/common/g++-unix.conf

# move some bundled libs to ensure they're not accidentally used
pushd src/3rdparty
mkdir UNUSED
mv freetype libjpeg libpng sqlite zlib xcb UNUSED/
popd


%build

./configure -v \
  -confirm-license \
  -opensource \
  -prefix %{_qt5_prefix} \
  -archdatadir %{_qt5_archdatadir} \
  -bindir %{_qt5_bindir} \
  -datadir %{_qt5_datadir} \
  -docdir %{_qt5_docdir} \
  -examplesdir %{_qt5_examplesdir} \
  -headerdir %{_qt5_headerdir} \
  -importdir %{_qt5_importdir} \
  -libdir %{_qt5_libdir} \
  -libexecdir %{_qt5_libexecdir} \
  -plugindir %{_qt5_plugindir} \
  -sysconfdir %{_qt5_sysconfdir} \
  -translationdir %{_qt5_translationdir} \
  -platform %{platform} \
  -release \
  -shared \
  -accessibility \
  -dbus-linked \
  -fontconfig \
  -glib \
  -gtkstyle \
  -iconv \
  -icu \
  -openssl-linked \
  -optimized-qmake \
  -nomake examples \
  -nomake tests \
  -no-pch \
  -no-rpath \
  -no-separate-debug-info \
  -no-strip \
  -reduce-relocations \
  -system-libjpeg \
  -system-libpng \
  %{?pcre} \
  -system-sqlite \
  -system-zlib

make %{?_smp_mflags}


%install

make install INSTALL_ROOT=%{buildroot}

# Qt5.pc
cat >%{buildroot}%{_libdir}/pkgconfig/Qt5.pc<<EOF
prefix=%{_qt5_prefix}
archdatadir=%{_qt5_archdatadir}
bindir=%{_qt5_bindir}
datadir=%{_qt5_datadir}

docdir=%{_qt5_docdir}
examplesdir=%{_qt5_examplesdir}
headerdir=%{_qt5_headerdir}
importdir=%{_qt5_importdir}
libdir=%{_qt5_libdir}
libexecdir=%{_qt5_libexecdir}
moc=%{_qt5_bindir}/moc
plugindir=%{_qt5_plugindir}
qmake=%{_qt5_bindir}/qmake
settingsdir=%{_qt5_settingsdir}
sysconfdir=%{_qt5_sysconfdir}
translationdir=%{_qt5_translationdir}

Name: Qt5
Description: Qt5 Configuration
Version: %{version}
EOF

# rpm macros
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cat >%{buildroot}%{_sysconfdir}/rpm/macros.qt5<<EOF
%%_qt5 %{name}
%%_qt5_epoch %{?epoch}%{!?epoch:0}
%%_qt5_version %{version}
%%_qt5_evr %{?epoch:%{epoch:}}%{version}-%{release}
%%_qt5_prefix %%{_libdir}/qt5
%%_qt5_archdatadir %%{_qt5_prefix}
%%_qt5_bindir %%{_qt5_prefix}/bin
%%_qt5_datadir %%{_datadir}/qt5
%%_qt5_docdir %%{_docdir}/qt5
%%_qt5_examples %%{_qt5_prefix}/examples
%%_qt5_headerdir %%{_includedir}/qt5
%%_qt5_importdir %{_qt5_archdatadir}/imports 
%%_qt5_libdir %%{_libdir}
%%_qt5_libexecdir %{_qt5_archdatadir}/libexec
%%_qt5_plugindir %{_qt5_archdatadir}/plugins 
%%_qt5_qmake %%{_qt5_bindir}/qmake
%%_qt5_settingsdir %%{_sysconfdir}/xdg
%%_qt5_sysconfdir %%{_qt5_settingsdir} 
%%_qt5_translationdir %%{_datadir}/qt5/translations 
EOF

# create/own dirs
mkdir -p %{buildroot}{%{_qt5_archdatadir}/mkspecs/modules,%{_qt5_importdir},%{_qt5_libexecdir},%{_qt5_plugindir}/iconengines,%{_qt5_translationdir}}

# put non-conflicting binaries with -qt5 postfix in %{_bindir} 
mkdir %{buildroot}%{_bindir}
pushd %{buildroot}%{_qt5_bindir}
for i in * ; do
  case "${i}" in
    moc|qdbuscpp2xml|qdbusxml2cpp|qmake|rcc|syncqt|uic)
      mv $i ../../../bin/${i}-qt5
      ln -s ../../../bin/${i}-qt5 .
      ln -s ../../../bin/${i}-qt5 $i
      ;;
   *)
      mv $i ../../../bin/
      ln -s ../../../bin/$i .
      ;;
  esac
done
popd

# qtchooser conf
%if 0%{?qtchooser}
  mkdir -p %{buildroot}%{_sysconfdir}/xdg/qtchooser
  pushd    %{buildroot}%{_sysconfdir}/xdg/qtchooser
  echo "%{_qt5_bindir}" >  qt5.conf
  echo "%{_qt5_prefix}" >> qt5.conf
  %ifarch %{multilib_archs}
    mv qt5.conf qt5-%{__isa_bits}.conf
    %ifarch %{multilib_basearchs}
      ln -sf qt5-%{__isa_bits}.conf qt5.conf
    %endif
  %endif
  popd
%endif

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files 
%doc LICENSE.GPL LICENSE.LGPL LGPL_EXCEPTION.txt
%if 0%{?qtchooser}
# not editable config files, so not using %%config here
%dir %{_sysconfdir}/xdg/qtchooser
%{_sysconfdir}/xdg/qtchooser/*.conf
%endif
%{_qt5_libdir}/libQt5Concurrent.so.5*
%{_qt5_libdir}/libQt5Core.so.5*
%{_qt5_libdir}/libQt5DBus.so.5*
%{_qt5_libdir}/libQt5Network.so.5*
%{_qt5_libdir}/libQt5Sql.so.5*
%{_qt5_libdir}/libQt5Test.so.5*
%{_qt5_libdir}/libQt5Xml.so.5*
%{_qt5_docdir}/
%{_qt5_importdir}/
%{_qt5_translationdir}/
%dir %{_qt5_prefix}/
%dir %{_qt5_datadir}/
%dir %{_qt5_libexecdir}/
%dir %{_qt5_plugindir}/
%dir %{_qt5_plugindir}/bearer/
%{_qt5_plugindir}/bearer/libqconnmanbearer.so
%{_qt5_plugindir}/bearer/libqgenericbearer.so
%{_qt5_plugindir}/bearer/libqnmbearer.so
%dir %{_qt5_plugindir}/accessible/
%dir %{_qt5_plugindir}/generic/
%dir %{_qt5_plugindir}/imageformats/
%dir %{_qt5_plugindir}/platforminputcontexts/
%dir %{_qt5_plugindir}/platforms/
%dir %{_qt5_plugindir}/printsupport/
%dir %{_qt5_plugindir}/sqldrivers/
%{_qt5_plugindir}/sqldrivers/libqsqlite.so

%files devel
%{_sysconfdir}/rpm/macros.qt5
%if "%{_qt5_bindir}" != "%{_bindir}"
%dir %{_qt5_bindir}
%endif
%{_bindir}/moc*
%{_bindir}/qdbuscpp2xml*
%{_bindir}/qdbusxml2cpp*
%{_bindir}/qdoc*
%{_bindir}/qmake*
%{_bindir}/rcc*
%{_bindir}/syncqt*
%{_bindir}/uic*
%{_qt5_bindir}/moc*
%{_qt5_bindir}/qdbuscpp2xml*
%{_qt5_bindir}/qdbusxml2cpp*
%{_qt5_bindir}/qdoc*
%{_qt5_bindir}/qmake*
%{_qt5_bindir}/rcc*
%{_qt5_bindir}/syncqt*
%{_qt5_bindir}/uic*
%if "%{_qt5_headerdir}" != "%{_includedir}"
%dir %{_qt5_headerdir}
%endif
%{_qt5_headerdir}/Qt*/
%{_qt5_archdatadir}/mkspecs/
%{_qt5_libdir}/libQt5Concurrent.prl
%{_qt5_libdir}/libQt5Concurrent.so
%{_qt5_libdir}/libQt5Core.prl
%{_qt5_libdir}/libQt5Core.so
%{_qt5_libdir}/libQt5DBus.prl
%{_qt5_libdir}/libQt5DBus.so
%{_qt5_libdir}/libQt5Gui.prl
%{_qt5_libdir}/libQt5Gui.so
%{_qt5_libdir}/libQt5Network.prl
%{_qt5_libdir}/libQt5Network.so
%{_qt5_libdir}/libQt5OpenGL.prl
%{_qt5_libdir}/libQt5OpenGL.so
%{_qt5_libdir}/libQt5PrintSupport.prl
%{_qt5_libdir}/libQt5PrintSupport.so
%{_qt5_libdir}/libQt5Sql.prl
%{_qt5_libdir}/libQt5Sql.so
%{_qt5_libdir}/libQt5Test.prl
%{_qt5_libdir}/libQt5Test.so
%{_qt5_libdir}/libQt5Widgets.prl
%{_qt5_libdir}/libQt5Widgets.so
%{_qt5_libdir}/libQt5Xml.prl
%{_qt5_libdir}/libQt5Xml.so
%dir %{_qt5_libdir}/cmake/
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc

%files static
%{_qt5_libdir}/libQt5Bootstrap.*a
%{_qt5_libdir}/libQt5Bootstrap.prl
%{_qt5_libdir}/libQt5PlatformSupport.*a
%{_qt5_libdir}/libQt5PlatformSupport.prl

%files ibase
%{_qt5_plugindir}/sqldrivers/libqsqlibase.so

%files mysql
%{_qt5_plugindir}/sqldrivers/libqsqlmysql.so

%files odbc 
%{_qt5_plugindir}/sqldrivers/libqsqlodbc.so

%files postgresql 
%{_qt5_plugindir}/sqldrivers/libqsqlpsql.so

%files tds
%{_qt5_plugindir}/sqldrivers/libqsqltds.so

%post x11 -p /sbin/ldconfig
%postun x11 -p /sbin/ldconfig

%files x11
%{_qt5_libdir}/libQt5Gui.so.5*
%{_qt5_libdir}/libQt5OpenGL.so.5*
%{_qt5_libdir}/libQt5PrintSupport.so.5*
%{_qt5_libdir}/libQt5Widgets.so.5*
%{_qt5_plugindir}/accessible/libqtaccessiblewidgets.so
%{_qt5_plugindir}/generic/libqevdevkeyboardplugin.so
%{_qt5_plugindir}/generic/libqevdevmouseplugin.so
%{_qt5_plugindir}/generic/libqevdevtabletplugin.so
%{_qt5_plugindir}/generic/libqevdevtouchplugin.so
%{_qt5_plugindir}/imageformats/libqgif.so
%{_qt5_plugindir}/imageformats/libqico.so
%{_qt5_plugindir}/imageformats/libqjpeg.so
%{_qt5_plugindir}/platforminputcontexts/libibusplatforminputcontextplugin.so
%{_qt5_plugindir}/platforminputcontexts/libmaliitplatforminputcontextplugin.so
%{_qt5_plugindir}/platforms/libqlinuxfb.so
%{_qt5_plugindir}/platforms/libqminimal.so
%{_qt5_plugindir}/platforms/libqxcb.so
%{_qt5_plugindir}/printsupport/libcupsprintersupport.so


%changelog
* Tue Apr 02 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-0.1.rc1
- 5.0.2-rc1

* Sat Mar 16 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-6
- pull in upstream gcc-4.8.0 buildfix

* Tue Feb 26 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-5
- -static subpkg, Requires: fontconfig-devel,glib2-devel,zlib-devel
- -devel: Requires: pkgconfig(gl)

* Mon Feb 25 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-4
- create/own %%{_qt5_plugindir}/iconengines
- -devel: create/own %%{_qt5_archdatadir}/mkspecs/modules
- cleanup .prl

* Sat Feb 23 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-3
- +%%_qt5_libexecdir

* Sat Feb 23 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-2
- macros.qt5: fix %%_qt5_headerdir, %%_qt5_datadir, %%_qt5_plugindir

* Thu Jan 31 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-1
- 5.0.1
- lowmem patch for %%arm, s390

* Wed Jan 30 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-4
- %%build: -system-pcre, BR: pkgconfig(libpcre)
- use -O1 optimization on lowmem (s390) arch

* Thu Jan 24 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-3
- enable (non-conflicting) qtchooser support

* Wed Jan 09 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-2
- add qtchooser support (disabled by default)

* Wed Dec 19 2012 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-1
- 5.0 (final)

* Thu Dec 13 2012 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-0.4.rc2
- 5.0-rc2
- initial try at putting non-conflicting binaries in %%_bindir

* Thu Dec 06 2012 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-0.3.rc1 
- 5.0-rc1

* Wed Nov 28 2012 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-0.2.beta2
- qtbase --> qt5-qtbase

* Mon Nov 19 2012 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-0.1.beta2
- %%build: -accessibility
- macros.qt5: +%%_qt5_archdatadir +%%_qt5_settingsdir
- pull in a couple more configure-related upstream patches 

* Wed Nov 14 2012 Rex Dieter <rdieter@fedoraproject.org> 5.0.0-0.0.beta2
- first try

