#!/bin/python3
import json
from flask import Flask, jsonify, request
from functools import lru_cache

app = Flask(__name__)

BASE_SERVER_PATH = "./"

# region User
def get_all_users() -> list:
    try:
        with open(BASE_SERVER_PATH + "usercache.json", "r") as file:
            data = json.load(file)
            return [user["name"] for user in data]
    except FileNotFoundError:
        print("usercache.json not found", BASE_SERVER_PATH + "usercache.json")
        return []

def get_user_from_uuid(uuid: str) -> str:
    with open(BASE_SERVER_PATH + "usercache.json", "r") as file:
        data = json.load(file)
        for user in data:
            if user["uuid"] == uuid:
                return user["name"]
        return None
    
def get_uuid_from_user(username: str) -> str:
    with open(BASE_SERVER_PATH + "usercache.json", "r") as file:
        data = json.load(file)
        for user in data:
            if user["name"] == username:
                return user["uuid"]
        return None
# endregion

# region Minecraft stats
def get_user_stats(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    with open(BASE_SERVER_PATH + "world/stats/" + uuid + ".json", "r") as file:
        return json.load(file)

def get_user_achievements(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    with open(BASE_SERVER_PATH + "world/advancements/" + uuid + ".json", "r") as file:
        return json.load(file)

# TODO: Add more stats like, time played, distance walked, deaths, etc.
    
# endregion

# region Cobblemon stats
def get_user_cobblemon_stats(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    try:
        with open(BASE_SERVER_PATH + "world/cobblemonplayerdata/" + uuid[0:2] + "/" + uuid + ".json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    
def get_pokemon_caught_count(data) -> int:
    return len(data.get("extraData", {}).get("captureCount", {}).get("defeats", {}))
    
def get_most_pokemon_caught() -> dict:
    users = get_all_users()
    most_pokemon_caught = 0
    user = None
    for u in users:
        stats = get_user_cobblemon_stats(u)
        if stats is not None:
            pokemon_caught = get_pokemon_caught_count(stats)
            if pokemon_caught > most_pokemon_caught:
                most_pokemon_caught = pokemon_caught
                user = u
    return {"user": user, "pokemon_caught": most_pokemon_caught}

def get_leaderboard_pokemon_caught() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_cobblemon_stats(u)
        if stats is not None:
            pokemon_caught = get_pokemon_caught_count(stats)
            leaderboard.append({"user": u, "pokemon_caught": pokemon_caught})
    leaderboard.sort(key=lambda x: x["pokemon_caught"], reverse=True)
    return leaderboard

def get_pokemon_caught_by_user(username: str) -> int:
    stats = get_user_cobblemon_stats(username)
    if stats is not None:
        return get_pokemon_caught_count(stats)
    return None

def get_pokedex_caught_by_user_data(data, shiny=False) -> int:
    if shiny:
        return len([p for p in data.get("extraData", {}).get("cobbledex_discovery", {}).get("registers", {}).values() if p.get("normal", {}).get("isShiny", False)])
    return len(data.get("extraData", {}).get("cobbledex_discovery", {}).get("registers", {}))

def get_pokedex_caught_by_user(username: str, shiny=False) -> int:
    stats = get_user_cobblemon_stats(username)
    if stats is not None:
        return get_pokedex_caught_by_user_data(stats, shiny)
    return None

def get_most_pokedex_caught(shiny=False) -> dict:
    users = get_all_users()
    most_pokedex_caught = 0
    user = None
    for u in users:
        stats = get_user_cobblemon_stats(u)
        if stats is not None:
            pokedex_caught = get_pokedex_caught_by_user_data(stats, shiny)
            if pokedex_caught > most_pokedex_caught:
                most_pokedex_caught = pokedex_caught
                user = u
    return {"user": user, "pokedex_caught": most_pokedex_caught}

def get_leaderboard_pokedex_caught(shiny=False) -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_cobblemon_stats(u)
        if stats is not None:
            pokedex_caught = get_pokedex_caught_by_user_data(stats, shiny)
            leaderboard.append({"user": u, "pokedex_caught": pokedex_caught})
    leaderboard.sort(key=lambda x: x["pokedex_caught"], reverse=True)
    return leaderboard

# endregion

# region Cache
@lru_cache(maxsize=128)
def cached_get_user_stats(username: str) -> dict:
    return get_user_stats(username)

@lru_cache(maxsize=128)
def cached_get_user_achievements(username: str) -> dict:
    return get_user_achievements(username)

@lru_cache(maxsize=128)
def cached_get_user_cobblemon_stats(username: str) -> dict:
    return get_user_cobblemon_stats(username)
# endregion

# region API
BASE_API_PATH_V1 = "/api/v1"

@app.route(BASE_API_PATH_V1+'/', methods=['GET'])
def api_get_root():
    pathes = app.url_map._rules
    baseJson = {
        "api": "Wiibleyde Stat Maker",
        "version": "1.0",
        "endpoints": []
    }
    for path in pathes:
        baseJson["endpoints"].append(path.rule)
    return jsonify(baseJson)

@app.route(BASE_API_PATH_V1+'/user/<username>/stats', methods=['GET'])
def api_get_user_stats(username):
    stats = cached_get_user_stats(username)
    if stats is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(stats)

@app.route(BASE_API_PATH_V1+'/user/<username>/achievements', methods=['GET'])
def api_get_user_achievements(username):
    achievements = cached_get_user_achievements(username)
    if achievements is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(achievements)

@app.route(BASE_API_PATH_V1+'/user/<username>/cobblemon_stats', methods=['GET'])
def api_get_user_cobblemon_stats(username):
    stats = cached_get_user_cobblemon_stats(username)
    if stats is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(stats)

@app.route(BASE_API_PATH_V1+'/leaderboard/pokemon_caught', methods=['GET'])
def api_get_leaderboard_pokemon_caught():
    return jsonify(get_leaderboard_pokemon_caught())

@app.route(BASE_API_PATH_V1+'/leaderboard/pokedex_caught', methods=['GET'])
def api_get_leaderboard_pokedex_caught():
    shiny = request.args.get('shiny', 'false').lower() == 'true'
    return jsonify(get_leaderboard_pokedex_caught(shiny))
# endregion

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Wiibleyde Cobblemon Stats Backend')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host')
    parser.add_argument('--port', type=int, default=5000, help='Port')
    parser.add_argument('--debug', type=bool, default=False, help='Debug')
    parser.add_argument('--path', type=str, default='./', help='Path')
    return parser.parse_args()

if __name__=='__main__':
    args = parse_args()
    BASE_SERVER_PATH = args.path
    app.run(host=args.host, port=args.port, debug=args.debug)