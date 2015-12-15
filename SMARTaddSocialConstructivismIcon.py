# NJCTL SMARTaddSocialConstructivismIcon
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

def ProcessNotebook(filename):
    workingFolder = filename.replace(".notebook", "")
    with zipfile.ZipFile(filename) as zf:
        zf.extractall(workingFolder)

    os.chdir(workingFolder)

    nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
    e = ET.parse("imsmanifest.xml")
    maxPage = 0
    group0_pages = None
    pages = None
    for c in e.find(".//" + nodePrefix + "resources"):
        if "identifier" in c.attrib:
            if c.attrib["identifier"] == "group0_pages":
                group0_pages = c
            elif c.attrib["identifier"] == "pages":
                pages = c

    count = 1
    
    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        p = c.attrib['href']

        SMARTLib.FixDuplicateXML(p)
        fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

        t = etree.parse(p)
        parentMap = {c:p for p in t.iter() for c in p}
        pullTabIds = SMARTLib.FindPullTabs(t, parentMap, p)

        if len(pullTabIds) > 0:
        # Replace the end of the document, which should be </g></svg> with the following.
            SMARTLib.ReplaceStringsInFile(p, [["</g></svg>",
                                              """<image xmlns:xlink="http://www.w3.org/1999/xlink" x="682.00" y="501.00" width="111.00" height="93.00" xlink:href="images/socialconstructivism.png" RotationPoint="(1598.000000,379.000000)" transform="rotate(0.00,737.50,547.50)" xml:id="annotation.MCTLSOCIALCONSTRUCTIVISM0" visible="1" /></g></svg>"""]])

        count = count + 1

            
    e.write("imsmanifest.xml")

    data = open("imsmanifest.xml").read()
    data = data.replace("ns0:", "")
    data = data.replace("ns0", "")
    data = data.replace("xmlns:=", "xmlns=")
    data = data.replace("ns1", "smartnotebook")
    data = data.replace("ns2", "adlcp")
    data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + data
    with open("imsmanifest.xml", 'w') as f:
        f.write(data)        

    # Copy over the Social Constructivism image
    shutil.copyfile("C:\\njctl\\socialconstructivism.png", "images\\socialconstructivism.png")

    # Repack the "notebook"
    zipf = zipfile.ZipFile('../%s-updated.notebook' % workingFolder, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk("."):
        for file in files:
            p = os.path.join(root, file)
            zipf.write(p)
            
    zipf.close()

    os.chdir("..")

    shutil.rmtree(workingFolder, True)
    return '%s-updated.notebook' % workingFolder

if __name__ == "__main__":
    ProcessNotebook(sys.argv[1])
