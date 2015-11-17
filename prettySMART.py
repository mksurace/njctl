# NJCTL prettySMART
# anthony@njctl.org

import zipfile
import os
import sys
import shutil
import re
import xml.etree.ElementTree as ET
import random
import string
import SMARTLib
import argparse
from sets import Set
from lxml import etree

# Color, Font-Family, Font-Size, Font-Weight (optional)
AllowedTSpans = [
    # Title Slide
    ["#00005E", "Arial", "24.000", "bold"],
    ["#00005E", "Arial", "20.000", "bold"],
    # Text
    ["#000000", "Arial", "24.000"],
    ["#000000", "Arial", "24.000", "bold"],
    ["#00005E", "Arial", "24.000"],
    ["#00005E", "Arial", "36.000", "bold"],
    ["#00005E", "Arial", "48.000", "bold"],
    # SR
    ["#000000", "Arial", "28.000"],
    ["#000000", "Arial", "20.000"],
    ]
Mappings = [
    ["Times New Roman", "Arial"],
    ["#0000FF", "#00005E"],
    ["#0000ff", "#00005E"],
    ["#00008B", "#00005E"],
    ["#00008b", "#00005E"],
    ["#333399", "#00005E"]
    ]

   
def UpdateText(f):
    SMARTLib.ReplaceStringsInFile(f, Mappings)

def NormalizeFont(f, n):
    t = etree.parse(f)
    parentMap = {c:p for p in t.iter() for c in p}
    pullTabIds = SMARTLib.FindPullTabs(t, parentMap, f)

    hasMultipleChoice = False
    for votemetadata in t.findall(".//votemetadata"):
        hasMultipleChoice = True

    for tspan in t.findall(".//tspan"):
        if ShouldIgnore(tspan, pullTabIds, parentMap):
            continue
        
        if "font-size" in tspan.attrib:
            size = float(tspan.attrib["font-size"])
        
            if abs(size - 24) <= 2:
                tspan.attrib["font-size"] = "24.000"
            elif abs(size - 28) <= 2:
                tspan.attrib["font-size"] = "28.000"
            elif abs(size - 36) <= 2:
                tspan.attrib["font-size"] = "36.000"
            elif abs(size - 48) <= 2:
                tspan.attrib["font-size"] = "48.000"
            else:
                tspan.attrib["font-size"] = tspan.attrib["font-size"].split(".")[0] + ".000"


            if "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Times New Roman":
                tspan.attrib["font-family"] = "Arial"
                
            if tspan.attrib["font-size"] in ["26.000", "36.000"] and "fill" in tspan.attrib and tspan.attrib["fill"] == "#000000" and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial":
                tspan.attrib["font-size"] = "28.000"

            if hasMultipleChoice and tspan.attrib["font-size"] in ["24.000", "26.000", "36.000"] and "fill" in tspan.attrib and tspan.attrib["fill"] == "#000000" and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial":
                tspan.attrib["font-size"] = "28.000"            

            if tspan.attrib["font-size"] in ["20.000", "28.000"] and "fill" in tspan.attrib and tspan.attrib["fill"] == "#000000":
                if "font-weight" in tspan.attrib:
                    del tspan.attrib["font-weight"]

            if tspan.attrib["font-size"] == "48.000":
                tspan.attrib["font-weight"] = "bold"

            if tspan.attrib["font-size"] == "28.000" and tspan.attrib["fill"] == "#00005E":
                tspan.attrib["font-size"] = "24.000"
                
                if "font-weight" in tspan.attrib:
                    if tspan.text and tspan.text.strip().count(" ") > 0:
                        unboldedNeighbors = False
                        for sibling in tspan.getparent():
                            if sibling.tag == "tspan" and "font-weight" not in sibling.attrib:
                                unboldedNeighbors = True

                        if not unboldedNeighbors:
                            del tspan.attrib["font-weight"]  
                

            if tspan.attrib["fill"] == "#00005E" and tspan.attrib["font-size"] == "24.000":  
                if "font-weight" in tspan.attrib:
                    if tspan.text and tspan.text.strip().count(" ") > 0:
                        unboldedNeighbors = False
                        for sibling in tspan.getparent():
                            if sibling.tag == "tspan" and "font-weight" not in sibling.attrib:
                                unboldedNeighbors = True

                        if not unboldedNeighbors:
                            del tspan.attrib["font-weight"]  


    t.write(f)

def UpdatePathWidth(f):
    t = etree.parse(f)
    for path in t.findall(".//path"):
        if "stroke-width" in path.attrib and path.attrib["stroke-width"] == "3.00":
            path.attrib["stroke-width"] = "6.00"
            
    t.write(f)

def DeleteColorEncodings(f):
    t = etree.parse(f)
    # Delete any of those color coded things at the top
    for i in t.findall(".//image"):
        if "height" in i.attrib and i.attrib["height"] == "5.00" and float(i.attrib["y"]) < 20:
            i.getparent().remove(i)
    t.write(f)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def ShouldIgnore(tspan, pullTabIds, parentMap):
    if not tspan.text:
        return True
    if tspan.text and (tspan.text.strip() == "" or len(tspan.text.strip()) == 0):
        return True
    if tspan.text and RepresentsInt(tspan.text) and "font-size" in tspan.attrib and tspan.attrib["font-size"] == "24.000": # Ignore number lines.
        return True
    if tspan.text and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Lucida Sans Unicode":
        if tspan.text == u'\u03b8': # Division symbol
            return True
        elif tspan.text == u'\xc3':
            return True
        else:
            try:
                if ord(tspan.text.strip()) == 247:
                    return True
            except:
                pass
    if tspan.text and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial Unicode MS":
        if len(tspan.text.strip()) == 1:
            return True
    if "supersuboriginalfont" in tspan.attrib:
        return True
    if tspan.text == "Students type their answers here":
        return True
    if tspan.text == "Click on the topic to go to that section":
        return True
    if SMARTLib.IsInShortAnswerNumeric(tspan, parentMap):
        return True
    if SMARTLib.IsInPullTab(tspan, pullTabIds, parentMap):
        return True
    if SMARTLib.IsInTable(tspan, parentMap):
        return True
    
    return False

def ConsistencyCheck(f):
    t = etree.parse(f)
    parentMap = {c:p for p in t.iter() for c in p}
    pullTabIds = SMARTLib.FindPullTabs(t, parentMap, f)

    results = {}
    results["Output"] = Set()
    results["nBadTSpan"] = 0
    results["nTotalTSpan"] = 0
    results["Arcs"] = Set()

    for tspan in t.findall(".//tspan"):
        if ShouldIgnore(tspan, pullTabIds, parentMap):
            continue
        
        results["nTotalTSpan"] = results["nTotalTSpan"] + 1
        if "supersuboriginalfont" not in tspan.attrib and "fill" in tspan.attrib and "font-family" in tspan.attrib and "font-size" in tspan.attrib:
            if "font-weight" in tspan.attrib:
                if [tspan.attrib["fill"], tspan.attrib["font-family"], tspan.attrib["font-size"], tspan.attrib["font-weight"]] not in AllowedTSpans:
                    results["nBadTSpan"] = results["nBadTSpan"] + 1
                    results["Output"].add("UNEXPECTED!: %s %s %s %s, text is '%s'" % (tspan.attrib["fill"], tspan.attrib["font-family"], tspan.attrib["font-size"], tspan.attrib["font-weight"], tspan.text.encode('utf-8') if tspan.text else ""))
            else: 
                if [tspan.attrib["fill"], tspan.attrib["font-family"], tspan.attrib["font-size"]] not in AllowedTSpans:
                    results["nBadTSpan"] = results["nBadTSpan"] + 1
                    results["Output"].add("UNEXPECTED!: %s %s %s, text is '%s'" % (tspan.attrib["fill"], tspan.attrib["font-family"], tspan.attrib["font-size"], tspan.text.encode('utf-8') if tspan.text else ""))

    for path in t.findall(".//path"):
        if "shapeDivisionLabel" in path.attrib and "ellipsRectX" in path.attrib:
            results["Arcs"].add("Detected divided circle")
        if "lineType" in path.attrib and path.attrib["lineType"] == "curve":
            results["Arcs"].add("Detected arc")

    return results

def IsTableOfContentsSlide(f):
    t = etree.parse(f)
    for tspan in t.findall(".//tspan"):
        if tspan.text and tspan.text.strip() == "Table of contents":
            return True
    return False

def ProcessNotebook(file):
    workingFolder = file.replace(".notebook", "")
    with zipfile.ZipFile(file) as zf:
        zf.extractall(workingFolder)

    os.chdir(workingFolder)

    nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
    e = ET.parse("imsmanifest.xml").getroot()
    count = 1

    results = Set()
    arcs = []

    with open("../converted/%s.notes.txt" % workingFolder, 'w') as out:    
        for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
            p = c.attrib['href']
            
            SMARTLib.FixDuplicateXML(p)
            fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

            UpdateText(p)

            if fixedDupes:
                if count != 3:
                    NormalizeFont(p, count)
                UpdatePathWidth(p)
                DeleteColorEncodings(p)
                res = ConsistencyCheck(p)
                if res["nTotalTSpan"] != 0:
                    pct = 100*float(res["nTotalTSpan"] - res["nBadTSpan"]) / res["nTotalTSpan"]
                    if pct != 100:
                        out.write("Slide #%d [%0.2f%%]\n" % (count, pct))
                for r in res["Output"]:
                    s = "Slide #%d (%s): %s" % (count, p, r)
                    out.write("%s\n" % s)
                for r in res["Arcs"]:
                    arcs.append("Slide #%d (%s): %s" % (count, p, r))
            else:
                out.write("Slide #%d (%s): Unable to process.. Please manually verify.\n" % (count, p))
                
            count = count + 1

        if len(arcs) > 0:
            out.write("SUMMARY: PROMETHEAN INCOMPATIBILITY\n")
            for r in arcs:
                out.write("%s\n" % r)
            
        # Repack the "notebook"
        zipf = zipfile.ZipFile('../converted/%s-updated.notebook' % workingFolder, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk("."):
            for file in files:
                p = os.path.join(root, file)
                zipf.write(p)
                
        zipf.close()

        os.chdir("..")

        shutil.rmtree(workingFolder, True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prettify a SMART notebook.')
    parser.add_argument('notebookFolder', help='path to a folder containing SMART notebooks')
    parser.add_argument('-t', default='1st', help='1st or 2nd')

    args = parser.parse_args()

    os.chdir(args.notebookFolder)
    try:
        os.mkdir("converted")
    except:
        pass


    if args.t not in ["1st", "2nd"]:
        assert False, "type can only be 1st or 2nd"

    
    for file in os.listdir("."):
        if file.find(".notebook") != -1:
            ProcessNotebook(file)
