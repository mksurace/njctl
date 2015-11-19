# NJCTL SMARTpdfCrop
# anthony@njctl.org

import sys
from pyPdf import PdfFileWriter, PdfFileReader

if __name__ == "__main__":
    input1 = PdfFileReader(file(sys.argv[1], "rb"))
    output = PdfFileWriter()

    numPages = input1.getNumPages()

    for i in range(numPages):
        page = input1.getPage(i)
        page.trimBox.lowerLeft = (88, 25)
        page.trimBox.upperRight = (753, 548)
        page.cropBox.lowerLeft = (88, 25)
        page.cropBox.upperRight = (753, 548)
        output.addPage(page)

    outputStream = file(sys.argv[1].replace(".pdf", ".cropped.pdf"), "wb")
    output.write(outputStream)
    outputStream.close()
