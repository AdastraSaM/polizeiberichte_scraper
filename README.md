# polizeiberichte_scraper
A simple webscraper for local police reports with basic NLP and text mining on the gathered data

# Functions:
## Scraper
The scraper extracts data from the press articles of the Frankfurt police department 
https://www.presseportal.de/blaulicht/nr/4970/

The raw data is scraped, cleaned up and stored in a csv file.

## Analysis
The notebook Basic_Analysis.ipynb can be used for basic inspection of the data and its metadata. The more advanced text
analytics are currently contained in the notebook PolizeiScrape2.3.ipynb. They will be rewritten as a standalone python 
module.

## Upcoming features
The following extensions could be implemented
* Inclusion of more (meta-)data from the scraped pages
* Extension of the scraping to more departments (capping at country-level by scraping news for all German departments)