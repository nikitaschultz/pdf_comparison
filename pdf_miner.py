from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re
import time
from docx2pdf import convert
from unidecode import unidecode
import os
from junit_xml import TestSuite, TestCase
from xml.etree import ElementTree

#ap = argparse.ArgumentParser()
#ap.add_argument("-1", "--doc1", required = True, help = "Path to the first document")
#args = vars(ap.parse_args())

#Method for processing a pdf to a string
def process_pdf(path):
    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return str(output_string.getvalue()) 

#Method for processing a docx to a string
def process_docx(path):
    convert(path)
    new_path = path.replace("docx", "pdf")
    print(new_path)
    output_string = process_pdf(new_path)
    os.remove(new_path)
    return output_string

#Open and process document to return a StringIO Object
def process_document(path):
    path_list = path.split('.')
    file_extension = path_list[-1]
    
    if(file_extension == "pdf"):
        return True, process_pdf(path)
    
    if(file_extension == "docx"):
        return True, process_docx(path)
    
    return False, file_extension

#Process string for comparison
def process_string(string):
    #Replace additional lines and end all sentences with a fullstop for splitting
    string = string.replace("\n", "")
    string = string.replace("\r\n", "")
    string = string.replace("\x0c", "")
    string = string.replace("\uf0b7", "")
    string = string.replace("?", ".")
    string = string.replace("!", ".")
    string = string.encode("ascii", errors="ignore").decode()

    #Convert to lowercase
    string = string.lower()

    #Remove additional spaces
    string = " ".join(string.split())      

    return string

def compare_documents(path1, path2):
    #Get output string for each document
    status1, string1 = process_document(path1)
    status2, string2 = process_document(path2)

    if status1 != True:
        print(string1 + " is not a valid file extension.  Please ensure both documents are PDF or Word documents.")
        return ("Error", "Invalid file type")

    if status2 != True:
        print(string2 + " is not a valid file extension.  Please ensure both documents are PDF or Word documents.")
        return ("Error", "Invalid file type")

    #Process the strings to be matched
    string1_processed = process_string(string1)
    string2_processed = process_string(string2)
    
    #Check for a perfect match
    if string1_processed == string2_processed:
        print("The content of the files is a perfect match.")
        return ("Pass", "")

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

    #Find words contained in list 1 that are not contained in list 2
    missing_sentences1 = []
    for string in string1_list_trimmed:
        if string not in string2_list_trimmed:
            missing_sentences1.append(string)

    #Find words contained in list 2 that are not contained in list 1
    missing_sentences2 = []
    for string in string2_list_trimmed:
        if string not in string1_list_trimmed:
            missing_sentences2.append(string)

    #If missing sentence lists are empty, check for order
    out_of_order = []
    if len(missing_sentences1) == 0 and len(missing_sentences2) == 0:
        partial_match = True
        for i in range(len(string1_list_trimmed)):
            if string1_list_trimmed[i] != string2_list_trimmed[i]:
                out_of_order.append(string1_list_trimmed[i])
        print("The content of the files is a partial match.  The content is the comparable, however maybe out of order or repeated in one document.  See results.csv for details.")
        return ("Fail", "Partial match")
    
    print("The content of the files is not a match.  Please see results.csv for details.")
    return ("Fail", "No match")

def write_to_xml(results, start_time):
    total_time = time.time() - start_time

    test_cases = [TestCase("Test for Perfect Match", "", total_time, "", "")]

    if results[0] == "Fail":
        test_cases[0].add_failure_info(results[1])

    if results[0] == "Error":
        test_cases[0].add_error_info(results[1])

    ts = TestSuite("Test suite", test_cases)
    with open('output.xml', 'w') as f:
        TestSuite.to_file(f, [ts])

start_time = time.time()

results = compare_documents("results.csv", "diff2.pdf")

write_to_xml(results, start_time)
