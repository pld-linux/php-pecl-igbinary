#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	igbinary
Summary:	Replacement for the standard PHP serializer
Name:		%{php_name}-pecl-%{modname}
Version:	3.1.2
Release:	1
License:	BSD
Group:		Development/Languages/PHP
Source0:	https://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	34280e1609ef8e23f67fe3e690405787
Source2:	%{modname}.ini
URL:		https://pecl.php.net/package/igbinary
%{?with_tests:BuildRequires:	%{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:7.0
%{?with_tests:BuildRequires:	%{php_name}-pcre}
%{?with_tests:BuildRequires:	%{php_name}-session}
%{?with_tests:BuildRequires:	%{php_name}-simplexml}
%{?with_tests:BuildRequires:	%{php_name}-spl}
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Requires:	%{php_name}-session
Provides:	php(%{modname}) = %{version}
Obsoletes:	php-pecl-igbinary < 1.1.1-6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Igbinary is a drop in replacement for the standard PHP serializer.

Instead of time and space consuming textual representation, igbinary
stores php data structures in a compact binary form. Savings are
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

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
exec %{__make} test \
	PHP_EXECUTABLE=%{__php} \
%if "%php_major_version.%php_minor_version" >= "7.4"
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="simplexml session" \
%else
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="pcre spl simplexml session" \
%endif
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

xfail() {
	local t=$1
	test -f $t
	cat >> $t <<-EOF

	--XFAIL--
	Skip
	EOF
}

while read line; do
	t=${line##*\[}; t=${t%\]}
	xfail $t
done << 'EOF'
Test serializing multiple reference groups to the same empty array [tests/igbinary_067.phpt]
EOF

%build
phpize
%configure
%{__make}

# simple module load test
%{__php} -n -q \
	-dextension_dir=modules \
	-dextension=%{php_extensiondir}/pcre.so \
	-dextension=%{php_extensiondir}/spl.so \
	-dextension=%{php_extensiondir}/simplexml.so \
	-dextension=%{php_extensiondir}/session.so \
	-dextension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

%if %{with tests}
./run-tests.sh --show-diff
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir}}
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

%if "%php_major_version.%php_minor_version" >= "7.4"
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/01_%{modname}.ini
%else
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/session_%{modname}.ini
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING CREDITS NEWS README.md
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/*_%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so

%files devel
%defattr(644,root,root,755)
%doc igbinary.php
%{_includedir}/php/ext/%{modname}
