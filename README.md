# Google Sheets Domain Generator

A python script that converts columns of single words into tables of two-word domain name combinations, via the Google Sheets API.

Input is a cell range in a Google Sheets spreadsheet. Output tables are written to a new Sheet in the same spreadsheet.

## Installation

- Clone this project to your local machine

- Copy your spreadsheet ID from your spreadsheet URL, and assign it to the SPREADSHEET_ID variable in the *.env* file in the project directory - e.g:`SPREADSHEET_ID = “abcD-efGHIjjKl-mnoPQRsTUVwxyZ”`

- Turn on the Google Sheets API, and install the python Google API client library locally. To do this, follow steps 1) and 2) at
https://developers.google.com/sheets/api/quickstart/python

### Script Authorization 

- Execute the script with `python domain_generator.py` The first run triggers the Google API authorization process. A new browser table will open, and Google will prompt you to allow the script to access your spreadsheet.

Successful authorization stores an access token locally in the project folder - further executions will not require authorization. 

## Usage

Run 
`python domain_generator.py` from your command line. You will be prompted for a range and 
new sheet name. If left blank, the new sheet name will be a timestamp.

The script creates a new sheet in your spreadsheet, and writes the domain name tables via POST request.
