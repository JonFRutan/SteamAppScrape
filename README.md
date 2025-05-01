# Open Valve - Steam Game Recommendation System

## Project Overview
This repository contains the deliverables for the Database Design Project. The objective of this project is to create a database and front-end that provides Steam game recommendations based on the user's current library.
Using user-generated tags from the Steam storefront, the system identifies and suggests similar games. The reports provide an in-depth analysis of the database design, with the accompanying video presentations that offer further context regarding the design process, key considerations, and a demo of the final product.

## Authors
- **Jon Rutan**
- **Trevor Corcoran**

This our team name comes from a play on words of Valve and their Steam platform. We decided to "Open the Valve" to generate
better game recommendations!

## Deliverables
- Deliverable 4: **Project Pitch Video and Report** 
- Deliverable 5: **Design Document**
- Deliverable 7: **Complete Software Product**

## Relevant Folders
* `./reports` - Quarto source files of the reports
* `./docs` - Rendered html files of the reports
* `./database` - Scripts, data, and SQL files related to the construction of the database
* `./webapp` - Interactable front-end website for the database

## Software Requirements
You must have the following installed on your machine to use the software in this repository: 
* [Quarto](https://quarto.org/) => Renders report documents
* [Python](https://www.python.org/) => Runs the scripts and website
* [Poetry](https://python-poetry.org/) => Install and manage dependencies

## Where and How

### Viewing Reports
Simply open the `./docs/index.html` in a browser and click on the report you would like to view.

### Installing Dependencies and Configuring the Environment
With the aforementioned software requirements installed, run `poetry install` in the base directory.
This will install all necessary Python dependencies and is required to use any other functionality of this repository.

Now, you must configure the environment variables to allow for a connection to the database server.
Create a copy of `.env.sample` in the root directory and name it `.env`. Inside that file replace `<eID>` with your VCU eID.
Note that access to this database is limited to the creators of this project. You may create your own MySQL database with the data and scripts
inside the `./database` folder, if you desire to run this on your own. Just make sure to put the connection details in the .env and all other files should work.

### Rendering Reports
Inside the `./reports` directory, run the command `poetry run quarto render`.  
It will take a moment to run all Python code and compile the markdown into html, and then the output will be placed in `./docs`

### Managing the Database
`./database` hosts a variety of scripts and software. See the README.md in that folder and any instructions from the
scripts inside the file or from their output to learn about using them.

### Running the Website
Inside the `./webapp` directory, run `make` to start the website.
It will be hosted on your [local machine](http://localhost:5000) using Flask.

