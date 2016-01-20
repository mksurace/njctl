import argparse
from pyPdf import PdfFileWriter, PdfFileReader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Splice a PDF')
    parser.add_argument('pdfPath', help='path to PDF')
    parser.add_argument('topic', help='topic name')
    parser.add_argument('start', help='start of range, inclusive, indexed by 1', type=int)
    parser.add_argument('end', help='end of range, inclusive', type=int)

    args = parser.parse_args()

    input1 = PdfFileReader(file(args.pdfPath, "rb"))
    output = PdfFileWriter()

    numPages = input1.getNumPages()

    for i in range(args.start-1, args.end):
        page = input1.getPage(i)
        output.addPage(page)

    outputStream = file(args.pdfPath.replace(".pdf", ".%s.pdf" % args.topic), "wb")
    output.write(outputStream)
    outputStream.close()

