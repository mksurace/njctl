# NJCTL SMARTpdfAddPageNumbers
# anthony@njctl.org

from pyPdf import PdfFileWriter, PdfFileReader
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys

if __name__ == "__main__":
    existing_pdf = PdfFileReader(file(sys.argv[1], "rb"))
    output = PdfFileWriter()
    numPages = existing_pdf.getNumPages()
    for i in range(numPages):
        packet = StringIO.StringIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawRightString(750, 30, "%d / %d" % (i+1, numPages))
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        
        page = existing_pdf.getPage(i)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        
    outputStream = file(sys.argv[1].replace(".pdf", ".numbered.pdf"), "wb")
    output.write(outputStream)
    outputStream.close()
