# SteamAppScrape  
SteamAppScrape is a set of tools for scraping game data off of Steam and putting them into a database.
Originally created by **Jon Rutan (me) & Trevor Corcoran** for a class project, I've moved here for preservation and to continue working on.

## Relevant Folders  
* `./database` - Scripts, data, and SQL files related to the construction of the database
* `./webapp` - Interactable front-end website for the database

## Software Requirements
You must have the following installed on your machine to use the software in this repository: 
* [Python](https://www.python.org/) => Runs the scripts and website
* [Poetry](https://python-poetry.org/) => Install and manage dependencies

## Where and How

### Installing Dependencies and Configuring the Environment
With the aforementioned software requirements installed, run `poetry install` in the base directory.
This will install all necessary Python dependencies and is required to use any other functionality of this repository.

### Managing the Database
`./database` hosts a variety of scripts and software. See the README.md in that folder and any instructions from the
scripts inside the file or from their output to learn about using them.
  
In order to use a database you'll need to populate a local `.env` file in your project root. The following variables will be looked for:  
- `DB_USER`: Username for database access.  
- `DB_PASS`: Password for database access.  
- `DB_NAME`: Name of the database.  
- `DB_HOST`: Hostname of the database.  
- `STEAM_API_KEY` : A Steam dev api key, which can be found [here](https://steamcommunity.com/dev).  

### Running the Website
Inside the `./webapp` directory, run `make` to start the website.
It will be hosted on your [local machine](http://localhost:5000) using Flask.

