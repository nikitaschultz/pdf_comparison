from PyPDF2 import PdfFileReader

def text_extractor(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f, strict = False)

        number_of_pages = pdf.getNumPages()

        for i in range(1, number_of_pages):
            page = pdf.getPage(i)
            text = page.extractText()

            print("PAGE " + str(i))
            print(text)

text_extractor("diff1.pdf")