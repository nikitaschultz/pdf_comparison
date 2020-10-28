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

data_xml = ElementTree.Element("data")
    
    result_xml = ElementTree.SubElement(data_xml, "result")
    result_xml.text = result

    differences_xml = ElementTree.SubElement(data_xml, "differences")

    def add_additions(parent_element, list, name_string):
        for i in range(0, len(list)):
            addition_xml = ElementTree.SubElement(parent_element, "addition")
            addition_xml.set('name', name_string + str(i + 1))
            addition_xml.text = list[i]

    additions_document1_xml = ElementTree.SubElement(differences_xml, "additions-document1")
    add_additions(additions_document1_xml, missing_sentences1, "doc1")

    additions_document2_xml = ElementTree.SubElement(differences_xml, "additions-document2")
    add_additions(additions_document2_xml, missing_sentences2, "doc2")

    tree = ElementTree.ElementTree(data_xml)
    tree.write("results.xml")

text_extractor("diff1.pdf")