#
# spec file for package sslCertTool
#
# Copyright (c) 2016 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name:           sslCertTool
Version:        1.0.0
Release:        1
License:        GPL-2.0
Summary:        A Tool for generating SSL Certificates
Url:            https://github.com/mcalmer/sslCertTool
Group:          Productivity/Security
Source:         %{name}.tar.gz
BuildRequires:  python
BuildRequires:  python-setuptools
# for testing
BuildRequires:  openssl rpm-python python-argparse
%if 0%{?suse_version}
%py_requires
%endif
Requires:       openssl
Requires:       rpm-build
Requires:       rpm-python
Requires:       python-argparse
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%else
BuildArch:      noarch
%endif

%description
A Tool for generating SSL Certificates.

%prep
%setup -q -n %{name}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --prefix=%{_prefix} --root=$RPM_BUILD_ROOT
chmod a+x %{buildroot}%{python_sitelib}/certTool/gen-rpm.sh

%check
export PYTHONPATH=%{buildroot}%{python_sitelib}
export PATH=%{buildroot}%{_bindir}:$PATH
./mytest.sh

%files
%defattr(-,root,root)
%doc README.md LICENSE
%{_bindir}/cert-tool
%{python_sitelib}/*

%changelog

