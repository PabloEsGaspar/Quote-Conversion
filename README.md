# QUOTE CONVERSION TOOL
**Email Based HTML to PDF Quote Conversion**<br />
*Kodama Group proprietary information* 

## Description
Program receives email with HTML attachment, extracts relevant data from HTML, uses data to create a PDF quote, and returns an email with the PDF quote as an attachment. 

## User Instructions
Email HTML file to <quote.conversion@gmail.com>. Emails limited to **ONE ATTACHMENT PER EMAIL**. Additional attachments from the same email will be ignored. Expect to receive response within one minute after intital email is sent. 

## Known Bugs
Emails to <quote.conversion@gmail.com> might get marked as spam, in which case they will not be seen by the program. To avoid being marked as spam provide developer with a list of sender email addresses. Filters will be updated so that emails received from those addresses will be kept out of the spam folder.  

## Support
Contact developer if you have any questions/issues, or to add additional functionality: <br />Gaspar Tonnesen - gaspartonnesen@gmail.com - 480-751-7157

## Project Skeleton 
Language: Python 3.7.9<br />
Deployment Environment: Heroku - Cloud Platform as a Service <br />
Docamatic API: Creates PDF quote from custom template and provided json data - endpoint: https://docamatic.com/api/v1/template 
#### Project Files:
File  | Contents 
:------------ | :------------
Quote.py | Classes/sub-classes that represent quotes, classes contain 'populate()' methods to scrape HTML and self populate attributes
Product.py | Classes/sub-classes that represent products, components, etc.. also contain methods to self-populate attributes
Conversion_Demo_01.py | Main method that iteratively checks inbox for new emails, and calls top level functions to carry out the quote conversion process
Procfile | Command to be executed upon startup (necessary for deployment) 
requirements.txt | Specifies dependencies (necessary for deployment)
runtime.txt | Specifies version of Python is used (necessary for deployment)
#### Important Packages 
Package  | Functionality
:------------ | :------------
requests  | Execute API POST requests to create PDF quote & email as attachment 
imaplib  | Connect to gmail account and access inbox   
BeautifulSoup | Works with HTML parser to search/navigate HTML and extract data  


