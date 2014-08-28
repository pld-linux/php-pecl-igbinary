#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	igbinary
Summary:	Replacement for the standard PHP serializer
Name:		%{php_name}-pecl-%{modname}
Version:	1.2.0
Release:	1
License:	BSD
Group:		Libraries
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	3755f17c73e7ef1fa022efd3b49d0573
Source2:	%{modname}.ini
URL:		http://pecl.php.net/package/igbinary
%{?with_tests:BuildRequires:	%{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:5.2.0
%{?with_tests:BuildRequires:	%{php_name}-pcre}
#%{?with_tests:BuildRequires:	%{php_name}-pecl-APC}
%{?with_tests:BuildRequires:	%{php_name}-session}
%{?with_tests:BuildRequires:	%{php_name}-simplexml}
%{?with_tests:BuildRequires:	%{php_name}-spl}
#BuildRequires:	php-pecl-apc-devel >= 3.1.7
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Requires:	%{php_name}-session
Provides:	php(%{modname}) = %{version}
Obsoletes:	php-pecl-igbinary < 1.1.1-6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Igbinary is a drop in replacement for the standard PHP serializer.

Instead of time and space consuming textual representation, igbinary
stores PHP data structures in a compact binary form. Savings are
significant when using memcached or similar memory based storages for
serialized data.

%package devel
Summary:	Igbinary developer files (header)
Group:		Development/Libraries
Requires:	%{php_name}-devel
# does not require base

%description devel
These are the files needed to compile programs using Igbinary

%prep
%setup -qc
mv %{modname}-*/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# APC required for test 045

# simple module load test
# without APC to ensure that can run without
%{__php} -n -q \
	-dextension_dir=modules \
	-dextension=%{php_extensiondir}/pcre.so \
	-dextension=%{php_extensiondir}/spl.so \
	-dextension=%{php_extensiondir}/simplexml.so \
	-dextension=%{php_extensiondir}/session.so \
	-dextension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

cat <<'EOF' > run-tests.sh
#!/bin/sh
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="pcre spl simplexml session" \
	RUN_TESTS_SETTINGS="-q $*"
EOF

chmod +x run-tests.sh
./run-tests.sh -w failed.log --show-out
test -f failed.log -a ! -s failed.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir}}
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

cp -p %{SOURCE2} $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/session_%{modname}.ini

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING CREDITS NEWS README.md
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/*%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/php/ext/%{modname}
