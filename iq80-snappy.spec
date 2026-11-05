Name:		iq80-snappy
Version:	0.4
Release:	1
Summary:	Java port of Snappy frame compression
Group:		Development/Java
License:	ASL 2.0
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
Pure Java implementation of the Snappy compression format. The Hadoop
codec is omitted: it imports Hadoop 0.20, which is not packaged, and
nothing else in this jar imports Hadoop.

%prep
%autosetup -n snappy-snappy-%{version}
rm -f src/main/java/org/iq80/snappy/HadoopSnappyCodec.java \
	src/test/java/org/iq80/snappy/TestHadoopSnappyCodec.java
# hadoop-core is optional and provided. Maven still resolves it, and
# sysjar builddep does not emit that scope. The extra jar execution would
# attach a second artifact; --file-name allows only one.
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def local(tag):
    return tag.split("}", 1)[-1]

def artifact_of(elem):
    for node in elem:
        if local(node.tag) == "artifactId":
            return (node.text or "").strip()
    return ""

tree = ET.parse("pom.xml")
root = tree.getroot()
for deps in list(root):
    if local(deps.tag) != "dependencies":
        continue
    for dep in list(deps):
        if artifact_of(dep) == "hadoop-core":
            deps.remove(dep)
for build in list(root):
    if local(build.tag) != "build":
        continue
    for plugins in list(build):
        if local(plugins.tag) != "plugins":
            continue
        for plugin in list(plugins):
            art = artifact_of(plugin)
            if art == "really-executable-jar-maven-plugin":
                plugins.remove(plugin)
                continue
            if art != "maven-jar-plugin":
                continue
            for executions in list(plugin):
                if local(executions.tag) != "executions":
                    continue
                for execution in list(executions):
                    eid = ""
                    for node in execution:
                        if local(node.tag) == "id":
                            eid = (node.text or "").strip()
                    if eid == "binary":
                        executions.remove(execution)
                if len(list(executions)) == 0:
                    plugin.remove(executions)
tree.write("pom.xml", encoding="utf-8", xml_declaration=True)
PY

%files -f .mfiles
%doc license.txt notice.md README.md
