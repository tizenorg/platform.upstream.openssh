Name:           openssh
Version:        6.0p1
Release:        0
License:        BSD-3-Clause ; MIT
%define xversion 1.2.4.1
Summary:        Secure Shell Client and Server (Remote Login Program)
Url:            http://www.openssh.com/
Group:          Productivity/Networking/SSH
Source:         ftp://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-%{version}.tar.gz
Source1:        sshd.init
Source2:        sshd.pamd
Source8:        ssh-askpass
Source11:       sshd-gen-keys-start
Source12:       sshd.service
Source13:       sshd.socket
Source14:       sshd@.service
Patch0:         %{name}-5.9p1-sshd_config.diff
Patch2:         %{name}-5.9p1-pam-fix2.diff
Patch3:         %{name}-5.9p1-saveargv-fix.diff
Patch4:         %{name}-5.9p1-pam-fix3.diff
Patch5:         %{name}-5.9p1-gssapimitm.patch
Patch6:         %{name}-5.9p1-eal3.diff
Patch7:         %{name}-5.9p1-engines.diff
Patch8:         %{name}-5.9p1-blocksigalrm.diff
Patch9:         %{name}-5.9p1-send_locale.diff
Patch10:        %{name}-5.9p1-xauthlocalhostname.diff
Patch12:        %{name}-5.9p1-xauth.diff
Patch14:        %{name}-5.9p1-default-protocol.diff
Patch15:        %{name}-5.9p1-audit.patch
Patch16:        %{name}-5.9p1-pts.diff
Patch17:        %{name}-5.9p1-homechroot.patch
Patch18:        %{name}-5.9p1-sshconfig-knownhostschanges.diff
Patch19:        %{name}-5.9p1-host_ident.diff
Patch21:        openssh-nocrazyabicheck.patch
%define _appdefdir      %{_datadir}/X11/app-defaults
BuildRequires:  autoconf
BuildRequires:  openssl-devel
BuildRequires:  pam-devel
BuildRequires:  systemd
Requires:       /usr/bin/netstat
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Requires(pre):  pwdutils coreutils

%{!?_initddir:%global _initddir %{_initddir}}

%description
SSH (Secure Shell) is a program for logging into and executing commands
on a remote machine. It is intended to replace rsh (rlogin and rsh) and
provides openssl (secure encrypted communication) between two untrusted
hosts over an insecure network.

xorg-x11 (X Window System) connections and arbitrary TCP/IP ports can
also be forwarded over the secure channel.

%prep
%setup -q
%patch0
%patch2
%patch3
%patch4
%patch5
%patch6 -p1
%patch7 -p1
%patch8
%patch9
%patch10
%patch12
%patch14
%patch15 -p1
%patch16
%patch17
%patch18
%patch19 -p1
%patch21

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
    --with-privsep-path=/var/lib/empty \
    --with-sandbox=rlimit \
    --disable-strip \
    --with-xauth=%{_bindir}/xauth \
    --target=%{_target_cpu}-tizen-linux
#   --with-afs=/usr \
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot}/ install
install -d -m 755 %{buildroot}%{_sysconfdir}/pam.d
install -d -m 755 %{buildroot}%{_localstatedir}/lib/sshd
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pam.d/sshd
install -d -m 755 %{buildroot}%{_initddir}
install -m 755 %{SOURCE1} %{buildroot}%{_initddir}/sshd
# install shell script to automate the process of adding your public key to a remote machine
install -m 755 contrib/ssh-copy-id %{buildroot}%{_bindir}
install -m 644 contrib/ssh-copy-id.1 %{buildroot}%{_mandir}/man1
sed -e "s,@LIBEXEC@,%{_libexecdir},g" < %{SOURCE8} > %{buildroot}%{_libexecdir}/ssh/ssh-askpass
rm -f %{buildroot}%{_datadir}/Ssh.bin
sed -i -e s@/usr/libexec@%{_libexecdir}@g %{buildroot}%{_sysconfdir}/ssh/sshd_config
install -D -m 0755 %{SOURCE11} %{buildroot}%{_sbindir}/sshd-gen-keys-start
install -D -m 0644 %{SOURCE12} %{buildroot}%{_unitdir}/sshd.service
install -D -m 0644 %{SOURCE13} %{buildroot}%{_unitdir}/sshd.socket
install -D -m 0644 %{SOURCE14} %{buildroot}%{_unitdir}/sshd@.service

mkdir -p %{buildroot}/%{_unitdir}/multi-user.target.wants
ln -s ../sshd.service %{buildroot}/%{_unitdir}/multi-user.target.wants/sshd.service


rm -rf %{buildroot}/%{_mandir}/cat*
rm -rf %{buildroot}/%{_mandir}/man*



%pre
getent group sshd >/dev/null || %{_sbindir}/groupadd -o -r sshd
getent passwd sshd >/dev/null || %{_sbindir}/useradd -r -g sshd -d /var/lib/sshd -s /bin/false -c "SSH daemon" sshd


%docs_package

%files
%defattr(-,root,root)
%dir %attr(755,root,root)
%attr(0755,root,root) %dir %{_sysconfdir}/ssh
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ssh/moduli
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ssh/ssh_config
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/ssh/sshd_config
%attr(0644,root,root) %config %{_sysconfdir}/pam.d/sshd
%attr(0755,root,root) %config %{_initddir}/sshd
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
%{_unitdir}/multi-user.target.wants/*.service
%{_unitdir}/sshd.socket

%changelog
