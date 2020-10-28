# PDF Comparison
## Installation
- pip install pdfminer

## Usage
- Run pdf_miner.py in the command line, with two additional arguments:
 - "-1" with the path to the first pdf
 - "-2" with the path to the second pdf
- The results will be output to output.xml 

## Reading the Results
### Full Match
- The program has identified no material differences in the content of the documents

### Partial Match
- Each segement of one document can be found in the other, however, the documents are not a perfect match
- The content may be out of order

### No Match
- The documents are not a match 
- At least one document contains additional content to the other
- results.csv will list all additional content found in each document