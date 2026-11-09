Name:		iq80-snappy
Version:	0.5
Release:	1
Summary:	Java port of Snappy frame compression
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/dain/snappy
Source0:	https://github.com/dain/snappy/archive/refs/tags/snappy-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
# artifactId is snappy. The C library owns that name; the jar file must not.
BuildOption(install):	--file-name %{name}

%description
Pure Java implementation of the Snappy compression format. 0.5 replaces
the compressor and framed streams with the Aircompressor implementation.
The Hadoop codec is omitted: it imports hadoop-common, which is not
packaged. Further pure-Java Snappy work lives in Aircompressor; this
coordinate stops at 0.5.

%prep
%autosetup -n snappy-snappy-%{version}
rm -rf .github
rm -f src/main/java/org/iq80/snappy/HadoopSnappyCodec.java \
	src/main/java/org/iq80/snappy/HadoopSnappyInputStream.java \
	src/main/java/org/iq80/snappy/HadoopSnappyOutputStream.java \
	src/test/java/org/iq80/snappy/HadoopSnappyStreamTest.java \
	src/test/java/org/iq80/snappy/TestHadoopSnappyCodec.java
if find . \( -name '*.jar' -o -name '*.class' \) | grep -q . ; then
	echo "prebuilt Java binary in the sources"
	find . \( -name '*.jar' -o -name '*.class' \)
	exit 1
fi
# hadoop-common is provided. Maven still resolves it, and the codec is
# the only user. The source and enforcer plugins would attach or enforce
# extra artifacts this package does not install.
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def local(tag):
    return tag.split("}", 1)[-1]

def child_text(elem, name):
    for node in elem:
        if local(node.tag) == name:
            return (node.text or "").strip()
    return ""

tree = ET.parse("pom.xml")
root = tree.getroot()
for deps in list(root):
    if local(deps.tag) != "dependencies":
        continue
    for dep in list(deps):
        art = child_text(dep, "artifactId")
        scope = child_text(dep, "scope")
        if art == "hadoop-common" or scope == "test":
            deps.remove(dep)
for build in list(root):
    if local(build.tag) != "build":
        continue
    for plugins in list(build):
        if local(plugins.tag) == "plugins":
            build.remove(plugins)
bound = False
for build in root:
    if local(build.tag) != "build":
        continue
    for plugins in build:
        if local(plugins.tag) == "plugins":
            bound = True
if bound:
    raise SystemExit("a plugin is still bound")
tree.write("pom.xml", encoding="utf-8", xml_declaration=True)
text = open("pom.xml", encoding="utf-8").read()
if "hadoop-common" in text:
    raise SystemExit("hadoop dependency remains")
if "maven-enforcer-plugin" in text:
    raise SystemExit("enforcer plugin remains")
if "testng" in text or "snappy-java" in text:
    raise SystemExit("test dependency remains")
PY

%files -f .mfiles
%doc license.txt notice.md README.md
