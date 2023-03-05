%define _disable_rebuild_configure %nil

Summary:	Program that wraps normal socket connections with SSL/TLS
Name:		stunnel
Version:	5.69
Release:	1
License:	GPLv2
Group:		System/Servers
URL:		http://www.stunnel.org/
Source0:	https://github.com/mtrojnar/stunnel/archive/%{name}-%{version}.tar.gz
Source2:	stunnel.service
Source3:        stunnel.tmpfiles
#Patch0:		stunnel-5.60-compile.patch
BuildRequires:	pkgconfig(openssl)
BuildRequires:	tcp_wrappers-devel
Requires:	tcp_wrappers
Requires(pre):	openssl
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
%setup -qn %{name}-%{name}-%{version}
%autopatch -p1

%build

%configure \
    --with-threads=pthread \
    --with-ssl=%{_prefix} \
    --disable-static \
    --enable-shared

%make LDADD="-pie -Wl,-z,defs,-z,relro,-z,now"
#% make pkglibdir=%{_libdir}

%install
# (oe) hack... don't generate the pem file, and stunnel.conf
install -d %{buildroot}%{_sysconfdir}/%{name}
touch %{buildroot}%{_sysconfdir}/%{name}/stunnel.pem

%make_install docdir=/doc-to-install pkglibdir=%{_libdir}

install -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/stunnel.service
install -D -m 644 %{SOURCE3} %{buildroot}%{_prefix}/lib/tmpfiles.d/stunnel.conf

install -d %{buildroot}%{_var}/openssl/certs/trusted
install -d %{buildroot}%{_var}/run/stunnel
# install -d -m755 %{buildroot}/usr/var/lib/%{name}

mv %{buildroot}%{_sysconfdir}/%{name}/stunnel.conf-sample \
    %{buildroot}%{_sysconfdir}/%{name}/stunnel.conf

perl -pi \
    -e 's|chroot = .*|chroot = /run/stunnel|;' \
    -e 's|cert = .*|cert = /etc/pki/tls/certs/stunnel.pem|;' \
    -e 's|;key = .*|key = /etc/pki/tls/private//stunnel.pem|;' \
    %{buildroot}%{_sysconfdir}/%{name}/stunnel.conf

# cleanup
mv %{buildroot}/doc-to-install .
rm -f ./doc-to-install/INSTALL.W32
rm -f %{buildroot}%{_sysconfdir}/%{name}/stunnel.pem

%post
%_create_ssl_certificate stunnel
chmod a+w %{_var}/run/stunnel

%files
%doc doc-to-install/*
%{_bindir}/stunnel
%{_bindir}/stunnel3
%dir %{_var}/run/stunnel
%{_mandir}/man8/stunnel*.8.*
%config(noreplace) %{_sysconfdir}/%{name}/stunnel.conf
%{_unitdir}/stunnel.service
%{_prefix}/lib/tmpfiles.d/stunnel.conf
%{_libdir}/*.so
