#
# spec file for package obs-server
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


%if 0%{?fedora}
%global sbin /usr/sbin
%else
%global sbin /sbin
%endif

%if 0%{?fedora} || 0%{?rhel}
%global apache_user apache
%global apache_group apache
%else
%global apache_user wwwrun
%global apache_group www
%endif

%define secret_key_file /srv/www/obs/api/config/secret.key
%define obs_backend_data_dir /srv/obs

%if ! %{defined _restart_on_update_reload}
%define _restart_on_update_reload() (\
	test "$YAST_IS_RUNNING" = instsys && exit 0\
	test -f /etc/sysconfig/services -a \\\
	     -z "$DISABLE_RESTART_ON_UPDATE" && . /etc/sysconfig/services\
	test "$DISABLE_RESTART_ON_UPDATE" = yes -o \\\
	     "$DISABLE_RESTART_ON_UPDATE" = 1 && exit 0\
	%{?*:/usr/bin/systemctl force-reload %{*}}\
	) || : %{nil}

%define service_del_postun(fnr) \
test -n "$FIRST_ARG" || FIRST_ARG="$1"						\
if [ "$FIRST_ARG" -ge 1 ]; then							\
	# Package upgrade, not uninstall					\
	if [ -x /usr/bin/systemctl ]; then					\
		/usr/bin/systemctl daemon-reload || :				\
		%{expand:%%_restart_on_update%{-f:_force}%{!-f:%{-n:_never}}%{!-f:%{!-n:%{-r:_reload}}} %{?*}}  \
	fi									\
else # package uninstall							\
	for service in %{?*} ; do						\
		sysv_service="${service%.*}"					\
		rm -f "/var/lib/systemd/migrated/$sysv_service" || :		\
	done									\
	if [ -x /usr/bin/systemctl ]; then					\
		/usr/bin/systemctl daemon-reload || :				\
	fi									\
fi										\
%{nil}

%endif

%if ! %{defined _fillupdir}
  %define _fillupdir %{_localstatedir}/adm/fillup-templates
%endif

%if 0%{?suse_version} >= 1315
%define reload_on_update() %{?nil:
	test -n "$FIRST_ARG" || FIRST_ARG=$1
	if test "$FIRST_ARG" -ge 1 ; then
	   test -f /etc/sysconfig/services && . /etc/sysconfig/services
	   if test "$YAST_IS_RUNNING" != "instsys" -a "$DISABLE_RESTART_ON_UPDATE" != yes ; then
	      test -x /bin/systemctl && /bin/systemctl daemon-reload >/dev/null 2>&1 || :
	      for service in %{?*} ; do
		 test -x /bin/systemctl && /bin/systemctl reload $service >/dev/null 2>&1 || :
	      done
	   fi
	fi
	%nil
}
%endif

%global obs_api_support_scripts obs-api-support.target obs-clockwork.service obs-delayedjob-queue-consistency_check.service obs-delayedjob-queue-default.service obs-delayedjob-queue-issuetracking.service obs-delayedjob-queue-mailers.service obs-delayedjob-queue-project_log_rotate.service obs-delayedjob-queue-releasetracking.service obs-delayedjob-queue-staging.service obs-delayedjob-queue-sphinx-indexing.service obs-sphinx.service

Name:           obs-server
Summary:        The Open Build Service -- Server Component
License:        GPL-2.0-only OR GPL-3.0-only
Group:          Productivity/Networking/Web/Utilities
Version:        2.10~pre
Release:        0
Url:            http://www.openbuildservice.org
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source0:        open-build-service-%version.tar.xz
BuildRequires:  python-devel
# make sure this is in sync with the RAILS_GEM_VERSION specified in the
# config/environment.rb of the various applications.
# atm the obs rails version patch above unifies that setting among the applications
# also see requires in the obs-server-api sub package
BuildRequires:  /usr/bin/xmllint
BuildRequires:  openssl
BuildRequires:  perl-BSSolv >= 0.28
BuildRequires:  perl-Compress-Zlib
BuildRequires:  perl-Diff-LibXDiff
BuildRequires:  perl-File-Sync >= 0.10
BuildRequires:  perl-JSON-XS
BuildRequires:  perl-Net-SSLeay
BuildRequires:  perl-Socket-MsgHdr
BuildRequires:  perl-TimeDate
BuildRequires:  perl-XML-Parser
BuildRequires:  perl-XML-Simple
BuildRequires:  perl-XML-Structured
BuildRequires:  perl-YAML-LibYAML
BuildRequires:  procps
BuildRequires:  timezone
BuildRequires:  perl(Devel::Cover)
BuildRequires:  perl(Test::Simple) > 1
PreReq:         /usr/sbin/useradd /usr/sbin/groupadd
BuildArch:      noarch
Requires(pre):  obs-common
Requires:       build >= 20191114
Requires:       perl-BSSolv >= 0.28
Requires:       perl(Date::Parse)
# Required by source server
Requires:       diffutils
PreReq:         git-core
Requires:       patch
Requires:       createrepo_c
Recommends:     cron logrotate
# zsync for appimage signing
Recommends:     zsync

Obsoletes:      obs-devel
Provides:       obs-devel

BuildRequires:  xz

%if 0%{?suse_version:1}
BuildRequires:  fdupes
PreReq:         %insserv_prereq permissions pwdutils
%endif

%if 0%{?suse_version:1}
Recommends:     yum yum-metadata-parser repoview dpkg
Recommends:     deb >= 1.5
Recommends:     lvm2
Recommends:     openslp-server
Recommends:     obs-signd
Recommends:     inst-source-utils
Recommends:     perl-Diff-LibXDiff
%else
Requires:       dpkg
Requires:       yum
Requires:       yum-metadata-parser
%endif
Requires:       perl-Compress-Zlib
Requires:       perl-File-Sync >= 0.10
Requires:       perl-JSON-XS
Requires:       perl-Net-SSLeay
Requires:       perl-Socket-MsgHdr
Requires:       perl-XML-Parser
Requires:       perl-XML-Simple
Requires:       perl-XML-Structured
Requires:       perl-YAML-LibYAML

Obsoletes:      obs-productconverter < 2.9
Obsoletes:      obs-source_service < 2.9
Provides:       obs-productconverter = %version
Provides:       obs-source_service = %version

Recommends:     obs-service-download_url
Recommends:     obs-service-verify_file
%if 0%{?suse_version} >= 1550
Requires:       insserv-compat
%endif

BuildRequires:  systemd-rpm-macros

%{?systemd_requires}

%description
The Open Build Service (OBS) backend is used to store all sources and binaries. It also
calculates the need for new build jobs and distributes it.

%package -n obs-worker
Requires(pre):  obs-common
Requires:       cpio
Requires:       curl
Requires:       perl-Compress-Zlib
Requires:       perl-TimeDate
Requires:       perl-XML-Parser
Requires:       screen
# for build script
Requires:       psmisc
# For runlevel script:
Requires:       curl
Recommends:     openslp lvm2
Requires:       bash
Requires:       binutils
Requires:       bsdtar
Summary:        The Open Build Service -- Build Host Component
Group:          Productivity/Networking/Web/Utilities
Requires:       util-linux >= 2.16
# the following may not even exist depending on the architecture
Recommends:     powerpc32
%if 0%{?suse_version} >= 1550
Requires:       insserv-compat
%endif

%description -n obs-worker
This is the obs build host, to be installed on each machine building
packages in this obs installation.  Install it alongside obs-server to
run a local playground test installation.

%package -n obs-common
Summary:        The Open Build Service -- base configuration files
Group:          Productivity/Networking/Web/Utilities
Requires(pre):  shadow
%if 0%{?suse_version}
PreReq:         %fillup_prereq
%endif

%description -n obs-common
This is a package providing basic configuration files.

%package -n obs-api
Summary:        The Open Build Service -- The API and WEBUI
Group:          Productivity/Networking/Web/Utilities
%if 0%{?suse_version}
Requires(pre):  obs-common
%endif
%if 0%{?suse_version} >= 1330
Requires(pre):  group(www)
%endif

# For apache
Requires:       apache2
Requires:       apache2-mod_xforward
Requires:       %{rubygem passenger}
Requires:       rubygem-passenger-apache2
Conflicts:      memcached < 1.4

Requires:       %{rb_default_ruby_suffix}
# for test suite:
BuildRequires:  createrepo_c
BuildRequires:  curl
BuildRequires:  netcfg
# write down dependencies for production
BuildRequires:  obs-api-testsuite-deps
Requires:       ghostscript-fonts-std
Requires:       obs-api-deps = %{version}
Requires:       obs-bundled-gems = %{version}

%description -n obs-api
This is the API server instance, and the web client for the
OBS.

%package -n obs-utils
Summary:        The Open Build Service -- utilities
Group:          Productivity/Networking/Web/Utilities
Requires:       build
Requires:       osc

%description -n obs-utils
obs_project_update is a tool to copy a packages of a project from one obs to another

%package -n obs-tests-appliance
Summary:        The Open Build Service -- Test cases for installed appliances
Group:          Productivity/Networking/Web/Utilities
Requires:       obs-api = %{version}
Requires:       obs-server = %{version}
Requires:       perl(Test::Most)

%description -n obs-tests-appliance
This package contains test cases for testing a installed appliances.
 Test cases can be for example:
 * checks for setup-appliance.sh
 * checks if database setup worked correctly
 * checks if required service came up properly

%package -n obs-cloud-uploader
Summary:        The Open Build Service -- Image Cloud Uploader
Group:          Productivity/Networking/Web/Utilities
Requires:       aws-cli
Requires:       azure-cli
Requires:       obs-server
%if 0%{?suse_version} > 1315
Requires:       python3-ec2uploadimg
%else
Requires:       python-ec2uploadimg
%endif

%description -n obs-cloud-uploader
This package contains all the necessary tools for upload images to the cloud.

#--------------------------------------------------------------------------------
%prep
%setup -q -n open-build-service-%version

# We don't need our docker files in our packages
rm -r src/api/docker-files

# drop build script, we require the installed one from own package
rm -rf src/backend/build

find -name .keep -o -name .gitignore | xargs rm -rf

%build
export DESTDIR=$RPM_BUILD_ROOT

pushd src/api
# configure to the bundled gems
bundle --local --path %_libdir/obs-api/
popd

#
# generate apidocs
#
make

%install
export DESTDIR=$RPM_BUILD_ROOT

%if 0%{?suse_version} < 1300
  perl -p -i -e 's/^APACHE_VHOST_CONF=.*/APACHE_VHOST_CONF=obs-apache2.conf/' Makefile.include
%endif

%if 0%{?fedora} || 0%{?rhel}
  # Fedora use different user:group for apache
  perl -p -i -e 's/^APACHE_USER=.*/APACHE_USER=apache/' Makefile.include
  perl -p -i -e 's/^APACHE_GROUP=.*/APACHE_GROUP=apache/' Makefile.include
%endif

export OBS_VERSION="%{version}"
DESTDIR=%{buildroot} make install FILLUPDIR=%{_fillupdir}
if [ -f %{_sourcedir}/open-build-service.obsinfo ]; then
    sed -n -e 's/commit: \(.\+\)/\1/p' %{_sourcedir}/open-build-service.obsinfo > %{buildroot}/srv/www/obs/api/last_deploy
else
    echo "" > %{buildroot}/srv/www/obs/api/last_deploy
fi
#
# turn duplicates into hard links
#
# There's dupes between webui and api:
%if 0%{?suse_version}
%fdupes $RPM_BUILD_ROOT/srv/www/obs
%endif

# drop testcases for now
rm -rf %{buildroot}/srv/www/obs/api/spec

# fail when Makefiles created a directory
if ! test -L %{buildroot}/usr/lib/obs/server/build; then
  echo "/usr/lib/obs/server/build is not a symlink!"
  exit 1
fi

install -m 755 $RPM_BUILD_DIR/open-build-service-%version/dist/clouduploader.rb $RPM_BUILD_ROOT/%{_bindir}/clouduploader
mkdir -p $RPM_BUILD_ROOT/etc/obs/cloudupload
install -m 644 $RPM_BUILD_DIR/open-build-service-%version/dist/ec2utils.conf.example $RPM_BUILD_ROOT/etc/obs/cloudupload/.ec2utils.conf
mkdir -p $RPM_BUILD_ROOT/etc/obs/cloudupload/.aws
install -m 644 $RPM_BUILD_DIR/open-build-service-%version/dist/aws_credentials.example $RPM_BUILD_ROOT/etc/obs/cloudupload/.aws/credentials

# Link the assets without hash to make them accessible for third party tools like the pattern library
pushd $RPM_BUILD_ROOT/srv/www/obs/api/public/assets/webui/
ln -sf application-*.js application.js
ln -sf application-*.css application.css
popd

%check
%if 0%{?disable_obs_test_suite}
echo "WARNING:"
echo "WARNING: OBS test suite got skipped!"
echo "WARNING:"
exit 0
%endif

export DESTDIR=$RPM_BUILD_ROOT
# check installed backend
pushd $RPM_BUILD_ROOT/usr/lib/obs/server/
rm -rf build
ln -sf /usr/lib/build build # just for %%check, it is a %%ghost
popd

# run in build environment
pushd src/backend/
rm -rf build
ln -sf /usr/lib/build build
popd

####
# start backend testing
pushd $RPM_BUILD_ROOT/usr/lib/obs/server/
%if 0%{?disable_obs_backend_test_suite:1} < 1
# TODO: move syntax check to backend test suite
for i in bs_*; do
  perl -wc "$i"
done
bash $RPM_BUILD_DIR/open-build-service-%version/src/backend/testdata/test_dispatcher || exit 1
popd

make -C src/backend test
%endif

####
# start api testing
#
%if 0%{?disable_obs_frontend_test_suite:1} < 1
make -C src/api test
%endif

####
# distribution tests
%if 0%{?disable_obs_dist_test_suite:1} < 1
make -C dist test
%endif

%pre
getent passwd obsservicerun >/dev/null || \
    /usr/sbin/useradd -r -g obsrun -d /usr/lib/obs -s %{sbin}/nologin \
    -c "User for the build service source service" obsservicerun

%service_add_pre obsscheduler.service
%service_add_pre obssrcserver.service
%service_add_pre obsrepserver.service
%service_add_pre obspublisher.service
%service_add_pre obssigner.service
%service_add_pre obsservicedispatch.service
%service_add_pre obsservice.service
%service_add_pre obsdeltastore.service
%service_add_pre obsdispatcher.service
%service_add_pre obsdodup.service
%service_add_pre obsgetbinariesproxy.service
%service_add_pre obswarden.service
%service_add_pre obsnotifyforward.service
%service_add_pre obsredis.service

# make sure logfiles belong to the obsrun user
if [ -f /etc/sysconfig/obs-server ] ; then
    . /etc/sysconfig/obs-server
fi
for i in deltastore dispatcher dodup obsgetbinariesproxy publisher rep_server servicedispatch signer src_server warden ; do
    LOG=${OBS_LOG_DIR:=/srv/obs/log}/$i.log
    test -f $LOG && chown obsrun:obsrun $LOG
done
for i in src_service ; do
    LOG=${OBS_LOG_DIR:=/srv/obs/log}/$i.log
    test -f $LOG && chown obsservicerun:obsrun $LOG
done

exit 0

# create user and group in advance of obs-server
%pre -n obs-common
getent group obsrun >/dev/null || /usr/sbin/groupadd -r obsrun
getent passwd obsrun >/dev/null || \
    /usr/sbin/useradd -r -g obsrun -d /usr/lib/obs -s %{sbin}/nologin \
    -c "User for build service backend" obsrun
%service_add_pre obsstoragesetup.service
exit 0

%pre -n obs-worker
%service_add_pre obsworker.service

%pre -n obs-cloud-uploader
%service_add_pre obsclouduploadworker.service
%service_add_pre obsclouduploadserver.service

%preun
%service_del_preun obsscheduler.service
%service_del_preun obssrcserver.service
%service_del_preun obsrepserver.service
%service_del_preun obspublisher.service
%service_del_preun obssigner.service
%service_del_preun obsservicedispatch.service
%service_del_preun obsservice.service
%service_del_preun obsdeltastore.service
%service_del_preun obsdispatcher.service
%service_del_preun obsdodup.service
%service_del_preun obsgetbinariesproxy.service
%service_del_preun obswarden.service
%service_del_preun obsnotifyforward.service
%service_del_preun obsredis.service

%preun -n obs-common
%service_del_preun obsstoragesetup.service

%preun -n obs-worker
%service_del_preun obsworker.service

%preun -n obs-cloud-uploader
%service_del_preun obsclouduploadworker.service
%service_del_preun obsclouduploadserver.service

%preun -n obs-api
%service_del_preun %{obs_api_support_scripts}

%post
%service_add_post obsscheduler.service
%service_add_post obssrcserver.service
%service_add_post obsrepserver.service
%service_add_post obspublisher.service
%service_add_post obssigner.service
%service_add_post obsservicedispatch.service
%service_add_post obsservice.service
%service_add_post obsdeltastore.service
%service_add_post obsdispatcher.service
%service_add_post obsdodup.service
%service_add_post obsgetbinariesproxy.service
%service_add_post obswarden.service
%service_add_post obsnotifyforward.service
%service_add_post obsredis.service

%post -n obs-worker
%service_add_post obsworker.service

%post -n obs-cloud-uploader
%service_add_post obsclouduploadworker.service
%service_add_post obsclouduploadserver.service

%posttrans
[ -d /srv/obs ] || install -d -o obsrun -g obsrun /srv/obs
# this changes from directory to symlink. rpm can not handle this itself.
if [ -e /usr/lib/obs/server/build -a ! -L /usr/lib/obs/server/build ]; then
  rm -rf /usr/lib/obs/server/build
fi
if [ ! -e /usr/lib/obs/server/build ]; then
  ln -sf ../../build /usr/lib/obs/server/build
fi

%postun
%service_del_postun -r obsscheduler.service
%service_del_postun -r obssrcserver.service
%service_del_postun -r obsrepserver.service
%service_del_postun -r obspublisher.service
%service_del_postun -r obssigner.service
%service_del_postun -r obsservicedispatch.service
%service_del_postun -r obsservice.service
%service_del_postun -r obsdeltastore.service
%service_del_postun -r obsdispatcher.service
%service_del_postun -r obsdodup.service
%service_del_postun -r obsgetbinariesproxy.service
%service_del_postun -r obswarden.service
%service_del_postun -r obsnotifyforward.service
%service_del_postun -r obsredis.service
# cleanup empty directory just in case
rmdir /srv/obs 2> /dev/null || :

%postun -n obs-common
# NOT used on purpose: restart_on_update obsstoragesetup
# This is just run once on boot
%service_del_postun -n obsstoragesetup.service

%postun -n obs-worker
# NOT used on purpose: restart_on_update obsworker
# This can cause problems when building chroot
# and bs_worker is anyway updating itself at runtime based on server code
%service_del_postun -n obsworker.service

%postun -n obs-cloud-uploader
%service_del_postun -r obsclouduploadworker.service
%service_del_postun -r obsclouduploadserver.service

%verifyscript -n obs-server
%verify_permissions

%pre -n obs-api
getent passwd obsapidelayed >/dev/null || \
  /usr/sbin/useradd -r -s /bin/bash -c "User for build service api delayed jobs" -d /srv/www/obs/api -g www obsapidelayed
%service_add_pre %{obs_api_support_scripts}

# On upgrade keep the values for the %post script
if [ "$1" == 2 ]; then
  # Cannot use "sytemctl is-enabled obsapidelayed.service" here
  # as it throws an error like "Can't determine current runlevel"
  if [ -e /etc/init.d/rc3.d/S50obsapidelayed ];then
    touch %{_rundir}/enable_obs-api-support.target
  fi
  if systemctl --quiet is-active  obsapidelayed.service;then
    touch %{_rundir}/start_obs-api-support.target
    systemctl stop    obsapidelayed.service
    systemctl disable obsapidelayed.service
  fi
fi

%post -n obs-common
%service_add_post obsstoragesetup.service
%{fillup_and_insserv -n obs-server}

%post -n obs-api
if [ -e /srv/www/obs/frontend/config/database.yml ] && [ ! -e /srv/www/obs/api/config/database.yml ]; then
  cp /srv/www/obs/frontend/config/database.yml /srv/www/obs/api/config/database.yml
fi
for i in production.rb ; do
  if [ -e /srv/www/obs/frontend/config/environments/$i ] && [ ! -e /srv/www/obs/api/config/environments/$i ]; then
    cp /srv/www/obs/frontend/config/environments/$i /srv/www/obs/api/config/environments/$i
  fi
done

if [ ! -s %{secret_key_file} ]; then
  pushd /srv/www/obs/api
  RAILS_ENV=production bin/rails secret > %{secret_key_file}
  popd
fi
chmod 0640 %{secret_key_file}
chown root.www %{secret_key_file}

# update config
sed -i -e 's,[ ]*adapter: mysql$,  adapter: mysql2,' /srv/www/obs/api/config/database.yml
touch /srv/www/obs/api/log/production.log
chown %{apache_user}:%{apache_group} /srv/www/obs/api/log/production.log

%restart_on_update memcached
%service_add_post %{obs_api_support_scripts}
# We need to touch the last_deploy file in the post hook
# to update the timestamp which we use to display the
# last deployment time in the API
touch /srv/www/obs/api/last_deploy || true

# Upgrading from SysV obsapidelayed.service to systemd obs-api-support.target
# This must be done after %%service_add_post. Otherwise the distribution preset is
# take, which is disabled in case of obs-api-support.target
if [ -e %{_rundir}/enable_obs-api-support.target ];then
  systemctl enable obs-api-support.target
  rm %{_rundir}/enable_obs-api-support.target
fi
if [ -e %{_rundir}/start_obs-api-support.target ];then
  systemctl start  obs-api-support.target
  rm %{_rundir}/start_obs-api-support.target
fi

%postun -n obs-api
%insserv_cleanup
%service_del_postun %{obs_api_support_scripts}
%service_del_postun -r apache2

%files
%defattr(-,root,root)
%doc dist/{README.UPDATERS,README.SETUP} docs/openSUSE.org.xml ReleaseNotes-* README.md COPYING AUTHORS
%dir /etc/slp.reg.d
%dir /usr/lib/obs
%dir /usr/lib/obs/server
%config(noreplace) /etc/logrotate.d/obs-server
%{_unitdir}/obsscheduler.service
%{_unitdir}/obssrcserver.service
%{_unitdir}/obsrepserver.service
%{_unitdir}/obspublisher.service
%{_unitdir}/obssigner.service
%{_unitdir}/obsservicedispatch.service
%{_unitdir}/obsdeltastore.service
%{_unitdir}/obsdispatcher.service
%{_unitdir}/obsdodup.service
%{_unitdir}/obsgetbinariesproxy.service
%{_unitdir}/obswarden.service
%{_unitdir}/obsnotifyforward.service
%{_unitdir}/obsredis.service
/usr/sbin/obs_admin
/usr/sbin/obs_serverstatus
/usr/sbin/obsscheduler
/usr/sbin/rcobsdispatcher
/usr/sbin/rcobspublisher
/usr/sbin/rcobsrepserver
/usr/sbin/rcobsscheduler
/usr/sbin/rcobssrcserver
/usr/sbin/rcobswarden
/usr/sbin/rcobsdodup
/usr/sbin/rcobsgetbinariesproxy
/usr/sbin/rcobsdeltastore
/usr/sbin/rcobsservicedispatch
/usr/sbin/rcobssigner
/usr/sbin/rcobsnotifyforward
/usr/sbin/rcobsredis
/usr/lib/obs/server/plugins
/usr/lib/obs/server/BSDispatcher
/usr/lib/obs/server/BSRepServer
/usr/lib/obs/server/BSSched
/usr/lib/obs/server/BSSrcServer
/usr/lib/obs/server/BSPublisher
/usr/lib/obs/server/*.pm
/usr/lib/obs/server/BSConfig.pm.template
/usr/lib/obs/server/DESIGN
/usr/lib/obs/server/License
/usr/lib/obs/server/README
/usr/lib/obs/server/bs_admin
/usr/lib/obs/server/bs_cleanup
/usr/lib/obs/server/bs_archivereq
/usr/lib/obs/server/bs_check_consistency
/usr/lib/obs/server/bs_deltastore
/usr/lib/obs/server/bs_servicedispatch
/usr/lib/obs/server/bs_dodup
/usr/lib/obs/server/bs_getbinariesproxy
/usr/lib/obs/server/bs_mergechanges
/usr/lib/obs/server/bs_mkarchrepo
/usr/lib/obs/server/bs_notar
/usr/lib/obs/server/bs_regpush
/usr/lib/obs/server/bs_dispatch
/usr/lib/obs/server/bs_publish
/usr/lib/obs/server/bs_repserver
/usr/lib/obs/server/bs_sched
/usr/lib/obs/server/bs_serverstatus
/usr/lib/obs/server/bs_srcserver
/usr/lib/obs/server/bs_worker
/usr/lib/obs/server/bs_signer
/usr/lib/obs/server/bs_warden
/usr/lib/obs/server/bs_redis
/usr/lib/obs/server/bs_notifyforward
/usr/lib/obs/server/worker
/usr/lib/obs/server/worker-deltagen.spec
/usr/lib/obs/server/obs-ptf.spec
%config(noreplace) /usr/lib/obs/server/BSConfig.pm
%config(noreplace) /etc/slp.reg.d/*
# created via %%post, since rpm fails otherwise while switching from
# directory to symlink
%ghost /usr/lib/obs/server/build
%attr(0775, obsrun, obsrun) %dir %{obs_backend_data_dir}
%attr(0755, obsrun, obsrun) %dir %{obs_backend_data_dir}/build
%attr(0755, obsrun, obsrun) %dir %{obs_backend_data_dir}/events
%attr(0700, root, root)     %dir %{obs_backend_data_dir}/gnupg
%attr(0755, obsrun, obsrun) %dir %{obs_backend_data_dir}/info
%attr(0755, obsrun, obsrun) %dir %{obs_backend_data_dir}/jobs
%attr(0775, obsrun, obsrun) %dir %{obs_backend_data_dir}/log
%attr(0755, obsrun, obsrun) %dir %{obs_backend_data_dir}/projects
%attr(0775, obsrun, obsrun) %dir %{obs_backend_data_dir}/run
%attr(0755, obsservicerun, obsrun) %dir %{obs_backend_data_dir}/service
%attr(0755, obsservicerun, obsrun) %dir %{obs_backend_data_dir}/service/log


# formerly obs-source_service
%{_unitdir}/obsservice.service
%config(noreplace) /etc/logrotate.d/obs-source_service
%if 0%{?suse_version} >= 1550
%dir /etc/cron.d
%endif
%config(noreplace) /etc/cron.d/cleanup_scm_cache
/usr/sbin/rcobsservice
/usr/lib/obs/server/bs_service
/usr/lib/obs/server/call-service-in-docker.sh
/usr/lib/obs/server/run-service-containerized
/usr/lib/obs/server/cleanup_scm_cache

# formerly obs-productconverter
/usr/bin/obs_productconvert
/usr/lib/obs/server/bs_productconvert

# add obsservicerun user into docker group if docker
# gets installed
%triggerin -n obs-server -- docker
usermod -a -G docker obsservicerun

%files -n obs-worker
%defattr(-,root,root)
%{_unitdir}/obsworker.service
/usr/sbin/obsworker
/usr/sbin/rcobsworker

%files -n obs-api
%defattr(-,root,root)
%doc dist/{README.UPDATERS,README.SETUP} docs/openSUSE.org.xml ReleaseNotes-* README.md COPYING AUTHORS
/srv/www/obs/overview

/srv/www/obs/api/config/thinking_sphinx.yml.example
%config(noreplace) /srv/www/obs/api/config/thinking_sphinx.yml
%attr(-,%{apache_user},%{apache_group}) %config(noreplace) /srv/www/obs/api/config/production.sphinx.conf

%dir /srv/www/obs
%dir /srv/www/obs/api
%dir /srv/www/obs/api/config
%config(noreplace) /srv/www/obs/api/config/cable.yml
%config(noreplace) /srv/www/obs/api/config/feature.yml
%config(noreplace) /srv/www/obs/api/config/puma.rb
%config(noreplace) /srv/www/obs/api/config/secrets.yml
%config(noreplace) /srv/www/obs/api/config/spring.rb
%config(noreplace) /srv/www/obs/api/config/crawler-user-agents.json
/srv/www/obs/api/config/initializers
%dir /srv/www/obs/api/config/environments
%dir /srv/www/obs/api/files
%dir /srv/www/obs/api/db
/srv/www/obs/api/db/checker.rb
/srv/www/obs/api/Gemfile
%verify(not mtime) /srv/www/obs/api/last_deploy
/srv/www/obs/api/Gemfile.lock
/srv/www/obs/api/config.ru
/srv/www/obs/api/config/application.rb
/srv/www/obs/api/config/clock.rb
%config(noreplace) /etc/logrotate.d/obs-api
%{_unitdir}/obsapisetup.service
%{_unitdir}/obs-api-support.target
%{_unitdir}/obs-clockwork.service
%{_unitdir}/obs-delayedjob-queue-consistency_check.service
%{_unitdir}/obs-delayedjob-queue-default.service
%{_unitdir}/obs-delayedjob-queue-issuetracking.service
%{_unitdir}/obs-delayedjob-queue-mailers.service
%{_unitdir}/obs-delayedjob-queue-project_log_rotate.service
%{_unitdir}/obs-delayedjob-queue-quick@.service
%{_unitdir}/obs-delayedjob-queue-releasetracking.service
%{_unitdir}/obs-delayedjob-queue-staging.service
%{_unitdir}/obs-delayedjob-queue-sphinx-indexing.service
%{_unitdir}/obs-sphinx.service
%{_sbindir}/rcobs-api-support
%{_sbindir}/rcobs-clockwork
%{_sbindir}/rcobs-delayedjob-queue-consistency_check
%{_sbindir}/rcobs-delayedjob-queue-default
%{_sbindir}/rcobs-delayedjob-queue-issuetracking
%{_sbindir}/rcobs-delayedjob-queue-mailers
%{_sbindir}/rcobs-delayedjob-queue-project_log_rotate
%{_sbindir}/rcobs-delayedjob-queue-releasetracking
%{_sbindir}/rcobs-delayedjob-queue-staging
%{_sbindir}/rcobs-delayedjob-queue-sphinx-indexing
%{_sbindir}/rcobs-sphinx
%{_sbindir}/rcobsapisetup
/srv/www/obs/api/app
%attr(-,%{apache_user},%{apache_group})  /srv/www/obs/api/db/structure.sql
%attr(-,%{apache_user},%{apache_group})  /srv/www/obs/api/db/data_schema.rb
/srv/www/obs/api/db/attribute_descriptions.rb
/srv/www/obs/api/db/data
/srv/www/obs/api/db/migrate
/srv/www/obs/api/db/seeds.rb
/srv/www/obs/api/files/wizardtemplate.spec
/srv/www/obs/api/lib
/srv/www/obs/api/public
/srv/www/obs/api/Rakefile
/srv/www/obs/api/script
/srv/www/obs/api/bin
/srv/www/obs/api/test
/srv/www/obs/api/vendor/assets
/srv/www/obs/docs

/srv/www/obs/api/config/locales
%dir /srv/www/obs/api/vendor
/srv/www/obs/api/vendor/diststats

#
# some files below config actually are _not_ config files
# so here we go, file by file
#

/srv/www/obs/api/config/boot.rb
/srv/www/obs/api/config/routes.rb
/srv/www/obs/api/config/routes
/srv/www/obs/api/config/environments/development.rb
%attr(0640,root,%apache_group) %config(noreplace) %verify(md5) /srv/www/obs/api/config/database.yml
%attr(0640,root,%apache_group) /srv/www/obs/api/config/database.yml.example
%attr(0644,root,root) %config(noreplace) %verify(md5) /srv/www/obs/api/config/options.yml
%attr(0644,root,root) /srv/www/obs/api/config/options.yml.example
%dir %attr(0755,%apache_user,%apache_group) /srv/www/obs/api/db/sphinx
%dir %attr(0755,%apache_user,%apache_group) /srv/www/obs/api/db/sphinx/production
/srv/www/obs/api/.bundle

%config /srv/www/obs/api/config/environment.rb
%config /srv/www/obs/api/config/environments/production.rb
%config /srv/www/obs/api/config/environments/test.rb
%config /srv/www/obs/api/config/environments/stage.rb

%dir %attr(-,%{apache_user},%{apache_group}) /srv/www/obs/api/log
%attr(-,%{apache_user},%{apache_group}) /srv/www/obs/api/tmp

# these dirs primarily belong to apache2:
%dir /etc/apache2
%dir /etc/apache2/vhosts.d
%config(noreplace) /etc/apache2/vhosts.d/obs.conf

%defattr(0644,wwwrun,www)
%ghost /srv/www/obs/api/log/access.log
%ghost /srv/www/obs/api/log/backend_access.log
%ghost /srv/www/obs/api/log/delayed_job.log
%ghost /srv/www/obs/api/log/error.log
%ghost /srv/www/obs/api/log/lastevents.access.log
%ghost /srv/www/obs/api/log/production.log
%ghost %attr(0640,root,www) %secret_key_file

%files -n obs-common
%defattr(-,root,root)
%{_fillupdir}/sysconfig.obs-server
/usr/lib/obs/server/setup-appliance.sh
%{_unitdir}/obsstoragesetup.service
/usr/sbin/obsstoragesetup
/usr/sbin/rcobsstoragesetup

%files -n obs-utils
%defattr(-,root,root)
/usr/sbin/obs_project_update

%files -n obs-tests-appliance
%defattr(-,root,root)
%dir /usr/lib/obs/tests/
%dir /usr/lib/obs/tests/appliance
/usr/lib/obs/tests/appliance/*

%files -n obs-cloud-uploader
%defattr(-,root,root)
%{_unitdir}/obsclouduploadworker.service
%{_unitdir}/obsclouduploadserver.service
/usr/sbin/rcobsclouduploadworker
/usr/sbin/rcobsclouduploadserver
/usr/lib/obs/server/bs_clouduploadserver
/usr/lib/obs/server/bs_clouduploadworker
%{_bindir}/clouduploader
%dir /etc/obs
%dir /etc/obs/cloudupload
%dir /etc/obs/cloudupload/.aws
%config(noreplace) /etc/obs/cloudupload/.aws/credentials
%config /etc/obs/cloudupload/.ec2utils.conf

%changelog
