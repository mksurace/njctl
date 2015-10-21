# NJCTL SMART2PDF
# anthony@njctl.org

import zipfile
import os.path
import os
import sys
import shutil
import xml.etree.ElementTree as ET
# import cairosvg
import subprocess
from PyPDF2 import PdfFileMerger, PdfFileReader
from lxml import etree
import SMARTLib
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj

nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"

### Preprocess the SVGs as they are not the best..
# superscript
#subprocess.call("""sed -i 's/baseline-shift="[0-9]*.[0-9]*"/dy="-7.2" dx="2"/g' *.svg""", shell=True)
# subscript
#subprocess.call("""sed -i 's/baseline-shift="-[0-9]*.[0-9]*"/dy="5.0"/g' *.svg""", shell=True)
# trailing whitespace
# subprocess.call("""sed -i 's/ <\/tspan><tspan/<\/tspan><tspan dx="10"/g' *.svg""", shell=True)
# subprocess.call("""sed -ri 's/leading=/dx=/g' *.svg""", shell=True)

def HideShortAnswerNumerics(t):
    for g in t.findall(".//g"):
        if "class" in g.attrib and g.attrib["class"] == "shortanswernumeric":
            g.attrib["visibility"] = "hidden"

def PreserveWhitespace(t):
    t.getroot().attrib["{http://www.w3.org/XML/1998/namespace}space"] = "preserve"

def AddPageNumber(t, n):
    pageN = etree.SubElement(t.getroot(), "text")
    pageN.text = "Page #%d" % n
    pageN.attrib["fill"] = "#000000"
    pageN.attrib["x"] = "730"
    pageN.attrib["y"] = "590"
    pageN.attrib["font-family"] = "Arial"
    pageN.attrib["font-size"] = "12.000"        
    
def ProcessNotebook(filename):
    workingFolder = filename.replace(".notebook", "")
    with zipfile.ZipFile(filename) as zf:
        zf.extractall(workingFolder)

    os.chdir(workingFolder)

    nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
    e = ET.parse("imsmanifest.xml").getroot()
    count = 1

    slideFiles = []

    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        p = c.attrib['href']

        t = etree.parse(p)
        parentMap = {c:p for p in t.iter() for c in p}
        PreserveWhitespace(t)
        HideShortAnswerNumerics(t)

        t.write(p)
        
        pullTabIds = SMARTLib.FindPullTabs(t, parentMap, p)

        AddPageNumber(t, count)
        t.write("%d-%s" % (count, p))
        subprocess.call("C:\\bin\\rsvg-convert -f pdf -o %d.pdf %d-%s" % (count, count, p), shell=True)

        slideFiles.append("%d.pdf" % count)
        count = count + 1
        
        if len(pullTabIds) > 0:
            t = etree.parse(p)
            
            # Create a second slide with the answer tab pulled out
            for g in t.findall(".//g"):
                if "{http://www.w3.org/XML/1998/namespace}id" in g.attrib:
                    id = g.attrib["{http://www.w3.org/XML/1998/namespace}id"]
                    if id in pullTabIds:
                        g.attrib["transform"] = "translate(-600, 0)"

            AddPageNumber(t, count)
            t.write("%d-%s" % (count, p))
            
            subprocess.call("C:\\bin\\rsvg-convert -f pdf -o %d.pdf %d-%s" % (count, count, p), shell=True)
            slideFiles.append("%d.pdf" % count)
            count = count + 1

    merger = PdfFileMerger()
    for f in slideFiles:
        merger.append(PdfFileReader(open(f, 'rb')))

    merger.write("..\converted\\%s.pdf" % workingFolder)
    os.chdir("..")
    shutil.rmtree(workingFolder, True)

if __name__ == "__main__":
    os.chdir(sys.argv[1])
    try:
        os.mkdir("converted")
    except:
        pass
    for file in os.listdir("."):
        if file.find(".notebook") != -1:
            ProcessNotebook(file)
