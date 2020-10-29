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
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-prog", "--prog", required = True, help = "Which program to run? 1. Check for perfect match 2. Check for specific difference")
ap.add_argument("-1", "--path1", required = True, help = "The path to file 1.")
ap.add_argument("-2", "--path2", required = True, help = "The path to file 2.")
ap.add_argument("-except", "--exception", help = "The text to be excepted (only in program 2).")
ap.add_argument("-occ", "--occurrences", help = "The acceptable number of occurrences of the excepted text (only in program 2).")

args = vars(ap.parse_args())

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

#Trim each sentence in a given list of leading and trailing whitespace
def trim_list(list):
    trimmed_list = []
    for string in list:
        trimmed_list.append(string.strip())
    return trimmed_list

#Find sentences contained in one list but not another
def find_additional_content(list1, list2):
    additional_content = []
    for item in list1:
        if item not in list2:
            additional_content.append(item)
    return additional_content

#Find sentences that are not presented in two lists in the same order
def check_content_order(list1, list2):
    for i in range(0, len(list1)):
        if list1[i] != list2[i]:
            out_of_order.append(list1[i])
    return out_of_order

#Separate lists to words and compare the count
def check_additional_words(list1, list2):
    def split_list_to_words(list):
        new_list = []
        for item in list:
            item_list = item.split(" ")
            for word in item_list:
                new_list.append(word)
        return new_list

    list1_words = split_list_to_words(list1)
    list2_words = split_list_to_words(list2)

    extra_words = []

    for word in list1_words:
        if list1_words.count(word) != list2_words.count(word):
            extra_words.append(word)
    
    return extra_words

#Check two lists for the excepted string
def check_for_exception(list1, list2, excepted_string, acceptable_occurences):
    if(len(list1) > 0 and len(list2) > 0):
        return False, "Additions in both documents"

    excepted_string = process_string(excepted_string)
    excepted_string_word_list = excepted_string.split(" ")

    excepted_list = []
    for i in range(0, acceptable_occurences):
        for word in excepted_string_word_list:
            excepted_list.append(word)

    acceptable = True

    def check_list(list):
        if len(list) > 0:
            for i in range(0, len(list)):
                if list[i] != excepted_list[i]:
                    acceptable = False

    check_list(list1)
    check_list(list2)
    
    if acceptable:
        return True, ""
    else:
        return False, "Outside the scope of acceptable occurrences"
    

#PROGRAM 1: SEEKING A PERFECT MATCH
def compare_documents_program_1(path1, path2):
    #Get output string for each document
    status1, string1 = process_document(path1)
    status2, string2 = process_document(path2)

    if status1 != True:
        print(string1 + " is not a valid file extension.  Please ensure both documents are PDF or Word documents.")
        return "Error", "Invalid File Type"

    if status2 != True:
        print(string2 + " is not a valid file extension.  Please ensure both documents are PDF or Word documents.")
        return "Error", "Invalid File Type"

    #Process the strings to be matched
    string1_processed = process_string(string1)
    string2_processed = process_string(string2)
    
    #Check for a perfect match
    if string1_processed == string2_processed:
        print("The content of the files is a perfect match.")
        return "Pass", ""

    #Split the strings into a list of sentences
    string1_list = string1_processed.split(".")    
    string2_list = string2_processed.split(".")

    #Trim each sentence in each list of leading and trailing whitespace
    string1_list_trimmed = trim_list(string1_list)
    string2_list_trimmed = trim_list(string2_list)

    #Find sentences contained in each list that are not contained in the other
    missing_sentences1 = find_additional_content(string1_list_trimmed, string2_list_trimmed)
    missing_sentences2 = find_additional_content(string2_list_trimmed, string1_list_trimmed)

    #If missing sentence lists are empty, check for order
    out_of_order = []
    if len(missing_sentences1) == 0 and len(missing_sentences2) == 0:
        out_of_order = check_content_order(string1_list_trimmed, string2_list_trimmed)
        print("The content of the files is a partial match.  The content is the comparable, however maybe out of order or repeated in one document.")
        return "Fail", "Partial Match"
    
    print("The content of the files is not a match.")
    return "Fail", "No Match"

#PROGRAM 2: SEEKING A PERFECT MATCH WITH AN EXCEPTED DIFFERENCE
def compare_documents_program_2(path1, path2, excepted_string, acceptable_occurences):
    #Get output string for each document
    status1, string1 = process_document(path1)
    status2, string2 = process_document(path2)

    if status1 != True:
        print(string1 + " is not a valid file extension.  Please ensure both documents are PDF or Word documents.")
        return "Error", "Invalid File Type"

    if status2 != True:
        print(string2 + " is not a valid file extension.  Please ensure both documents are PDF or Word documents.")
        return "Error", "Invalid File Type"

    #Process the strings to be matched
    string1_processed = process_string(string1)
    string2_processed = process_string(string2)
    
    #Check for a perfect match
    if string1_processed == string2_processed:
        print("The content of the files is a perfect match.")
        return "Fail", "Perfect Match"

    #Split the strings into a list of sentences
    string1_list = string1_processed.split(".")    
    string2_list = string2_processed.split(".")

    #Trim each sentence in each list of leading and trailing whitespace
    string1_list_trimmed = trim_list(string1_list)
    string2_list_trimmed = trim_list(string2_list)

    #Find sentences contained in each list that are not contained in the other
    missing_sentences1 = find_additional_content(string1_list_trimmed, string2_list_trimmed)
    missing_sentences2 = find_additional_content(string2_list_trimmed, string1_list_trimmed)

    #Convert each additional sentence list to a list of words and check for count
    missing_words1 = check_additional_words(missing_sentences1, missing_sentences2)
    missing_words2 = check_additional_words(missing_sentences2, missing_sentences1)

    #Check the additional words for the acceptable occurrences of the excepted string
    exception_result, exception_comment = check_for_exception(missing_words1, missing_words2, excepted_string, acceptable_occurences)
    
    if exception_result == True:
        return "Pass", exception_comment
        print("The excepted string was present in the acceptable number of occurrences")
    else:
        return "Fail", exception_comment
        print("The excepted string was not found in the acceptable number of occurrences")

    print("The content of the files is not a match and the difference was not the excepted string.")
    return "Fail", "No Match"

#Write the results to output.xml
def write_to_xml(results, start_time):
    total_time = time.time() - start_time

    test_cases = [TestCase("Test for Document Comparison", "", total_time, "", "")]

    if results[0] == "Fail":
        test_cases[0].add_failure_info(results[1])

    if results[0] == "Error":
        test_cases[0].add_error_info(results[1])

    ts = TestSuite("Test suite", test_cases)
    with open('output.xml', 'w') as f:
        TestSuite.to_file(f, [ts])

if(args["prog"] == "1"):
    start_time = time.time()
    results = compare_documents_program_1(args["path1"], args["path2"])
    write_to_xml(results, start_time)

if(args["prog"] == "2"):
    start_time = time.time()
    results = compare_documents_program_2(args["path1"], args["path2"], args["exception"], int(args["occurrences"]))
    write_to_xml(results, start_time)