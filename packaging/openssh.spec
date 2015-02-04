%define _appdefdir      %{_prefix}/share/X11/app-defaults
%define xversion 1.2.4.1

Name:           openssh
Version:        6.6p1
Release:        0
Summary:        Secure Shell Client and Server (Remote Login Program)
License:        BSD-3-Clause and MIT
Group:          System/Network
Url:            http://www.openssh.com/
Source:         ftp://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-%{version}.tar.gz
Source2:        sshd.pamd
Source8:        ssh-askpass
Source11:       sshd-gen-keys-start
Source12:       sshd.service
Source13:       sshd.socket
Source14:       sshd@.service
Source1001:     openssh.manifest

BuildRequires:  systemd
BuildRequires:  autoconf
BuildRequires:  openssl-devel
BuildRequires:  pam-devel
Requires:       /usr/bin/netstat
Requires:       pam-modules-extra
Requires(pre):  pwdutils coreutils

%{!?_initddir:%global _initddir %{_initrddir}}

%description
SSH (Secure Shell) is a program for logging into and executing commands
on a remote machine. It is intended to replace rsh (rlogin and rsh) and
provides openssl (secure encrypted communication) between two untrusted
hosts over an insecure network.

xorg-x11 (X Window System) connections and arbitrary TCP/IP ports can
also be forwarded over the secure channel.

%prep
%setup -q 
cp %{SOURCE1001} .

%build
autoreconf -fiv
PIEFLAGS="-fpie"
export CFLAGS="%{optflags} $PIEFLAGS -fstack-protector"
export CXXFLAGS="%{optflags} $PIEFLAGS -fstack-protector"
export LDFLAGS="-pie"
%configure \
    --with-ssl-engine \
    --sysconfdir=%{_sysconfdir}/ssh \
    --libexecdir=%{_libexecdir}/ssh \
    --with-pam \
    --without-lastlog \
    --with-privsep-path=%{_localstatedir}/lib/empty \
    --with-sandbox=rlimit \
    --disable-strip \
    --with-xauth=%{_prefix}/bin/xauth \
    --target=%{_target_cpu}-tizen-linux
%__make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot}/ install
install -d -m 755 %{buildroot}%{_sysconfdir}/pam.d
install -d -m 755 %{buildroot}%{_localstatedir}/lib/sshd
install -m 644 %{S:2} %{buildroot}%{_sysconfdir}/pam.d/sshd
# install shell script to automate the process of adding your public key to a remote machine
install -m 755 contrib/ssh-copy-id %{buildroot}%{_bindir}
install -m 644 contrib/ssh-copy-id.1 %{buildroot}%{_mandir}/man1
sed -e "s,@LIBEXEC@,%{_libexecdir},g" < %{S:8} > %{buildroot}%{_libexecdir}/ssh/ssh-askpass
rm -f %{buildroot}%{_datadir}/Ssh.bin
sed -i -e s@/usr/libexec@%{_libexecdir}@g %{buildroot}%{_sysconfdir}/ssh/sshd_config

install -D -m 0755 %{SOURCE11} %{buildroot}%{_sbindir}/sshd-gen-keys-start
# systemd
install -D -m 0644 %{SOURCE12} %{buildroot}%{_unitdir}/sshd.service
install -D -m 0644 %{SOURCE13} %{buildroot}%{_unitdir}/sshd.socket
install -D -m 0644 %{SOURCE14} %{buildroot}%{_unitdir}/sshd@.service

mkdir -p %{buildroot}/%{_unitdir}/sockets.target.wants
ln -s ../sshd.socket %{buildroot}/%{_unitdir}/sockets.target.wants/sshd.socket

rm -rf %{buildroot}/%{_mandir}/cat*
rm -rf %{buildroot}/%{_mandir}/man*

%pre
getent group sshd >/dev/null || %{_sbindir}/groupadd -o -r sshd
getent passwd sshd >/dev/null || %{_sbindir}/useradd -r -g sshd -d %{_localstatedir}/lib/sshd -s /bin/false -c "SSH daemon" sshd

%files
%manifest %{name}.manifest
%defattr(-,root,root)
%dir %attr(755,root,root) %{_localstatedir}/lib/sshd
%attr(0755,root,root) %dir %{_sysconfdir}/ssh
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ssh/moduli
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ssh/ssh_config
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/ssh/sshd_config
%attr(0644,root,root) %config %{_sysconfdir}/pam.d/sshd
%attr(0755,root,root) %{_bindir}/ssh
%{_bindir}/scp
%{_bindir}/sftp
%{_bindir}/slogin
%{_bindir}/ssh-*
%{_sbindir}/*
%attr(0755,root,root) %dir %{_libexecdir}/ssh
%attr(0755,root,root) %{_libexecdir}/ssh/sftp-server
%attr(0755,root,root) %{_libexecdir}/ssh/ssh-keysign
%attr(0755,root,root) %{_libexecdir}/ssh/ssh-pkcs11-helper
%attr(0755,root,root) %{_libexecdir}/ssh/ssh-askpass
%{_sbindir}/sshd-gen-keys-start
%{_unitdir}/sshd.service
%{_unitdir}/sshd@.service
%{_unitdir}/sockets.target.wants/*.socket
%{_unitdir}/sshd.socket

%changelog
