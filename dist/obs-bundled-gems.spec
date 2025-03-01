#
# spec file for package obs-bundled-gems
#
# Copyright (c) 2018 SUSE LINUX GmbH, Nuernberg, Germany.
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


Name:           obs-bundled-gems
Version:        2.10~pre
Release:        0
Summary:        The Open Build Service -- Bundled Gems
# The actual license is from the gems, but we take a more restrictive
# license to bundle them. Most are MIT anyway (TODO for Ana: check)
License:        GPL-2.0-only OR GPL-3.0-only
Group:          Productivity/Networking/Web/Utilities
Url:            http://www.openbuildservice.org
Source0:        Gemfile
Source1:        Gemfile.lock
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  cyrus-sasl-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  glibc-devel
BuildRequires:  libtool
BuildRequires:  libffi-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  make
BuildRequires:  mysql-devel
BuildRequires:  nodejs
BuildRequires:  openldap2-devel
BuildRequires:  python-devel
BuildRequires:  %{rb_default_ruby_suffix}-devel
BuildRequires:  %{rubygem bundler}
BuildRequires:  chrpath

BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
This package bundles all the gems required by the Open Build Service
to make it easier to deploy the obs-server package.

%define rake_version 13.0.1
%define rack_version 2.0.7

%package -n obs-api-deps
Summary:        Holding dependencies required to run the OBS frontend
Group:          Productivity/Networking/Web/Utilities
Requires:       build >= 20170315
Requires:       memcached >= 1.4
Requires:       mysql
Requires:       obs-bundled-gems = %{version}
Requires:       sphinx >= 2.1.8
Requires:       perl(GD)
Requires:       %{rubygem bundler)
Requires:       %{rubygem rake:%{rake_version}}
Requires:       %{rubygem rack:%{rack_version}}

%description -n obs-api-deps
To simplify splitting the test suite packages off the main package,
this package is just a meta package used to run and build obs-api

%files -n obs-api-deps
%doc README

%package -n obs-api-testsuite-deps
Summary:        Holding dependencies required to run frontend test suites
Group:          Productivity/Networking/Web/Utilities
Requires:       inst-source-utils
Requires:       nodejs
Requires:       obs-api-deps = %{version}

%description -n obs-api-testsuite-deps
To simplify splitting the test suite packages off the main package,
this package is just a meta package used to build obs-api testsuite

%files -n obs-api-testsuite-deps
%doc README

%prep
echo > README <<EOF
This package is just a meta package containing requires
EOF

cp %{S:0} %{S:1} .

%build
# copy gem files into cache
mkdir -p vendor/cache
cp %{_sourcedir}/vendor/cache/*.gem vendor/cache
export GEM_HOME=~/.gems
bundle config build.ffi --enable-system-libffi
bundle config build.mysql2 --with-cflags='%{optflags} -Wno-return-type'
bundle config build.nokogiri --use-system-libraries
bundle config build.sassc --disable-march-tune-native

%install
bundle --local --path %{buildroot}%_libdir/obs-api/

%define rb_default_path %(echo %{rb_default_ruby_abi} | sed -e 's?:?/?g')

# test that the rake and rack macros is still matching our Gemfile
test -f %{buildroot}%_libdir/obs-api/%{rb_default_path}/gems/rake-%{rake_version}/rake.gemspec
test -f %{buildroot}%_libdir/obs-api/%{rb_default_path}/gems/rack-%{rack_version}/rack.gemspec

# run gem clean up script
/usr/lib/rpm/gem_build_cleanup.sh %{buildroot}%_libdir/obs-api/ruby/*/

# Remove sources of extensions, we don't need them
rm -rf %{buildroot}%_libdir/obs-api/ruby/*/gems/*/ext/

# remove binaries with invalid interpreters
rm -rf %{buildroot}%_libdir/obs-api/ruby/*/gems/diff-lcs-*/bin

# remove spec / test files from gems as they shouldn't be shipped in gems anyway
# and often cause errors / warning in rpmlint
rm -rf %{buildroot}%_libdir/obs-api/ruby/*/gems/*/spec/
rm -rf %{buildroot}%_libdir/obs-api/ruby/*/gems/*/test/
# we do not verify signing of the gem
rm -rf %{buildroot}%_libdir/obs-api/ruby/*/gems/mousetrap-rails-*/gem-public_cert.pem

# remove prebuilt binaries causing broken dependencies
rm -rf %{buildroot}%_libdir/obs-api/ruby/*/gems/selenium-webdriver-*/lib/selenium/webdriver/firefox/native

# remove all gitignore files to fix rpmlint version-control-internal-file
find %{buildroot}%_libdir/obs-api -name .gitignore | xargs rm -rf

# fix interpreter in installed binaries
for bin in %{buildroot}%_libdir/obs-api/ruby/*/bin/*; do
  sed -i -e 's,/usr/bin/env ruby.%{rb_default_ruby_suffix},/usr/bin/ruby.%{rb_default_ruby_suffix},' $bin
done

# remove exec bit from all other files still containing /usr/bin/env - mostly helper scripts
find %{buildroot} -type f -print0 | xargs -0 grep -l /usr/bin/env | while read file; do
  chmod a-x $file
done

%files
%_libdir/obs-api

%changelog
