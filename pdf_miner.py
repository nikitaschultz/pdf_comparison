from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re

#ap = argparse.ArgumentParser()
#ap.add_argument("-1", "--doc1", required = True, help = "Path to the first document")
#args = vars(ap.parse_args())

#Open and process document to return a StringIO Object
def process_document(path):
    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string 

#Process string for comparison
def process_string(string_io):
    #Convert to a Python string
    string = str(string_io.getvalue())

    #Replace additional lines and end all sentences with a fullstop for splitting
    string.replace("\n", "")
    string.replace("\r\n", "")
    string.replace("\x0c", "")
    string.replace("?", ".")
    string.replace("!", ".")

    #Convert to lowercase
    string = string.lower()

    #Remove additional spaces
    string = " ".join(string.split())      

    return string

def compare_strings(string1, string2):
    #Process the strings to be matched
    string1_processed = process_string(string1)
    string2_processed = process_string(string2)

    #Check for a perfect match
    perfect_match = False
    if string1_processed == string2_processed:
        perfect_match = True
        print("Perfect Match!")
        return True

    #Split the strings into a list of sentences
    string1_list = string1_processed.split(".")    
    string2_list = string2_processed.split(".")

    #Trim each sentence in each list of leading and trailing whitespace
    string1_list_trimmed = []
    string2_list_trimmed = []

    for string in string1_list:
        string1_list_trimmed.append(string.strip())
    
    for string in string2_list:
        string2_list_trimmed.append(string.strip())
    
    missing_sentences1 = []

    print("MISSING FROM DOC 1:")
    for string in string1_list_trimmed:
        if string not in string2_list_trimmed:
            print(string)
            missing_sentences1.append(string)

    missing_sentences2 = []

    print("MISSING FROM DOC 1:")
    for string in string2_list_trimmed:
        if string not in string1_list_trimmed:
            print(string)
            missing_sentences2.append(string)

    #If missing sentence lists are empty, check for order
    if len(missing_sentences1) == 0 and len(missing_sentences2) == 0:
        for string in string1_list_trimmed:
                

output_string1 = process_document("comp1.pdf")
output_string2 = process_document("comp3.pdf")
compare_strings(output_string1, output_string2)
