# Comp-Engine Scraper
Since [comp-engine.org](https://www.comp-engine.org/) seems to not offer an option to download all data with a quick single click anymore, I've made this script to get all data automatically.

The website is dynamically rendered, which means that a simple http request won't solve the problem. Therefore, here I'm using Selenium to scrape data automatically through a real web browser.

## Installation
After cloning this repository into your local machine:
```
pip install -Ur requirements.txt
```

## Usage
There is two main scripts: 'scrape.py' and 'merge_data.py'.

The 'scrape.py' recovers data from [comp-engine.org](https://www.comp-engine.org/) and store all downloaded .zip files in a local directory, while 'merge_data.py' extracts, merge and save the full data into a single .csv file.

To use both scripts just follow the instructions below:

### scrape.py
```
python scrape.py [-h] [--render] data_type start_on_page end_on_page
```
**Where:**
- **data_type:** must be 'real', 'synthetic' or 'unassigned';
- **start_on_page:** which page to start scrapping on. Must be 1 or larger;
- **end_on_page:** which page to end scrapping. Must be equal or larger than 'start_on_page';
- **-h:** shows help;
- **--render:** if not given, retrieve data using Firefox --headless option.

#### Examples:
Recovers the first 100 pages of real time-series:
```
python scrape.py real 1 100
```

Recovers the pages from index 150 to 325 of synthetic time-series:
```
python scrape.py synthetic 150 325
```

### merge_data.py
After downloading all your zip files, it is natural that you want a single .csv file containing all data, and not a bunch of .zip files. Luckily for you, I've made a script that solves this issue so you don't have to: 'merge_data.py'.
```
python merge_data.py [-h] [--no-unzip] [--no-clean] data_type
```
**Where:**
- **data_type:** same as 'scrape.py';
- **-h:** shows help;
- **--no-unzip:** use this option in case you already unzipped all files by yourself. Note that the .csv fragments must be within the same directory as the .zip files;
- **--no-clean:** in case you whant to keep all .csv fragments (stored in the same directory as the .zip files) from each .zip file after merging.

#### Examples:
Merge all real time-series .zip files into a single .csv:
```
python merge_data.py real
```
Merge all synthetic time-series .zip files into a single .csv:
```
python merge_data.py synthetic
```

## Dev notes
- I'm using Firefox as the web browser to scrape data. If you have Python and Selenium understandings, you may easily rewrite some lines of code in the scrape.py script to use another web browser. Good luck.
