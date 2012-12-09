Summary:	Program that wraps normal socket connections with SSL/TLS
Name:		stunnel
Version:	4.53
Release:	4
License:	GPLv2
Group:		System/Servers
URL:		http://www.stunnel.org/
Source0:	http://www.stunnel.org/download/stunnel/src/%{name}-%{version}.tar.gz
Source1:	http://www.stunnel.org/download/stunnel/src/%{name}-%{version}.tar.gz.asc
Source2:	stunnel.service
BuildRequires:	pkgconfig(openssl)
BuildRequires:	tcp_wrappers-devel
Requires:	tcp_wrappers
Obsoletes:	%{mklibname %{name} 0} < 4.53
Obsoletes:	%{mklibname %{name} -d} < 4.53
Obsoletes:	%{mklibname %{name} -d -s} < 4.53

%description
The stunnel program is designed to work as SSL encryption wrapper between 
remote clients and local (inetd-startable) or remote servers. The concept is 
that having non-SSL aware daemons running on your system you can easily set 
them up to communicate with clients over secure SSL channels.

stunnel can be used to add SSL functionality to commonly used inetd daemons 
like POP-2, POP-3, and IMAP servers, to standalone daemons like NNTP, SMTP 
and HTTP, and in tunneling PPP over network sockets without changes to the 
source code.

%prep
%setup -q

iconv -f iso-8859-1 -t utf-8 < doc/stunnel.fr.8 > doc/stunnel.fr.8_
mv doc/stunnel.fr.8_ doc/stunnel.fr.8
iconv -f iso-8859-2 -t utf-8 < doc/stunnel.pl.8 > doc/stunnel.pl.8_
mv doc/stunnel.pl.8_ doc/stunnel.pl.8

# XXX don't install /var/lib/stunnel
perl -ni -e '/INSTALL.*-m 1770 -g nogroup.*stunnel$/ or print' tools/Makefile.am
%build
%configure2_5x \
    --with-threads=fork \
    --with-ssl=%{_prefix} \
    --disable-static \
    --enable-shared
%make pkglibdir=%{_libdir}

%install
rm -rf %{buildroot}

# (oe) hack... don't generate the pem file, and stunnel.conf
install -d %{buildroot}%{_sysconfdir}/%{name}
touch %{buildroot}%{_sysconfdir}/%{name}/stunnel.pem

%makeinstall docdir=`pwd`/doc-to-install pkglibdir=%{buildroot}%{_libdir}

install -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/stunnel.service

install -d %{buildroot}%{_var}/openssl/certs/trusted
install -d %{buildroot}%{_var}/run/stunnel

mv %{buildroot}%{_sysconfdir}/%{name}/stunnel.conf-sample \
    %{buildroot}%{_sysconfdir}/%{name}/stunnel.conf

perl -pi \
    -e 's|cert = .*|cert = /etc/pki/tls/certs/stunnel.pem|;' \
    -e 's|;key = .*|key = /etc/pki/tls/private//stunnel.pem|;' \
    %{buildroot}%{_sysconfdir}/%{name}/stunnel.conf

# Move the translated man pages to the right subdirectories, and strip off the
# language suffixes.
for lang in fr pl ; do
        mkdir -p %{buildroot}%{_mandir}/${lang}/man8
        mv %{buildroot}%{_mandir}/man8/*.${lang}.8* %{buildroot}%{_mandir}/${lang}/man8/
        rename ".${lang}" "" %{buildroot}%{_mandir}/${lang}/man8/*
done

# cleanup
rm -f ./doc-to-install/INSTALL.W32
rm -f %{buildroot}%{_sysconfdir}/%{name}/stunnel.pem
rm -f %{buildroot}%{_libdir}/libstunnel.la

%post
%_create_ssl_certificate stunnel

%files
%doc doc-to-install/*
%{_bindir}/stunnel
%{_bindir}/stunnel3
%dir %{_var}/run/stunnel
%{_mandir}/man8/stunnel.8.*
%lang(fr) %{_mandir}/fr/man8/stunnel.8*
%lang(pl) %{_mandir}/pl/man8/stunnel.8*
%config(noreplace) %{_sysconfdir}/%{name}/stunnel.conf
%{_unitdir}/stunnel.service
%{_libdir}/libstunnel.so


%changelog
* Mon Aug 20 2012 guillomovitch <guillomovitch> 4.53-3.mga3
+ Revision: 282639
- don't bother using library and devel subpackage, as there is no defined interface, and no include file available (#4223)

* Tue Aug 14 2012 guillomovitch <guillomovitch> 4.53-2.mga3
+ Revision: 281253
- add systemd support (Bit Twister <junk_no_spam@verizon.net>)
- mark the configuration file as configuration
- readd explicit lib package dependenncy

* Tue Aug 14 2012 guillomovitch <guillomovitch> 4.53-1.mga3
+ Revision: 281247
- new version
- spec cleanup
- drop useless patches
- drop static lib package
- use rpm-helper macros to generate ssl certificate

* Sun Jan 09 2011 blino <blino> 4.34-3.mga1
+ Revision: 3737
- remove old ldconfig scriptlets
- imported package stunnel


* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 4.34-2mdv2011.0
+ Revision: 627719
- don't force the usage of automake1.7

* Thu Oct 14 2010 Sandro Cazzaniga <kharec@mandriva.org> 4.34-1mdv2011.0
+ Revision: 585547
- update patches
- update to 4.34
- fix pacthes names in spec file
- remove -b option

* Sat May 08 2010 Sandro Cazzaniga <kharec@mandriva.org> 4.33-2mdv2010.1
+ Revision: 544098
- add a stunnel.conf file

* Sun Apr 25 2010 Sandro Cazzaniga <kharec@mandriva.org> 4.33-1mdv2010.1
+ Revision: 538739
- update to 4.33

* Wed Apr 07 2010 Funda Wang <fwang@mandriva.org> 4.31-2mdv2010.1
+ Revision: 532515
- rebuild

  + Sandro Cazzaniga <kharec@mandriva.org>
    - fix license
    - drop some patches (applied upstream for this version)
    - update to 4.31
    - fix file list

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 4.29-2mdv2010.1
+ Revision: 511641
- rebuilt against openssl-0.9.8m

* Thu Dec 10 2009 Frederik Himpe <fhimpe@mandriva.org> 4.29-1mdv2010.1
+ Revision: 476124
- update to new version 4.29

* Mon Nov 09 2009 Frederik Himpe <fhimpe@mandriva.org> 4.28-1mdv2010.1
+ Revision: 463687
- Update to new version 4.28

* Sun Jun 21 2009 Oden Eriksson <oeriksson@mandriva.com> 4.27-1mdv2010.0
+ Revision: 387861
- forgot to rediff the patches, duh!
- add another file...
- 4.27

* Wed Dec 17 2008 Oden Eriksson <oeriksson@mandriva.com> 4.26-2mdv2009.1
+ Revision: 315259
- rediffed fuzzy patches

* Sun Sep 21 2008 Oden Eriksson <oeriksson@mandriva.com> 4.26-1mdv2009.0
+ Revision: 286323
- 4.26 (Major bugfixes)
- rediffed P3
- drop upstream implemented patches

* Thu Sep 11 2008 Oden Eriksson <oeriksson@mandriva.com> 4.25-4mdv2009.0
+ Revision: 283757
- fix #31837 (Incorrect pid file location in sample init script)

* Tue Sep 09 2008 Oden Eriksson <oeriksson@mandriva.com> 4.25-3mdv2009.0
+ Revision: 283080
- fix #43685 (stunnel opens multiple times and killing the pid swollows the cpu)

* Tue Sep 09 2008 Oden Eriksson <oeriksson@mandriva.com> 4.25-2mdv2009.0
+ Revision: 283072
- fix deps
- sync with fedora

* Fri Sep 05 2008 Oden Eriksson <oeriksson@mandriva.com> 4.25-1mdv2009.0
+ Revision: 281121
- 4.25

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 4.24-3mdv2009.0
+ Revision: 265742
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon May 19 2008 David Walluck <walluck@mandriva.org> 4.24-2mdv2009.0
+ Revision: 209191
- move stunnel.cnf out of %%doc

* Mon May 19 2008 David Walluck <walluck@mandriva.org> 4.24-1mdv2009.0
+ Revision: 209138
- add stunnel-4.24-lib64.patch
- 4.24
- rediff lib64 patch
- update mdvconf patch

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sat Nov 10 2007 David Walluck <walluck@mandriva.org> 4.21-2mdv2008.1
+ Revision: 107380
- add 4.21 sources
- call %%{make} normally
- 4.21
- new lib policy
- split out static lib
- fix eol in INSTALL.WCE
- set pkglibdir to %%{_libdir}
- bins are now installed into %%{_bindir} and not %%{_sbindir} (by default)


* Mon Feb 05 2007 Oden Eriksson <oeriksson@mandriva.com> 4.20-1mdv2007.0
+ Revision: 116207
- 4.20
- drop obsolete and unmaintained patches
- fix the soname loading in client.c
- rediffed some patches
- synced a bit with fedora

* Tue Dec 12 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 4.15-2mdv2007.1
+ Revision: 95732
- fix build
- lib64 fixes
- fix configure script
- Import stunnel

* Thu Jun 08 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 4.15-1mdv2007.0
- 4.15
- regenerate P0

* Sun Nov 13 2005 Oden Eriksson <oeriksson@mandriva.com> 4.11-2mdk
- rebuilt against openssl-0.9.8a

* Wed Jul 13 2005 Oden Eriksson <oeriksson@mandriva.com> 4.11-1mdk
- 4.11 (Major bugfixes)
- rediff P0, merged pidfile location into P0

* Mon Apr 25 2005 Oden Eriksson <oeriksson@mandriva.com> 4.10-1mdk
- 4.10

* Sun Apr 17 2005 Oden Eriksson <oeriksson@mandriva.com> 4.09-1mdk
- 4.09
- rediffed P0
- use the %%mkrel macro
- fix requires-on-release

* Mon Feb 28 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.08-1mdk
- 4.08

* Mon Jan 03 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.07-1mdk
- 4.07

* Fri Dec 31 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.06-3mdk
- revert latest "lib64 fixes"

* Mon Dec 27 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.06-2mdk
- added P4 as an --with distcache rpmbuild switch (disabled per default)
- make it rpmbuildupdate aware
- misc spec file fixes

* Mon Dec 27 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.06-1mdk
- 4.06
- rediffed P0 & P1
- fix soname (P2) and do libifictions
- automake1.7
- fix default pidfile location (P3)
- enable ipv6
- misc spec file fixes

* Tue Aug 10 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 4.05-1mdk
- Release 4.05.
- Use automake1.4.

