%define pemdir               %{_sysconfdir}/ssl/stunnel

%define major                0
%define libname              %mklibname %{name} %{major}
%define libname_devel        %mklibname %{name} -d
%define libname_static_devel %mklibname %{name} -d -s

Name:           stunnel
Version:        4.24
Release:        %mkrel 2
Summary:        Program that wraps normal socket connections with SSL/TLS
License:        GPL
Group:          System/Servers
URL:            http://www.stunnel.org/
Source0:        http://www.stunnel.org/download/stunnel/src/%{name}-%{version}.tar.gz
Source1:        http://www.stunnel.org/download/stunnel/src/%{name}-%{version}.tar.gz.asc
Source1:        http://www.stunnel.org/download/stunnel/src/%{name}-%{version}.tar.gz.sha1
Patch0:         stunnel-mdvconf.diff
Patch1:         stunnel-4.06-authpriv.patch
Patch2:         stunnel-soname.diff
Patch4:         stunnel-4.24-lib64.patch
BuildRequires:  libtool
BuildRequires:  automake1.7
BuildRequires:  autoconf2.5
BuildRequires:  openssl >= 0.9.5
BuildRequires:  openssl-devel >= 0.9.5
BuildRequires:  tcp_wrappers-devel
Requires:       openssl >= 0.9.5a
Requires:       tcp_wrappers
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The stunnel program is designed to work as SSL encryption wrapper between 
remote clients and local (inetd-startable) or remote servers. The concept is 
that having non-SSL aware daemons running on your system you can easily set 
them up to communicate with clients over secure SSL channels.

stunnel can be used to add SSL functionality to commonly used inetd daemons 
like POP-2, POP-3, and IMAP servers, to standalone daemons like NNTP, SMTP 
and HTTP, and in tunneling PPP over network sockets without changes to the 
source code.

%package -n %{libname}
Summary:        Shared library for stunnel
Group:          System/Libraries

%description -n %{libname}
The stunnel program is designed to work as SSL encryption wrapper between 
remote clients and local (inetd-startable) or remote servers. The concept is 
that having non-SSL aware daemons running on your system you can easily set 
them up to communicate with clients over secure SSL channels.

stunnel can be used to add SSL functionality to commonly used inetd daemons 
like POP-2, POP-3, and IMAP servers, to standalone daemons like NNTP, SMTP 
and HTTP, and in tunneling PPP over network sockets without changes to the 
source code.

This package contains the shared library for stunnel.

%package -n %{libname_devel}
Summary:        Development files for stunnel
Group:          Development/C
Requires:       %{libname} = %{version}-%{release}
Provides:       lib%{name}-devel = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}
Obsoletes:      %{libname}-devel < %{version}-%{release}

%description -n %{libname_devel}
The stunnel program is designed to work as SSL encryption wrapper between 
remote clients and local (inetd-startable) or remote servers. The concept is 
that having non-SSL aware daemons running on your system you can easily set 
them up to communicate with clients over secure SSL channels.

stunnel can be used to add SSL functionality to commonly used inetd daemons 
like POP-2, POP-3, and IMAP servers, to standalone daemons like NNTP, SMTP 
and HTTP, and in tunneling PPP over network sockets without changes to the 
source code.

This package contains development files for stunnel.

%package -n %{libname_static_devel}
Summary:        Static library for stunnel
Group:          Development/C
Requires:       %{libname_devel} = %{version}-%{release}
Provides:       lib%{name}-static-devel = %{version}-%{release}
Provides:       %{name}-static-devel = %{version}-%{release}

%description -n %{libname_static_devel}
The stunnel program is designed to work as SSL encryption wrapper between 
remote clients and local (inetd-startable) or remote servers. The concept is 
that having non-SSL aware daemons running on your system you can easily set 
them up to communicate with clients over secure SSL channels.

stunnel can be used to add SSL functionality to commonly used inetd daemons 
like POP-2, POP-3, and IMAP servers, to standalone daemons like NNTP, SMTP 
and HTTP, and in tunneling PPP over network sockets without changes to the 
source code.

This package contains the static library for stunnel.

%prep
%setup -q
%patch0 -p1 -b .confdir
%patch1 -p1 -b .authprv
%patch2 -p1 -b .soname
%patch4 -p1 -b .lib64

iconv -f iso-8859-1 -t utf-8 < doc/stunnel.fr.8 > doc/stunnel.fr.8_
mv doc/stunnel.fr.8_ doc/stunnel.fr.8
iconv -f iso-8859-2 -t utf-8 < doc/stunnel.pl.8 > doc/stunnel.pl.8_
mv doc/stunnel.pl.8_ doc/stunnel.pl.8

# XXX don't install /var/lib/stunnel
perl -ni -e '/INSTALL.*-m 1770 -g nogroup.*stunnel$/ or print' tools/Makefile.am

%{__perl} -pi -e 's/\r$//g' INSTALL.WCE

%{_bindir}/autoreconf -i -v -f

%build
%{configure2_5x} \
    --with-ssl=%{_prefix} \
    --enable-static \
    --enable-shared \
    --localstatedir=%{_var} \
    --with-tcp-wrappers \
    --with-ipv6
%{make} pkglibdir=%{_libdir}

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{pemdir} \
        %{buildroot}%{_var}/openssl/certs/trusted \
        %{buildroot}%{_var}/run/stunnel

# (oe) hack... don't generate the pem file
touch %{buildroot}%{pemdir}/stunnel.pem

%{makeinstall} docdir=`pwd`/doc-to-install pkglibdir=%{buildroot}%{_libdir}

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
%{__cp} -p tools/stunnel.cnf %{buildroot}%{_datadir}/%{name}/stunnel.cnf

# Move the translated man pages to the right subdirectories, and strip off the
# language suffixes.
for lang in fr pl ; do
        mkdir -p %{buildroot}%{_mandir}/${lang}/man8
        mv %{buildroot}%{_mandir}/man8/*.${lang}.8* %{buildroot}%{_mandir}/${lang}/man8/
        rename ".${lang}" "" %{buildroot}%{_mandir}/${lang}/man8/*
done

# cleanup
rm -f ./doc-to-install/INSTALL.W32
rm -f %{buildroot}%{pemdir}/*

%post
echo "To build a new pem, execute the following OpenSSL command:"
echo "    openssl req -new -x509 -days 365 -nodes \ "
echo "    -config %{_datadir}/%{name}/stunnel.cnf \ "
echo "    -out %{pemdir}/stunnel.pem -keyout %{pemdir}/stunnel.pem"
echo ""

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc doc-to-install/*
%{_bindir}/stunnel
%{_bindir}/stunnel3
%{_datadir}/%{name}/
%dir %{pemdir}
%dir %{_var}/run/stunnel
%dir %{_var}/openssl/certs/trusted
%{_mandir}/man8/stunnel.8.*
%lang(fr) %{_mandir}/fr/man8/stunnel.8*
%lang(pl) %{_mandir}/pl/man8/stunnel.8*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n %{libname_devel}
%defattr(-,root,root)
%{_libdir}/*.so
%{_libdir}/*.la

%files -n %{libname_static_devel}
%{_libdir}/*.a
