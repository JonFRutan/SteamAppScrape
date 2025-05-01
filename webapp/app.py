"""
Authors: Jon Rutan and Trevor Corcoran
Assignment: CMSC-408 Semester Project Web App
Instructor: Dr. Leonard
Date: Spring 2025
Description: Provides a web interface to our Steam database that we
scraped. The idea is to provide recommendations based on games that the user already owns.
"""
# Module imports
import flask as fl
import json

# Local imports
import scrape as sc
from helpers import create_db_wrapper, run_sql_and_return_html, run_sql_and_return_df
import steamAPI as steam
import db_handler as db
import queries as queries

# Resources
# https://realpython.com/python-web-applications/
# https://flask.palletsprojects.com/en/stable/quickstart/#
# https://developer.valvesoftware.com/wiki/Steam_Web_API#GetOwnedGames_(v0001)

# Start flask
app = fl.Flask(__name__)

# Initiate database connection
config_map = {
    'user': "DB_USER",
    'password': "DB_PASS",
    'host': "DB_HOST",
    'database': "DB_NAME",
    'steam_key': "STEAM_API_KEY"
}
cnx, config = create_db_wrapper(config_map)


def display_query(sql: str, title="SQL Query Display") -> str:
    """Runs a SQL query and returns it inside a query_display.html template.
    Returns a full html file."""
    query_result = run_sql_and_return_html(cnx, sql)
    return fl.render_template("query_display.html", query=sql, dataframe=query_result, title=title)


def display_game(sql: str, title="View Game") -> str:
    """Runs a SQL query and returns it inside a game_display.html template.
    Returns a full html file."""
    query_result = run_sql_and_return_html(cnx, sql)
    return fl.render_template("game_display.html", query=sql, dataframe=query_result, title=title)


@app.route("/")
def index():
    return fl.render_template("index.html")


@app.route("/about")
def about():
    """Displays a short about page."""
    return fl.render_template("about.html")


@app.route("/add", methods=["POST", "GET"])
def scrape():
    """Displays an input form that allows a user to scrape Steam for an AppID.
    If scrape is successful, the data is displayed as well."""

    if fl.request.method == 'GET':
        # Show just the input form
        return fl.render_template("appid.html", data_available=False)

    else:  # Show the form and the resulting data.

        # Get AppID as form input
        try:
            appid = int(fl.request.form['AppID'])
        except TypeError:
            appid = None

        # Check if database already has this AppID
        show_appid_query = f"SELECT * FROM Game WHERE app_id = {appid}"
        query = run_sql_and_return_df(cnx, show_appid_query)
        print("DATAFRAME for " + str(appid) + ":\n" + str(query))

        appid_already_exists = str(query).find("no records returned")
        if appid_already_exists != -1:  # AppID is not already in database
            data = sc.scrape(appid)  # Get data from AppID

            # Check response for success
            if data is not None:  # The AppID is real, upload to database then view it
                print(f"AppID {appid} request VALID and NEW. Adding to database...")
                #data = sc.gameDataToString(data)

                # Upload data to database and redirect
                db.from_data(cnx, data)
                return fl.redirect(fl.url_for("view_game", appid=appid))

            else:  # The AppID is not real
                data = f"No game found for AppID {appid}. Please try another."
            return fl.render_template("appid.html", appdata=data, data_available=True)

        else:  # AppID is already in the database
            return fl.redirect(fl.url_for("view_game", appid=appid))  # Redirect to that record


@app.route("/view/<int:appid>", methods=["POST", "GET"])
def view_game(appid):
    """Queries the Database for a game with the provided AppID"""
    return display_game(f"SELECT * FROM Game WHERE app_id = {appid}", title=f"Display AppID {appid}")

@app.route("/view", methods=["POST"])
def view_game_form():
    """Handles the form submission to view a game by AppID."""
    try:
        appid = int(fl.request.form['appid'])
        return fl.redirect(fl.url_for('view_game', appid=appid))
    except Exception as e:
        return f"Invalid AppID entered: {e}"

@app.route("/library/<user_id>")
def view_library(user_id):
    return steam.getLibrary(user_id, config['steam_key'])

@app.route("/import_user", methods=["POST", "GET"])
def import_user():
    if fl.request.method == "GET":
        return fl.render_template("import_user.html", data_available=False)
    else:
        try:
            user_id = fl.request.form['SteamID']
            user_info_json = steam.get_user_and_library(user_id, config['steam_key'])
            user_info = json.loads(user_info_json)

            db.import_user_and_library(cnx, user_info)
            return fl.render_template(
                "import_user.html",
                data_available=True,
                result=f"Successfully imported user {user_info['username']} (SteamID: {user_id}) and their games)"
            )
            

        except Exception as e:
            return fl.render_template(
                "import_user.html",
                data_available=True,
                result=f"Failed to import user {user_id}: {e}"
            )
        
@app.route("/update_game", methods=["POST", "GET"])
def update_game():
    if fl.request.method == "GET":
        return fl.render_template("update_game.html", data_available=False)
    else:
        try:
            appid = int(fl.request.form['AppID'])
            new_title = fl.request.form['NewTitle']
            new_description = fl.request.form['NewDescription']
            result = db.update_game(cnx, appid, new_title, new_description)
            return fl.render_template("update_game.html", data_available=True, result=result)
        except Exception as e:
            return fl.render_template("update_game.html", data_available=True, result=f"Err: {e}")

@app.route("/delete_game", methods=["POST", "GET"])
def delete_game():
    if fl.request.method == "GET":
        return fl.render_template("delete_game.html", data_available=False)
    else:
        try:
            appid = int(fl.request.form['AppID'])
            result = db.delete_game(cnx, appid)
            return fl.render_template("delete_game.html", data_available=True, result=result)
        except Exception as e:
            return fl.render_template("delete_game.html", data_available=True, result=f"Err: {e}")


@app.route("/rec", methods=["POST", "GET"])
def recommendation():
    """Displays a game recommendation based on the given appid"""

    # Definine search strength levels
    strengths = [
        {"value": "10", "name": "Normal"},
        {"value": "5", "name": "Weak"},
        {"value": "15", "name": "Strong"}
    ]

    # Display input page for GETs
    if fl.request.method == "GET":
        return fl.render_template("recommendation.html", display_result=False, strengths=strengths)

    # Display recommendation result
    else:
        # Run query
        appid = int(fl.request.form['appid'])
        num_matches = int(fl.request.form['strength'])
        query = queries.getRecommendationSQL(cnx, appid, num_matches=num_matches)
        query_result = run_sql_and_return_html(cnx, query)
        return fl.render_template("recommendation.html", display_result=True, query=query, dataframe=query_result, appid=appid, strengths=strengths)
