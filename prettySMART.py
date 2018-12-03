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
    ["#000000", "Arial", "18.000"],
    ["#000000", "Arial", "18.000", "bold"],
    ["#000000", "Arial", "24.000"],
    ["#000000", "Arial", "24.000", "bold"],
    ["#00005E", "Arial", "18.000"],
    ["#00005E", "Arial", "24.000"],
    ["#00005E", "Arial", "28.000"], # 1st
    ["#00005E", "Arial", "36.000", "bold"],
    ["#00005E", "Arial", "28.000", "bold"],
    ["#595959", "Arial", "18.000"],
    ["#595959", "Arial", "20.000"],
    ["#595959", "Arial", "24.000"],
    ["#595959", "Arial", "28.000"],
    ["#595959", "Arial", "18.000", "bold"],
    ["#595959", "Arial", "20.000", "bold"],
    ["#595959", "Arial", "24.000", "bold"],
    # SR
    ["#000000", "Arial", "36.000"], # 1st
    ["#000000", "Arial", "28.000"],
    ["#000000", "Arial", "20.000"],
    # Video Links
    ["#000000", "Arial", "12.000"],
    ["#000000", "Arial", "10.000"],
    ["#000000", "Arial", "8.000"],
    # Coding
    ["#00005D", "Courier New", "24.000"],
    ["#595959", "Courier New", "18.000"],
    ["#595959", "Courier New", "20.000"],
    ["#595959", "Courier New", "24.000"],
    ["#595959", "Courier New", "28.000"],
    ["#595959", "Courier New", "18.000", "bold"],
    ["#595959", "Courier New", "20.000", "bold"],
    ["#595959", "Courier New", "24.000", "bold"],
    ["#595959", "Courier New", "28.000"],
    ["#000000", "Courier New", "20.000"],
    ["#000000", "Courier New", "24.000"],
    ["#000000", "Courier New", "28.000"],
    ["#000000", "Courier New", "18.000"],
    ["#000000", "Courier New", "28.000", "bold"],
    ["#000000", "Courier New", "24.000", "bold"],
    ["#000000", "Courier New", "18.000", "bold"],
    ["#00005E", "Courier New", "18.000"],
    ["#00005E", "Courier New", "20.000"],
    ["#00005E", "Courier New", "24.000"],
    ["#00005E", "Courier New", "28.000"],
    ["#00005E", "Courier New", "18.000", "bold"],
    ["#00005E", "Courier New", "20.000", "bold"],
    ["#00005E", "Courier New", "24.000", "bold"],
    ["#00005E", "Courier New", "28.000", "bold"],
    # Math Symbols
    ["#000000", "Cambria Math", "18.000"],
    ["#000000", "Cambria Math", "20.000"],
    ["#000000", "Cambria Math", "24.000"],
    ["#000000", "Cambria Math", "28.000"],
    ["#000000", "Cambria Math", "18.000", "bold"],
    ["#000000", "Cambria Math", "20.000", "bold"],
    ["#000000", "Cambria Math", "24.000", "bold"],
    ["#000000", "Cambria Math", "28.000", "bold"],
    ["#00005E", "Cambria Math", "18.000"],
    ["#00005E", "Cambria Math", "20.000"],
    ["#00005E", "Cambria Math", "24.000"],
    ["#00005E", "Cambria Math", "28.000"],
    ["#00005E", "Cambria Math", "18.000", "bold"],
    ["#00005E", "Cambria Math", "20.000", "bold"],
    ["#00005E", "Cambria Math", "24.000", "bold"],
    ["#00005E", "Cambria Math", "28.000", "bold"],
    ]
Mappings = [
    ["Times New Roman", "Arial", "Courier New", "Cambria Math"],
    ["#00005D", "#00005E"],
    ["#595959", "#00005E"],
    ["#0000FF", "#00005E"],
    ["#0000ff", "#00005E"],
    ["#00008B", "#00005E"],
    ["#00008b", "#00005E"],
    ["#333399", "#00005E"],
    ["#A52A00", "#00005E"] # Physics B
    ]
   
def UpdateText(f):
    SMARTLib.ReplaceStringsInFile(f, Mappings)

def NormalizeFont(f, n, style):
    t = etree.parse(f)
    parentMap = {c:p for p in t.iter() for c in p}
    pullTabIds = SMARTLib.FindPullTabs(t, parentMap, f)

    hasMultipleChoice = False
    for votemetadata in t.findall(".//votemetadata"):
        hasMultipleChoice = True

    for tspan in t.iter():
        if not (tspan.tag == "{http://www.w3.org/2000/svg}tspan" or tspan.tag == "tspan"):
            continue

        if ShouldIgnore(tspan, pullTabIds, parentMap):
            continue
        
        if "font-size" in tspan.attrib:
            size = float(tspan.attrib["font-size"])
        
           ## if abs(size - 24) <= 2:
           ##     tspan.attrib["font-size"] = "24.000"
           ## elif abs(size - 28) <= 2:
           ##     tspan.attrib["font-size"] = "28.000"
           ## elif abs(size - 36) <= 2:
           ##     tspan.attrib["font-size"] = "36.000"
           ## elif abs(size - 48) <= 2:
           ##     tspan.attrib["font-size"] = "48.000"
           ## else:
           ##     tspan.attrib["font-size"] = tspan.attrib["font-size"].split(".")[0] + ".000"

            if n == 3:
                continue

            if "fill" in tspan.attrib:
                tspan.attrib["fill"] = tspan.attrib["fill"].upper()

            if tspan.attrib["fill"] == "#000000" and tspan.attrib["font-size"] in ["28.00", "20.000", "24.000", "18.000"]:
               tspan.attrib["fill"] = "#00005E"
            
            if tspan.attrib["fill"] == "#595959" and tspan.attrib["font-size"] in ["28.00", "20.000", "24.000", "18.000"]:
               tspan.attrib["fill"] = "#00005E"
            
            if tspan.attrib["fill"] == "#00005D" and tspan.attrib["font-size"] in ["28.00", "20.000", "24.000", "18.000"]:
               tspan.attrib["fill"] = "#00005E"
            
            ##if tspan.attrib["fill"] == "#00005E" and tspan.attrib["font-size"] in ["38.000"] and "font-weight" in tspan.attrib:
            ##    tspan.attrib["font-size"] = "48.000"
            ##if tspan.attrib["font-family"] in ["Lucida Sans Unicode", "Comic Sans MS"]:
            ##    tspan.attrib["font-family"] = "Arial"
            ##
            
            if tspan.attrib["font-size"] in ["28.000", "36.000"] and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial":
                tspan.attrib["font-size"] = "36.000" 
                tspan.attrib["fill"] = "#00005E" 
                tspan.attrib["font-weight"] = "bold"
                
            ##if IsQuestion(tspan, parentMap) and tspan.attrib["fill"] == "#000000":
            ##    tspan.attrib["font-size"] = "28.000"

            if tspan.attrib["font-size"] in ["18.000", "20.000", "24.000"] and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial":
                tspan.attrib["font-size"] = "24.000"
                tspan.attrib["fill"] == "#00005E"

            if tspan.attrib["font-size"] in ["28.00", "18.000", "24.00", "28.00"] and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Courier New":
                tspan.attrib["font-size"] = "20.000" 
                tspan.attrib["fill"] == "#00005E"            

            if hasMultipleChoice and tspan.attrib["font-size"] in ["24.000", "26.000"] and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial":
                tspan.attrib["font-size"] = "28.000" 
                tspan.attrib["fill"] == "#000000"            

            
            ##if tspan.attrib["font-size"] in ["20.000", "28.000"] and "fill" in tspan.attrib and tspan.attrib["fill"] == "#000000":
            ##    if "font-weight" in tspan.attrib:
            ##        del tspan.attrib["font-weight"]

            if tspan.attrib["font-size"] in "36.000" and "font-family" in tspan.attrib and tspan.attrib["font-family"] == "Arial":
                tspan.attrib["font-weight"] = "bold"

                           
            ##if tspan.attrib["font-size"] == "28.000" and tspan.attrib["fill"] == "#000000":
            ##   tspan.attrib["font-size"] = "24.000" and tspan.attrib["fill"] == "#00005E"
                
                if "font-weight" in tspan.attrib:
                    del tspan.attrib["font-weight"]

            ##if tspan.attrib["fill"] == "#00005E" and tspan.attrib["font-size"] == "24.000":  
            ##    if "font-weight" in tspan.attrib:
            ##        del tspan.attrib["font-weight"]

            ##if style == "1st":
                #FA 36 #000 unbold
               ## if hasMultipleChoice:
                 ##   if tspan.attrib["fill"] == "#000000" and tspan.attrib["font-size"] == "28.000":
                 ##       tspan.attrib["font-size"] = "36.000"
                #DI 28 blue unbold
               ## else:
                ##    if tspan.attrib["fill"] == "#00005E" and tspan.attrib["font-size"] == "24.000":
                ##        tspan.attrib["font-size"] = "28.000"

           ## elif style == "2nd":
                #DI 28 blue unbold
             ##   if not hasMultipleChoice and tspan.attrib["fill"] == "#00005E" and tspan.attrib["font-size"] == "24.000":
              ##      tspan.attrib["font-size"] = "28.000"

    t.write(f)

def UpdatePathWidth(f):
    t = etree.parse(f)
    for path in t.findall(".//path"):
        if "stroke-width" in path.attrib and path.attrib["stroke-width"] == "3.00":
            path.attrib["stroke-width"] = "6.00"
            
    t.write(f)

def DeleteColorEncodings(f):
    # Delete any of those color coded things at the top
    t = etree.parse(f)
    
    deleted = False
    for i in t.iter():
        if not (i.tag == "{http://www.w3.org/2000/svg}image" or i.tag == "image"):
            continue

        if "height" in i.attrib and i.attrib["height"] == "5.00" and float(i.attrib["y"]) < 20:
            i.getparent().remove(i)
            deleted = True

    if deleted:
        t.write(f)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def IsQuestion(tspan, parentMap):
    parent = tspan
    
    while True:
        if parent in parentMap:
            parent = parentMap[parent]
        else:
            break
        
        if "class" in parent.attrib and parent.attrib["class"] in ["question", "questionchoice"]:
            return True

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
    if tspan.text and "font-family" in tspan.attrib and tspan.attrib["font-family"] in ["Lucida Sans Unicode", "Arial Unicode MS", "Symbol", "Courier New", "Arial"]:
        if len(tspan.text.strip()) == 1:
            return True
        if len(tspan.text.strip()) == 2 and tspan.text.strip() == "**":
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

    for tspan in t.iter():
        if not (tspan.tag == "{http://www.w3.org/2000/svg}tspan" or tspan.tag == "tspan"):
            continue

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

def ProcessNotebook(file, t):
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
            if "file" not in c.tag:
                continue

            p = None

            try:
                p = c.attrib['href']
            except:
                print "%s has a problem" % workingFolder
                break
            
            SMARTLib.FixDuplicateXML(p)
            fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

            UpdateText(p)

            if fixedDupes:
                NormalizeFont(p, count, t)
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
    parser.add_argument('-t', default=None, help='1st or 2nd')

    args = parser.parse_args()

    os.chdir(args.notebookFolder)
    try:
        os.mkdir("converted")
    except:
        pass

    if args.t not in [None, "1st", "2nd"]:
        assert False, "type can only be 1st or 2nd"
    
    for file in os.listdir("."):
        if file.find(".notebook") != -1:
            ProcessNotebook(file, args.t)
