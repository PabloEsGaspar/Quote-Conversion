# QUOTE CONVERSION TOOL HTML to PDF
**Email Based HTML to PDF Quote Conversion**<br />
*Kodama Group proprietary information* 

## Description
User sends email with HTML attachment(s), tool extracts relevevant data from the HTML file then sends the data to Docamatic API in the form of a json request. Docamatic converts the json request into a PDF quote and emails it to <quotes@kodamagroup.com> as an attachment. 

## User Instructions
Email HTML file to <quote.conversion@gmail.com>. Ensure you have a subject like 'Quote Conversion' to avoid spam filters. You may send multiple HTML attachments in the same email. Expect to receive response 1 to 5 minutes after your intital email is sent. You will recieve one response email for for each HTML file you originally sent. each response email will contain one attachment of the converted PDF quote. If the application fails to convert one of the HTML files it will send a warning message to <quotes@kodamagroup.com> with notice that the application remains operational, but a particualr HTML file was unable to be converted. 

## Known Bugs
1. Emails to <quote.conversion@gmail.com> might get marked as spam, in which case they will not be seen by the program. Ways to avoid being marked as spam are: Include subject and body when sending your request email. Add user email addresses to Gmail filters so messages from those addresses never get marked as spam (or provide a list user emails to developer to update filters).
2. The response email may also end up in your spam folder. To avoid this you can add a filter to your email that prevents emails recevied from <no-reply@docamatic.com> from being marked as spam.   
3. For anyone using a corporate email, the response message may not make it past your company's firewall. Solution unknown. 

## Support
Contact developer with any questions, or to add new functionality: <br />Gaspar Tonnesen - gaspartonnesen@gmail.com - 480-751-7157

## Project Skeleton 
Language: Python 3.7.9<br />
Deployment Environment: Heroku - Cloud PaaS <br />
Docamatic API: Creates PDF quote using a custom template and json post request - endpoint: https://docamatic.com/api/v1/template 
#### Project Files:
File  | Contents 
:------------ | :------------
Quote.py | Classes/sub-classes that represent quotes, classes contain 'populate()' methods to scrape HTML and self populate attributes
Product.py | Classes/sub-classes that represent products, components, etc.. also contain methods to self-populate attributes
Conversion_Demo_01.py | Main method that iteratively checks <quote.conversion@gmail.com> inbox for new emails, calls top level functions to carry out the quote conversion process, packages quote data into json request, sends post request to Docamatic API's template url   
Procfile | Command to be executed upon startup (necessary for deployment) 
requirements.txt | Specifies dependencies (necessary for deployment)
runtime.txt | Specifies version of Python is used (necessary for deployment)
#### Important Packages 
Package  | Functionality
:------------ | :------------
requests  | Execute API POST requests to create PDF quote & email as attachment 
imaplib  | Connect to gmail account and access inbox   
BeautifulSoup | Works with HTML parser to search/navigate HTML and extract data  


