%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-messaging
Version:        %(%{__python} -c 'from messaging import VERSION; print "%s.%s.%s" % VERSION')
Release:        1%{?dist}
Summary:        SMS encoder/decoder library
License:        GPL
Group:          Development
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-buildroot
BuildArch:      noarch

BuildRequires:  python-devel
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif

%description
Pure python SMS encoder/decoder library

%prep
%setup -q -n %{name}-%{version}

%build
%{__python} -c 'import setuptools; execfile("setup.py")' build

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install -O1 --skip-build --root %{buildroot} --prefix=%{_prefix}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%{python_sitelib}
%defattr(-,root,root,-)
%doc README

%changelog

* Tue Jan 24 2012 - Andrew Bird <ajb@spheresystems.co.uk> - 0.5.12
- New release

* Tue Aug 30 2011 - Andrew Bird <ajb@spheresystems.co.uk> - 0.5.11
- New release

* Mon Jun 06 2011 - Andrew Bird <ajb@spheresystems.co.uk> - 0.5.10
- Initial release - Spec file tested on Fedora 14 / 15 and OpenSUSE 11.4
