# NJCTL SMARTpullTabs
# anthony@njctl.org

import zipfile
import os.path
import os
import sys
import shutil
import xml.etree.ElementTree as ET
import subprocess
from PyPDF2 import PdfFileMerger, PdfFileReader
from lxml import etree
import SMARTLib

nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"

def HideShortAnswerNumerics(t):
    for g in t.findall(".//g"):
        if "class" in g.attrib and g.attrib["class"] == "shortanswernumeric":
            g.attrib["visibility"] = "hidden"

def ShiftElements(e):
    if e is None:
        return

    if e.tag == "path":
        if "d" in e.attrib:
            dArray = e.attrib["d"].split(" ")

            for i in range(len(dArray)):
                pType = dArray[i][0]
                if pType in ["L", "M"]:
                    dArray[i] = "%s%0.2f" % (pType, float(dArray[i][1:]) - 600)

            e.attrib["d"] = " ".join(dArray)

    if "x" in e.attrib and e.tag != "tspan":
        t = e.attrib["x"]
        x = float(t) - 600
        e.attrib["x"] = "%0.2f" % x
    
    if "xbk_transform" in e.attrib:
        t = e.attrib["xbk_transform"]
        #angle,x,y = 0.0
        if t.startswith("rotate"):
            t = t.split("rotate(")[1][:-1]
            angle,x,y = t.split(",")
            x = float(x)
            x = x - 600
            e.attrib["xbk_transform"] = "rotate(%s,%f,%s)" % (angle, x, y)
    if "transform" in e.attrib:
        t = e.attrib["transform"]
        transformMap = dict()
        for part in t.split(" "):
            k = part.split("(")[0]
            values = part.split("(")[1][:-1].split(",")
            transformMap[k] = values
        for k in transformMap:
            if k == "translate":
                transformMap[k][0] = "%0.2f"% (float(transformMap[k][0])-600)
            elif k == "rotate":
                if e.tag != "text":
                    transformMap[k][1] = "%0.2f"% (float(transformMap[k][1])-600)

        newTransform = ""
        for k in transformMap:
            newTransform += "%s(%s) " % (k, ",".join(transformMap[k]))

        e.attrib["transform"] = newTransform.strip()
    if "RotationPoint" in e.attrib:
        t = e.attrib["RotationPoint"]
        t = t[1:-1]
        x,y = t.split(",")
        x = float(x)
        x = x - 600
        e.attrib["RotationPoint"] = "(%f,%s)" % (x, y)
    for c in e:
        ShiftElements(c)

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

    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        pageNum = int(c.attrib["href"].replace("page", "").replace(".svg", ""))
        if pageNum > maxPage:
            maxPage = pageNum

    count = 1
    newPagesMap = {}
    
    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        p = c.attrib['href']

        SMARTLib.FixDuplicateXML(p)
        fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

        t = etree.parse(p)
        parentMap = {c:p for p in t.iter() for c in p}
        HideShortAnswerNumerics(t)
        t.write(p)

        pullTabIds = SMARTLib.FindPullTabs(t, parentMap, p)

        count = count + 1
        if len(pullTabIds) > 0:
            t = etree.parse(p)
            
            # Create a second slide with the answer tab pulled out
            for g in t.findall(".//g"):
                if "{http://www.w3.org/XML/1998/namespace}id" in g.attrib:
                    id = g.attrib["{http://www.w3.org/XML/1998/namespace}id"]
                    if id in pullTabIds:
                        # Shift all the child elements
                        ShiftElements(g)
                        # g.attrib["transform"] = "translate(-600, 0)"

            maxPage = maxPage + 1
            t.write("page%d.svg" % maxPage)
            newPagesMap[count] = "page%d.svg" % maxPage

    count = -1
    for k in newPagesMap:
        print k+count
        f = etree.Element("file")
        f.attrib["href"] = newPagesMap[k]
        group0_pages.insert(k+count, f)        
        pages.insert(k+count, f)
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

    # Repack the "notebook"
    zipf = zipfile.ZipFile('../%s-PulledTabs.notebook' % workingFolder, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk("."):
        for file in files:
            p = os.path.join(root, file)
            zipf.write(p)
            
    zipf.close()

    os.chdir("..")

    shutil.rmtree(workingFolder, True)

if __name__ == "__main__":
    ProcessNotebook(sys.argv[1])
