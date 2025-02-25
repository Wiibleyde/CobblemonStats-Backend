#!/bin/python3
import json
import os
from flask import Flask, jsonify, request
from functools import lru_cache

app = Flask(__name__)

BASE_SERVER_PATH = os.getenv('BASE_SERVER_PATH', './Docker-data/les-chialeuses/cobblemon/')

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
    try:
        with open(BASE_SERVER_PATH + "world/stats/" + uuid + ".json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def get_user_achievements(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    with open(BASE_SERVER_PATH + "world/advancements/" + uuid + ".json", "r") as file:
        return json.load(file)
    
def get_user_playtime(data) -> int:
    return data.get("stats", {}).get("minecraft:custom", {}).get("minecraft:play_time", 0) // 20 // 60

def get_user_deaths(data) -> int:
    return data.get("stats", {}).get("minecraft:custom", {}).get("minecraft:deaths", 0)

def get_user_sneak_time(data) -> int:
    return data.get("stats", {}).get("minecraft:custom", {}).get("minecraft:sneak_time", 0) // 20 // 60

def get_user_distance_traveled(data) -> int:
    customStats = data.get("stats", {}).get("minecraft:custom", {})
    distance = customStats.get("minecraft:walk_one_cm", 0) + customStats.get("minecraft:swim_one_cm", 0) + customStats.get("minecraft:fly_one_cm", 0) + customStats.get("minecraft:boat_one_cm", 0) + customStats.get("minecraft:climb_one_cm", 0) + customStats.get("minecraft:sprint_one_cm", 0) + customStats.get("minecraft:walk_on_water_one_cm", 0) + customStats.get("minecraft:walk_under_water_one_cm", 0)
    return distance // 100 # Convert cm to meters

def get_lootball_openned(data) -> int:
    return data.get("stats", {}).get("minecraft:custom", {}).get("minecraft:open_loot_ball", 0)

def get_lootr_chests_openned(data) -> int:
    return data.get("stats", {}).get("minecraft:custom", {}).get("lootr:looted_stat", 0)

def get_leaderboard_playtime() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_stats(u)
        if stats is not None:
            playtime = get_user_playtime(stats)
            leaderboard.append({"user": u, "playtime": playtime})
    leaderboard.sort(key=lambda x: x["playtime"], reverse=True)
    return leaderboard

def get_leaderboard_deaths() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_stats(u)
        if stats is not None:
            deaths = get_user_deaths(stats)
            leaderboard.append({"user": u, "deaths": deaths})
    leaderboard.sort(key=lambda x: x["deaths"], reverse=True)
    return leaderboard

def get_leaderboard_sneak_time() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_stats(u)
        if stats is not None:
            sneak_time = get_user_sneak_time(stats)
            leaderboard.append({"user": u, "sneak_time": sneak_time})
    leaderboard.sort(key=lambda x: x["sneak_time"], reverse=True)
    return leaderboard

def get_leaderboard_distance_traveled() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_stats(u)
        if stats is not None:
            distance_traveled = get_user_distance_traveled(stats)
            leaderboard.append({"user": u, "distance_traveled": distance_traveled})
    leaderboard.sort(key=lambda x: x["distance_traveled"], reverse=True)
    return leaderboard

def get_learderboard_lootball_openned() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_stats(u)
        if stats is not None:
            lootball_openned = get_lootball_openned(stats)
            leaderboard.append({"user": u, "lootball_openned": lootball_openned})
    leaderboard.sort(key=lambda x: x["lootball_openned"], reverse=True)
    return leaderboard

def get_learderboard_lootr_chests_openned() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        stats = get_user_stats(u)
        if stats is not None:
            lootr_chests_openned = get_lootr_chests_openned(stats)
            leaderboard.append({"user": u, "lootr_chests_openned": lootr_chests_openned})
    leaderboard.sort(key=lambda x: x["lootr_chests_openned"], reverse=True)
    return leaderboard

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

@app.route(BASE_API_PATH_V1+'/leaderboard/playtime', methods=['GET'])
def api_get_leaderboard_playtime():
    return jsonify(get_leaderboard_playtime())

@app.route(BASE_API_PATH_V1+'/leaderboard/deaths', methods=['GET'])
def api_get_leaderboard_deaths():
    return jsonify(get_leaderboard_deaths())

@app.route(BASE_API_PATH_V1+'/leaderboard/sneak_time', methods=['GET'])
def api_get_leaderboard_sneak_time():
    return jsonify(get_leaderboard_sneak_time())

@app.route(BASE_API_PATH_V1+'/leaderboard/distance_traveled', methods=['GET'])
def api_get_leaderboard_distance_traveled():
    return jsonify(get_leaderboard_distance_traveled())

@app.route(BASE_API_PATH_V1+'/leaderboard/lootball_openned', methods=['GET'])
def api_get_leaderboard_lootball_openned():
    return jsonify(get_learderboard_lootball_openned())

@app.route(BASE_API_PATH_V1+'/leaderboard/lootr_chests_openned', methods=['GET'])
def api_get_leaderboard_lootr_chests_openned():
    return jsonify(get_learderboard_lootr_chests_openned())
# endregion

if __name__=='__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(host=host, port=port, debug=debug)