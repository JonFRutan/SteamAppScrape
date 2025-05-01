"""Contains some functions that interact with the Steam API"""
"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=XXXXXXXXXXXXXXXXX&steamid=76561197960434622&format=json"

import requests, os, json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('STEAM_API_KEY')

def get_user_and_library(user_id: str, api_key: str) -> str:
    """Takes a steam user ID and returns their game library"""
    summary = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/' #summary of user info
    games_summary = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    resolve_custom_id = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'

    # First check if given user id is a custom, non-numeric id.
    if not user_id.isnumeric():
        # Make a Steam API call to get the user's numeric identifer
        params = {
            'key': api_key,
            'vanityurl': user_id
        }
        resolve_response = requests.get(resolve_custom_id, params=params)
        response = resolve_response.json().get('response')

        # Check if user id actually exists
        if response.get('success') == 1:  # User DOES exist
            user_id = response.get('steamid')
            print(user_id)
        else:  # User does NOT exist
            raise ValueError("Player not found, check Steam ID")


    games_params = {
        'key': api_key,
        'steamid': user_id,
        'include_appinfo': True,
        'include_played_free_games': True,
        'format': 'json',
    }

    user_params = {
        'key': api_key,
        'steamids': user_id
    }

    user_summary_response = requests.get(summary, params=user_params)
    #print(f"Status: {user_summary_response.status_code}")
    #print(f"Response text: {user_summary_response.text}")
    user_summary_json = user_summary_response.json()

    games_summary_response = requests.get(games_summary, params=games_params)
    #print(f"Status: {games_summary_response.status_code}")
    #print(f"Response text: {games_summary_response.text}")
    games_summary_json = games_summary_response.json()

    players = user_summary_json.get('response', {}).get('players', [])
    if not players:
        raise ValueError("Player Not found, check Steam ID")
    
    username = players[0].get('personaname', "na") #'na' is used for default

    user_info = {
        'username': username,
        'steam_id': user_id,
        'games': []
    }

    for game in games_summary_json.get('response', {}).get('games', []):
        user_info['games'].append({
            'name': game['name'],
            'appid': game['appid'],
        })
    
    return json.dumps(user_info)

if __name__ == "__main__":
    user_id = input("enter a user_id: ")
    print(f"{get_user_and_library(user_id, api_key)}")
