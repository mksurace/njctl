# NJCTL SMART2PDF
# anthony@njctl.org

import os
import sys
import subprocess
import SMARTpullTabs
import SMARThideTabs

def ProcessNotebook(file):
    # First create a no-pull-tab version and a pull-tab version of the notebook.
    for notebookToConvert in [SMARThideTabs.ProcessNotebook(file), SMARTpullTabs.ProcessNotebook(file)]:
        # Open the notebook file
        subprocess.Popen(notebookToConvert, shell=True)
        
        # Launch the sikuli script to turn it into a PDF
        p = subprocess.Popen("C:\\sikuli\\runsikulix.cmd -r C:\\njctl\\sikuli\\11.4.exportAutomation.sikuli", shell=True)
        p.wait()
        
        # 
        print notebookToConvert

if __name__ == "__main__":
    ProcessNotebook(sys.argv[1])
