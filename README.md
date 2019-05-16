# polizeiberichte_scraper
A simple webscraper for local police reports with basic NLP and text mining on the gathered data

# Functions:
## Scraper
The scraper extracts data from the press articles of the Frankfurt police department 
https://www.presseportal.de/blaulicht/nr/4970/

The raw data is scraped, cleaned up and stored in a csv file.

## Analysis
The notebooks TextAnalysis2.ipynb and TextAnalysis3.ipynb contain basic analysis of the data.

## Author prediction
the probabilities for each author.

The model was built in the notebook author_prediction_model_notebook.ipynb. Currently we use a 
plain vanilla support vector machine on the tfidf matrix.

The model was trained on a complete scrape of the ~8000 articles that were available at May 8th 2019.

Most of the articles that were published since then were correctly classified by the algorithm.

## How to try author prediction
To try the author prediction yourself, download the pickled model from /resources/pickled/ and the 
notebook predict_author.ipynb .
Just paste the article text (of course without the author token :-) ) into the variable new_text as a raw string, 
then execute the notebook. The barplot that is generated in the last cell shows the predicted probabilities for the authors.

You can also write your own article into the variable and see which author it fits best.