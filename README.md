# Open Valve - Steam Game Recommendation System

## Project Overview
This repository contains the deliverables for the Database Design Project. The objective of this project is to create a database and front-end that provides Steam game recommendations based on the user's current library.
Using user-generated tags from the Steam storefront, the system identifies and suggests similar games. The reports provide an in-depth analysis of the database design, with the accompanying video presentations that offer further context regarding the design process, key considerations, and a demo of the final product.

## Authors
- **Jon Rutan**
- **Trevor Corcoran**

This our team name comes from a play on words of Valve and their Steam platform. We decided to "Open the Valve" to generate
better game recommendations!

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
  
In order to use a database you'll need to populate a local `.env` file in your project root. See the README.md in database for more info.  

### Running the Website
Inside the `./webapp` directory, run `make` to start the website.
It will be hosted on your [local machine](http://localhost:5000) using Flask.

