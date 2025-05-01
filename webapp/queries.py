"""Holds a number of constructors for queries on the database."""

from helpers import run_sql_and_return_df

"""
Notes on what to include.

Done:
    * Games with no tags
    * Games with some tag
    * Games in a range of AppIDs
    * Games with a name
        * How many copies of "Kane & Lynch 2: Dog Days" are in the database
    * Pull a library and upload it to database

Not done:
* Find adult games and filter them out
* How many free games in the database (page that allows searching by tag name?)
* Show recommendation for a random game in library based on tags
* Give a recommendation for a given AppID
* Users ordered by game count
* Users who play the most free games
* Games with more than 10 tags
* Least used tags (tags with a count of <3)

This list not necessarily up to date.
"""


def gamesWithNoTagsSQL() -> str:
    return """
SELECT g.app_id, g.title, g.description, g.release_date
FROM Game g
LEFT JOIN GameTag gt ON g.app_id = gt.app_id
WHERE gt.tag_id is NULL;
    """


def gamesWithTagsSQL(tags, limit=20, num_matches=None, include_link=False) -> str:
    """names in tags case sensitive. Use limit parameter to change the LIMIT clause.
    num_matches sets the number of tags that a game must have in common with the tags list to be included. Defaults to all given tags.
    tags parameter can either be a single string for one tag or a list of strings for multiple."""

    # Detect if user wishes to include links to games
    STEAM_LINK = "https://store.steampowered.com/app/"
    link = ""
    if include_link:
        link = f", CONCAT('{STEAM_LINK}', g.app_id) AS Link"

    # Only one tag
    if type(tags) is str:
        return f"""
SELECT g.app_id, g.title{link}
FROM Game g
LEFT JOIN GameTag gt ON g.app_id = gt.app_id
LEFT JOIN Tag t on t.tag_id = gt.tag_id
WHERE t.name = '{tags}'
LIMIT {limit};
"""
    # Multiple tags
    else:
        # Configure minimum number of tags that must match to be included
        num_matches = len(tags) if num_matches is None else num_matches

        where_clause = "WHERE t.name IN ("

        for idx, tag in enumerate(tags):
            if tag.find("'") == -1:  # Make sure no tags with single quotes are included
                where_clause += f"'{tag}'"

                # Only add commas if this tag is not the last
                if idx < len(tags) - 1:
                    where_clause += ", "

        where_clause += ")"  # Close out where clause

        return f"""
SELECT g.app_id, g.title{link}
FROM Game g
JOIN GameTag gt ON g.app_id = gt.app_id
JOIN Tag t ON gt.tag_id = t.tag_id
{where_clause}
GROUP BY g.app_id, g.title
HAVING COUNT(DISTINCT t.tag_id) = {num_matches}
LIMIT {limit};
"""


def viewRangeOfAppIDsSQL(from_id: int, to_id: int) -> str:
    """From and To IDs are inclusive"""
    return f"""
SELECT *
FROM Game
WHERE app_id >= {from_id} AND app_id <= {to_id}
"""


def gamesWithNameSQL(name: str) -> str:
    return f"""
SELECT *
FROM Game
WHERE title = '{name}'
"""


def queryHasResult(cnx, sql_query: str) -> bool:
    """Returns True if query returns any result. False if it returns no records.
    Yes, this is a super scuffed way of doing it."""

    query = run_sql_and_return_df(cnx, sql_query)

    appid_already_exists = str(query).find("no records returned")

    if appid_already_exists != -1:  # AppID is not in database
        return False
    else:  # AppID is in the database
        return True


def appidExists(cnx, appid: int) -> bool:
    """Checks if this AppID is found in the Game table. Returns a boolean."""
    sql_query = f"SELECT * FROM Game WHERE app_id = {appid}"
    return queryHasResult(cnx, sql_query)


def getRecommendationSQL(cnx, appid: int, num_matches=10) -> str:
    """Takes in an appid and finds a suitable recommendation and returns it.
    Requires a database connection."""

    # Make sure the requested game exists
    if not appidExists(cnx, appid):
        return f"-- ERROR: No AppID {appid} exists in the database"

    else:
        find_tags_query = f"""
SELECT t.name
FROM Game g
LEFT JOIN GameTag gt ON g.app_id = gt.app_id
LEFT JOIN Tag t ON t.tag_id = gt.tag_id
WHERE g.app_id = {appid}
"""
        # Query database and extract tags from origin game
        origin = run_sql_and_return_df(cnx, find_tags_query)
        origin_tags = []
        for cell in origin.values:
            origin_tags.append(cell[0])

        return gamesWithTagsSQL(origin_tags, limit=50, num_matches=num_matches, include_link=True)
