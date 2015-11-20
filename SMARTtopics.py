# NJCTL SMARTtopics
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
    ["#00005E", "Arial", "28.000"], # 1st
    ["#00005E", "Arial", "36.000", "bold"],
    ["#00005E", "Arial", "48.000", "bold"],
    # SR
    ["#000000", "Arial", "36.000"], # 1st
    ["#000000", "Arial", "28.000"],
    ["#000000", "Arial", "20.000"],
    ]

def GetTopic(f):
    topic = ""
    t = etree.parse(f)
    for tspan in t.findall(".//tspan"):
        if tspan.text and tspan.attrib["fill"] == "#00005E" and tspan.attrib["font-size"] == "36.000" and "font-weight" in tspan.attrib and len(tspan.text.strip()) > 1:
            topic += tspan.text
    return topic

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

    with open("../%s.topics.txt" % workingFolder, 'w') as out:
        topics = []
        for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
            p = c.attrib['href']
            
            SMARTLib.FixDuplicateXML(p)
            fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

            if fixedDupes:
                topic = GetTopic(p)
                if topic and topic not in topics:
                    topics.append(topic)
            else:
                out.write("Slide #%d (%s): Unable to process.. Please manually verify.\n" % (count, p))
                
            count = count + 1

        for topic in topics:
            out.write("%s\n" % topic.encode('utf-8'))

        os.chdir("..")

        shutil.rmtree(workingFolder, True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prettify a SMART notebook.')
    parser.add_argument('notebookFolder', help='path to a folder containing SMART notebooks')

    args = parser.parse_args()

    os.chdir(args.notebookFolder)
    try:
        os.mkdir("topics")
    except:
        pass
    
    for file in os.listdir("."):
        if file.find(".notebook") != -1:
            ProcessNotebook(file)
