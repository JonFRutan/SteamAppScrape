"""
Author: Trevor Corcoran, Jon Rutan
License: MIT License
"""

from bs4 import BeautifulSoup as bs # Web scraping
import json #json file dumping - may be easier/smaller footprint
import urllib.request # Get webpage data
from datetime import datetime # Handle dates
import multiprocessing as mp # Multiprocessing capabilities
from os import getpid # Show process id of workers for fun
import pickle # Store data as a binary object to be given to SQL scripts
# Sleep functions to avoid rate limiting
from random import uniform
from time import sleep
from sys import argv

MAX_PROCESSES = 4 # Max number of concurrent scrapers. Keep low to avoid rate limiting
AppIDs = (1, 100) # Running from main will process all AppIDs from left (inclusive) to right (exclusive)
#PICKLE_FILE was changed from using colons to underscores, as Windows systems don't allow colons in file names.
PICKLE_FILE = f"../database/SteamData_&_{datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.pickle"
OUTPUT = "pickle";

def scrape(arg):
    """Scrapes steam web pages and returns a dict with all the information as follows:
        - title: Game title
        - tags: List of user tags
        - description: Game description
        - release_date: Datetime object of game's release date
        - appID: Game's AppID
        """
    #allows it to accept AppIDs as an argument
    if isinstance(arg, int):
        url = f"https://store.steampowered.com/app/{arg}/"
    elif isinstance(arg, str):
        url = arg

    # Scrapes a specific URL
    try:
        html_download = urllib.request.urlopen(url).read()
    except:
        return None

    soup = bs(html_download, "html.parser")

    result = {}

    # Game title
    try:
        title = soup.find("div", id="appHubAppName", class_="apphub_AppName").text.strip()
        result.update({"title" : title})
    except AttributeError:  # AppID is an invalid game
        return None

    # Tags
    tags = []
    
    tag_list = soup.find_all('a', {'class': 'app_tag'})
    
    if tag_list:
        if len(tag_list) > 1:
            for tag in tag_list:
                tags.append(tag.text.strip())

    result.update({"tags" : tags})

    #other fields within our ER diagram - jon
    try:
        description = soup.find("div", class_="game_description_snippet")
        if description:
            result.update({"description": description.text.strip()})
        else:
            result.update({"description": "No description."})
        result.update({"description": description.text.strip()})
    except AttributeError:
        return None

    try:
        release = soup.find("div", class_="date")
        release = release.text.strip()
        release = datetime.strptime(release, "%b %d, %Y")
        result.update({"release_date": release})
    except AttributeError:
        return None

    app_id = url.strip("/").split("/")[-1]
    result.update({"appID": int(app_id)})

    return result


def scrapeProcess(args):
    """Runs scrape() function and puts result into the queue
    args[0] -> AppID passes to scrape
    args[1] -> queue to deposit resulting data in"""
    
    # Sleep 1-3 seconds to avoid rate limiting
    sleep(uniform(1, 3))

    print(f"Process {getpid()} => Pulling AppID {args[0]}")
    
    result = scrape(args[0])
    if result is not None:
        args[1].put(result)


def processQueue(queue):
    """Takes in a multiprocessing queue of all web scraped data and does something with it"""
    
    gameDataList = []

    # Iterate until queue is empty
    while not queue.empty():
        gameData = queue.get()
        gameDataList.append(gameData)
        printGameData(gameData)

    # Pickle (store in binary) data to PICKLE_FILE
    if (OUTPUT == "pickle") :
        with open(PICKLE_FILE, 'wb') as handle:
            pickle.dump(gameDataList, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # JSON (stored in plaintext) data to JSON_FILE      
    elif (OUTPUT == "json"):
        JSON_FILE = PICKLE_FILE.replace(".pickle", ".json")
        with open(JSON_FILE, 'w', encoding='utf-8') as handle:
            json.dump(gameDataList, handle, ensure_ascii=False, indent=4, default=str)

def printGameData(gameData: dict):
    """Prints game data from scrape()"""

    if gameData is None:
        return

    print(f"""AppID {gameData["appID"]}
    - Title: {gameData["title"]}
    - Description: {gameData["description"]}
    - Date Released: {datetime.strftime(gameData["release_date"], "%Y/%m/%d")}
    - Tags: {gameData["tags"]}""")

    
if __name__ == "__main__":
    #if 2 arguments are provided, they're cast into ints and used for AppID indices.
    #Furthermore, a third argument may be provided to specify a file output type.
    if len(argv) >= 3:
        AppIDs = (int(argv[1]), int(argv[2]))
        if len(argv) == 4:
            OUTPUT = argv[3].lower()
            if OUTPUT not in ("pickle", "json"):
                print(f"{OUTPUT} not supported. Using '.pickle")
                OUTPUT = "pickle"
    else:
        print("Error: Should be at least two arguments.\nUsage: python scrape.py first_app_id last_app_id filetype")
        print("AppIDs are Steam game AppIDs, and filetype can be \"json\" or \"pickle\"")
        exit(0)
    
    # Append AppID range to file name
    PICKLE_FILE = PICKLE_FILE.replace("&", f"{AppIDs[0]}-{AppIDs[1]}")

    app_count = int(argv[2]) - int(argv[1])
    eta_seconds = (app_count / MAX_PROCESSES) * 2 #total ids to process divided by process count and multipled by average wait time of 2 seconds.

    print(f"SteamScraper reporting for duty!\nMax Processes {MAX_PROCESSES}\nFrom AppID {AppIDs[0]} -> {AppIDs[1] - 1}\nOutputting in {OUTPUT} format.")
    print(f"Processing {app_count} apps.\nETA: {eta_seconds} seconds.")
    print("=" * 50)

    # Run through requested range and output
    AppIDsRange = list(range(AppIDs[0], AppIDs[1]))

    # Run with MAX_PROCESSES number of workers
    manager = mp.Manager()
    queue = manager.Queue()
    with mp.Pool(processes=MAX_PROCESSES) as pool:
        pool.map(scrapeProcess, [(appid, queue) for appid in AppIDsRange])

    # Process data gathered from steam
    print("=" * 50)
    print(f"Scraping complete! Outputting results...")
    processQueue(queue)

