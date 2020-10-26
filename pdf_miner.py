from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re
import csv
from datetime import datetime

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
    perfect_match = False
    partial_match = False

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

def compare_documents(path1, path2):
    #Get output string for each document
    string1 = process_document(path1)
    string2 = process_document(path2)

    #Process the strings to be matched
    string1_processed = process_string(string1)
    string2_processed = process_string(string2)

    #Check for a perfect match
    if string1_processed == string2_processed:
        perfect_match = True
        return [[datetime.now(), "Perfect match", path1, path2, "N/A", "N/A", "N/A"]]

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

    #Find words contained in list 2 that are not conta
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
        return [[datetime.now(), "Partial match", path1, path2, "N/A", "N/A", out_of_order]]
    
    return [[datetime.now(), "No match", path1, path2, missing_sentences1, missing_sentences2, "N/A"]]

results = compare_documents("comp1.pdf", "diff3.pdf")

with open('results.csv', 'a') as file:
    writer = csv.writer(file)
    writer.writerows(results)
