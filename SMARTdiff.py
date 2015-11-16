# NJCTL SMARTdiff
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
import difflib
from sets import Set
from lxml import etree

def Diff(f1, f2):
    UnpackNotebook(f1)
    UnpackNotebook(f2)

    slideMapOrig = GetSlideMap(f1)
    slideMapNew = GetSlideMap(f2)

    aIter = 0
    bIter = 0

    while True:
        if bIter == len(slideMapNew):
            break

        if slideMapOrig[aIter] == slideMapNew[bIter]:
            Compare(f1, slideMapOrig[aIter], aIter+1, f2, slideMapNew[bIter], bIter+1)
            if (aIter < len(slideMapOrig) - 1):
                aIter = aIter + 1
            if (bIter < len(slideMapNew)):
                bIter = bIter + 1
        else:
            Found = -1
            for i in range(len(slideMapOrig)):
                if slideMapOrig[i] == slideMapNew[bIter]:
                    Found = i
                    break

            if Found == -1:
                print "'%s': Slide #%d is new" % (f2, bIter+1)
            else:
                print "'%s': Slide #%d was moved from Slide #%d" % (f2, bIter+1, Found)
                
            bIter = bIter + 1

    Cleanup(f1)
    Cleanup(f2)

def Compare(f1, s1, n1, f2, s2, n2):

    svg1 = "%s\\%s" % (f1.replace(".notebook", ""), s1)
    svg2 = "%s\\%s" % (f2.replace(".notebook", ""), s2)
    
    SMARTLib.FixDuplicateXML(svg1)
    fixedDupes = SMARTLib.FixDuplicateIDs(svg1, n1)

    if not fixedDupes:
        print "%s:%d(%s) unable to process" % (f1, n1, s1)
        return

    SMARTLib.FixDuplicateXML(svg2)
    fixedDupes = SMARTLib.FixDuplicateIDs(svg2, n2)

    if not fixedDupes:
        print "%s:%d(%s) unable to process" % (f2, n2, s2)
        return

    t1 = etree.parse(svg1)
    t2 = etree.parse(svg2)

    r1 = t1.getroot()
    r2 = t2.getroot()

    if not xml_compare(r1, r2, None):
        print "Please compare Slide #%d in '%s' against Slide #%d in '%s'" % (n1, f1, n2, f2)
    
    """
    #l1 = etree.tostring(t1, pretty_print = True)
    #l2 = etree.tostring(t2, pretty_print = True)
    
    #for line in difflib.unified_diff(l1.split("\n"), l2.split("\n")):
    #    if line.startswith("+") or line.startswith("-"):
    #        print line
    """

class Printer:
    def __init__(self, string):
        print string
    
def GetSlideMap(file):
    workingFolder = file.replace(".notebook", "")
    nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"

    e = ET.parse("%s/imsmanifest.xml" % workingFolder).getroot()

    slideMap = []

    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        p = c.attrib['href']
        slideMap.append(p)

    return slideMap

def Cleanup(file):
    workingFolder = file.replace(".notebook", "")
    shutil.rmtree(workingFolder, True)
    
def UnpackNotebook(file):
    workingFolder = file.replace(".notebook", "")
    with zipfile.ZipFile(file) as zf:
        zf.extractall(workingFolder)

def xml_compare(x1, x2, reporter=None):
    if x1.tag != x2.tag:
        if reporter:
            reporter('Tags do not match: %s and %s' % (x1.tag, x2.tag))
        return False
##    for name, value in x1.attrib.items():
##        if name not in ["x"]:
##            pass
##        if x2.attrib.get(name) != value:
##            if reporter:
##                reporter('Attributes do not match: %s=%r, %s=%r'
##                         % (name, value, name, x2.attrib.get(name)))
##            return False
    for name in x2.attrib.keys():
        if name in ["smart-txt-ver", "autokern", "forceheight"]:
            continue
        if name not in x1.attrib:
            if reporter:
                reporter('x2 has an attribute x1 is missing: %s'
                         % name)
            return False
    if not text_compare(x1.text, x2.text):
        if reporter:
            reporter('text: %r != %r' % (x1.text, x2.text))
        return False
    if not text_compare(x1.tail, x2.tail):
        if reporter:
            reporter('tail: %r != %r' % (x1.tail, x2.tail))
        return False
    cl1 = x1.getchildren()
    cl2 = x2.getchildren()
    if len(cl1) != len(cl2):
        if reporter:
            reporter('children length differs, %i != %i'
                     % (len(cl1), len(cl2)))
        return False
    i = 0
    for c1, c2 in zip(cl1, cl2):
        i += 1
        if not xml_compare(c1, c2, reporter=reporter):
            if reporter:
                reporter('children %i do not match: %s'
                         % (i, c1.tag))
            return False
    return True

def text_compare(t1, t2):
    if not t1 and not t2:
        return True
    if t1 == '*' or t2 == '*':
        return True
    return (t1 or '').strip() == (t2 or '').strip()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "USAGE: SMARTdiff.py [Orig Notebook] [New Notebook]"
        exit()
        
    f1 = sys.argv[1]
    f2 = sys.argv[2]

    if not os.path.exists(f1):
        print "%s doesn't exist." % f1
        exit()

    if not os.path.exists(f2):
        print "%s doesn't exist." % f2
        exit()

    Diff(f1, f2)
