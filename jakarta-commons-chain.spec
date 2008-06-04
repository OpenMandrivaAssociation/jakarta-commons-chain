# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support 0
# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'
%define _without_maven 1
%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define section   free
%define base_name commons-chain

Name:           jakarta-commons-chain
Version:        1.2
Release:        %mkrel 0.0.1
Epoch:          0
Summary:        Commons Chain
License:        Apache Software License 2.0
Url:            http://jakarta.apache.org/commons/chain/
Group:          Development/Java
Source0:        %{base_name}-%{version}-src.zip

Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl

BuildRequires:  jpackage-utils >= 0:1.7.2
BuildRequires:  java-rpmbuild
BuildRequires:  ant >= 0:1.6
BuildRequires:  junit
%if %{with_maven}
BuildRequires:  maven >= 0:1.1
BuildRequires:  saxon
BuildRequires:  saxon-scripts
BuildRequires:  maven-plugin-changelog
BuildRequires:  maven-plugin-changes
BuildRequires:  maven-plugin-xdoc
%endif
BuildRequires:  jakarta-commons-beanutils
BuildRequires:  jakarta-commons-collections
BuildRequires:  jakarta-commons-digester
BuildRequires:  jakarta-commons-logging
BuildRequires:  myfaces
BuildRequires:  portlet-1.0-api
BuildRequires:  servletapi5
BuildRequires:  struts
Requires:       jakarta-commons-beanutils
Requires:       jakarta-commons-collections
Requires:       jakarta-commons-digester
Requires:       jakarta-commons-logging
Requires:       myfaces
Requires:       portlet-1.0-api
Requires:       servlet
Requires:       struts
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot

%description
A popular technique for organizing the execution of complex 
processing flows is the "Chain of Responsibility" pattern, as 
described (among many other places) in the classic "Gang of Four" 
design patterns book. Although the fundamental API contracts 
required to implement this design patten are extremely simple, 
it is useful to have a base API that facilitates using the pattern, 
and (more importantly) encouraging composition of command 
implementations from multiple diverse sources.

Towards that end, the Chain API models a computation as a series 
of "commands" that can be combined into a "chain". The API for a 
command consists of a single method (execute()), which is passed 
a "context" parameter containing the dynamic state of the 
computation, and whose return value is a boolean that determines 
whether or not processing for the current chain has been completed 
(true), or whether processing should be delegated to the next 
command in the chain (false).

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%if %{with_maven}
%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.
%endif

%prep
%setup -q -n %{base_name}-%{version}-src
%remove_java_binaries

%if %{with_maven}
if [ ! -f %{SOURCE4} ]; then
export DEPCAT=$(pwd)/%{base_name}-%{version}-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > %{base_name}-%{version}-depmap.new.xml
fi
%endif

%build
%if %{with_maven}
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done

maven \
    -Dmaven.javadoc.source=1.4 \
    -Dmaven.repo.remote=file:/usr/share/maven/repository \
    -Dmaven.home.local=$(pwd)/.maven \
    jar javadoc xdoc:transform
%else
mkdir -p target/lib
pushd target/lib
ln -sf $(build-classpath commons-beanutils)
ln -sf $(build-classpath commons-collections)
ln -sf $(build-classpath commons-digester)
ln -sf $(build-classpath commons-logging)
ln -sf $(build-classpath junit)
ln -sf $(build-classpath myfaces/myfaces-jsf-api)
ln -sf $(build-classpath portlet-1.0-api)
ln -sf $(build-classpath servletapi5)
ln -sf $(build-classpath struts)
popd
%ant -Dnoget compile jar javadoc
%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 target/%{base_name}-%{version}.jar \
           $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar

%add_to_maven_depmap %{base_name} %{base_name} %{version} JPP %{name}

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in jakarta-*; do \
ln -sf ${jar} ${jar/jakarta-/}; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do \
ln -sf ${jar} ${jar/-%{version}/}; done)

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -m 644 pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf target/docs/apidocs
%else
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

## manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -p LICENSE.txt $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
%endif

%{gcj_compile}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap 
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}/LICENSE.txt
%{_javadir}/*
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%{gcj_files}

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%if %{with_maven}
%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
%endif
