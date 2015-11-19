# NJCTL SMARThideTabs
# anthony@njctl.org

import zipfile
import os.path
import os
import sys
import shutil
import xml.etree.ElementTree as ET
import subprocess
from lxml import etree
import SMARTLib

nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"

def RemoveTabs(t, parentMap):
    for tspan in t.findall(".//tspan"):
        if tspan.text and (tspan.text == "Teacher Notes" or tspan.text == "Teacher" or tspan.text == "Answer"):
            parent = parentMap[tspan] # tspan
            parent = parentMap[parent] # tspan
            parent = parentMap[parent] # text
            parent = parentMap[parent] # g
            if parentMap[parent].tag == "g" and "{http://www.w3.org/XML/1998/namespace}id" in parentMap[parent].attrib:
                parent = parentMap[parent] # g
            if parent.tag == "g":
                try:
                    parentMap[parent].remove(parent)
                    #ids.append(parent.attrib["{http://www.w3.org/XML/1998/namespace}id"])
                except:
                    print "Problem with finding parent of pull tab in '%s'" % f
                    pass

def HideShortAnswerNumerics(t):
    for g in t.findall(".//g"):
        if "class" in g.attrib and g.attrib["class"] == "shortanswernumeric":
            g.attrib["visibility"] = "hidden"

def ProcessNotebook(filename):
    workingFolder = filename.replace(".notebook", "")
    with zipfile.ZipFile(filename) as zf:
        zf.extractall(workingFolder)

    os.chdir(workingFolder)

    nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
    e = ET.parse("imsmanifest.xml").getroot()
    count = 1

    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        p = c.attrib['href']

        SMARTLib.FixDuplicateXML(p)
        fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

        t = etree.parse(p)
        parentMap = {c:p for p in t.iter() for c in p}
        HideShortAnswerNumerics(t)
        RemoveTabs(t, parentMap)
        t.write(p)

    # Repack the "notebook"
    zipf = zipfile.ZipFile('../%s-NoTabs.notebook' % workingFolder, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk("."):
        for file in files:
            p = os.path.join(root, file)
            zipf.write(p)
            
    zipf.close()

    os.chdir("..")

    shutil.rmtree(workingFolder, True)

    return '%s-NoTabs.notebook' % workingFolder

if __name__ == "__main__":
    ProcessNotebook(sys.argv[1])
