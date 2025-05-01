# Steam Scraper and Database Import

**By Trevor Corcoran and Jon Rutan**

This script checks a range of Steam AppIDs and scrapes pertinent data that is saved to a json file.

The scraping process is run concurrently on four worker processes, and between each request to steam is
a delay between one to three seconds to prevent rate limiting. Do NOT lower this value else your
IP will be blocked by Steam for some time.

### Tools

* [Poetry](https://python-poetry.org/) => Python dependency management
* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) => Web scraping library

### Getting started

You will need to have Poetry installed, along with a modern Python interpreter. Then run in the root directory

`poetry install`

With poetry having installed the correct dependencies, you may now use these programs.

## Programs and Usage

#### `scrape.py`

`poetry run python scrape.py <from-id> <to-id> <format>`

The program will scrape Steam on the range of AppIDs supplied, and then output in the specified format (`json` (default) or `pickle`).

#### `import.py`

`poetry run python import.py`

One running, it will initiate a database connection then prompt you for the file path to the .json of the data.
This data will be uploaded to the database, any tags linked correctly or created if necessary.

## Acknowledgement

Thanks to @EthanStanks for their [SteamWebScraper](https://github.com/EthanStanks/SteamWebScraper/) project. No license was given,
so I will mention them here as some of the code and much inspiration came from their example for `scrape.py`
