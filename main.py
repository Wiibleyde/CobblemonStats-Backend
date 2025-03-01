#!/bin/python3
import json
import os
from flask import Flask, jsonify, request, send_file
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import threading
import time
from nbt import nbt
from nbt.nbt import MalformedFileError

app = Flask(__name__)

BASE_SERVER_PATH = os.getenv('BASE_SERVER_PATH', '../Docker-data/les-chialeuses/cobblemon/')

BACKGROUND_PATH = os.getenv('IMAGE_PATH', './cobblemon.jpg')

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
    
# endregion

# region Cobblemon stats
def get_user_cobblemon_stats(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    try:
        with open(BASE_SERVER_PATH + "world/cobblemonplayerdata/" + uuid[0:2] + "/" + uuid + ".json", "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for user {username} with UUID {uuid}")
                return None
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

# region Dat files
def get_user_dat_file(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    try:
        nbtfile = nbt.NBTFile(BASE_SERVER_PATH + "world/playerdata/" + uuid + ".dat", "rb")
        return nbtfile
    except FileNotFoundError:
        return None
    except MalformedFileError:
        print(f"Malformed NBT file for user {username} with UUID {uuid}")
        return None
    
def get_user_money(data) -> int:
    try:
        return int(data["cardinal_components"]["numismatic-overhaul:currency"]["Value"].value)
    except KeyError:
        return 0

def get_leaderboard_money() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        dat = get_user_dat_file(u)
        if dat is not None:
            money = get_user_money(dat)
            leaderboard.append({"user": u, "money": money})
    leaderboard.sort(key=lambda x: x["money"], reverse=True)
    return leaderboard
    
def get_user_pokemon_pc_dat_file(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    try:
        nbtfile = nbt.NBTFile(BASE_SERVER_PATH + "world/pokemon/pcstore/" + uuid[0:2] + "/" + uuid + ".dat", "rb")
        return nbtfile
    except FileNotFoundError:
        return None
    except MalformedFileError:
        print(f"Malformed NBT file for user {username} with UUID {uuid}")
        return None
    
def get_user_pokemon_playerpartystore_dat_file(username: str) -> dict:
    uuid = get_uuid_from_user(username)
    if uuid is None:
        return None
    try:
        nbtfile = nbt.NBTFile(BASE_SERVER_PATH + "world/pokemon/playerpartystore/" + uuid[0:2] + "/" + uuid + ".dat", "rb")
        return nbtfile
    except FileNotFoundError:
        return None
    except MalformedFileError:
        print(f"Malformed NBT file for user {username} with UUID {uuid}")
        return None
    
def get_user_pokemon_count(pc_data, playerpartystore_data) -> int:
    total = 0
    for box in range(50):
        box_name = f"Box{box}"
        if box_name in pc_data:
            total += len(pc_data[box_name])
    for box in range(50):
        box_name = f"Slot{box}"
        if box_name in playerpartystore_data:
            total += len(playerpartystore_data[box_name])
    return total

def get_leaderboard_pokemon_count() -> list:
    users = get_all_users()
    leaderboard = []
    for u in users:
        pc_data = get_user_pokemon_pc_dat_file(u)
        playerpartystore_data = get_user_pokemon_playerpartystore_dat_file(u)
        if pc_data is not None and playerpartystore_data is not None:
            pokemon_count = get_user_pokemon_count(pc_data, playerpartystore_data)
            leaderboard.append({"user": u, "pokemon_count": pokemon_count})
    leaderboard.sort(key=lambda x: x["pokemon_count"], reverse=True)
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

# @app.route(BASE_API_PATH_V1+'/leaderboard/money', methods=['GET'])
# def api_get_leaderboard_money():
#     return jsonify(get_leaderboard_money())

@app.route(BASE_API_PATH_V1+'/leaderboard/pokemon_count', methods=['GET'])
def api_get_leaderboard_pokemon_count():
    return jsonify(get_leaderboard_pokemon_count())

@app.route(BASE_API_PATH_V1+'/leaderboard/image.jpg', methods=['GET'])
def api_get_leaderboard_image():
    return send_file("ranking.png", mimetype='image/png')
    
# endregion

# region Image generation
def generate_ranking_image(list1, list2, list3, background_path, output_path="ranking.png"):
    image = Image.open(background_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 35)
    title_font = ImageFont.truetype(font_path, 70)
    footer_font = ImageFont.truetype(font_path, 15)
    
    start_x = 70
    start_y = 150
    col_width = (image.width - 2 * start_x) // 3
    line_height = 50

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 200))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)
    
    title = "Leaderboard (Live)"
    draw.text((image.width // 2 - draw.textbbox((0, 0), title, font=title_font)[2] // 2, 50), title, fill="white", font=title_font)
    
    draw.text((start_x, start_y), "Nombre de pokémon dans le pokédex", fill="white", font=font)
    draw.text((start_x + col_width, start_y), "Nombre de pokémon capturés", fill="white", font=font)
    draw.text((start_x + 2 * col_width, start_y), "Temps de jeu (en minutes)", fill="white", font=font)

    colors = ["#cf980e", "#9da9ab", "#805b00", "white"]

    for index, entry in enumerate(list1, start=1):
        user = entry["user"]
        score = next(value for key, value in entry.items() if key != "user")
        text = f"{index}. {user} : {score}"
        color = colors[index - 1] if index <= 3 else colors[3]
        draw.text((start_x, start_y + index * line_height), text, fill=color, font=font)

    for index, entry in enumerate(list2, start=1):
        user = entry["user"]
        score = next(value for key, value in entry.items() if key != "user")
        text = f"{index}. {user} : {score}"
        color = colors[index - 1] if index <= 3 else colors[3]
        text_width = draw.textbbox((0, 0), text, font=font)[2]
        draw.text((start_x + col_width + (col_width - text_width) // 2, start_y + index * line_height), text, fill=color, font=font)

    for index, entry in enumerate(list3, start=1):
        user = entry["user"]
        score = next(value for key, value in entry.items() if key != "user")
        text = f"{index}. {user} : {score}"
        color = colors[index - 1] if index <= 3 else colors[3]
        text_width = draw.textbbox((0, 0), text, font=font)[2]
        draw.text((start_x + 2 * col_width + col_width - text_width, start_y + index * line_height), text, fill=color, font=font)

    draw.line([(start_x + col_width - 20, start_y), (start_x + col_width - 20, start_y + (max(len(list1), len(list2), len(list3)) + 1) * line_height)], fill="white", width=2)
    draw.line([(start_x + 2 * col_width - 20, start_y), (start_x + 2 * col_width - 20, start_y + (max(len(list1), len(list2), len(list3)) + 1) * line_height)], fill="white", width=2)

    draw.rectangle([start_x - 10, start_y - 10, start_x + col_width - 30, start_y + line_height], outline="white", width=2)
    draw.rectangle([start_x + col_width - 10, start_y - 10, start_x + 2 * col_width - 30, start_y + line_height], outline="white", width=2)
    draw.rectangle([start_x + 2 * col_width - 10, start_y - 10, start_x + 3 * col_width - 30, start_y + line_height], outline="white", width=2)

    # Footer text
    footer_text = "- Wiibleyde"
    draw.text((image.width - draw.textbbox((0, 0), footer_text, font=footer_font)[2] - 10, image.height - 50), footer_text, fill="white", font=footer_font)

    image = image.convert("RGB")
    image.save(output_path)

def generate_ranking_image_periodically():
    while True:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Generating ranking image at {now}")
        generate_ranking_image(get_leaderboard_pokedex_caught()[0:10], get_leaderboard_pokemon_caught()[0:10], get_leaderboard_playtime()[0:10], BACKGROUND_PATH)
        time.sleep(120)  # Sleep for 2 minutes

# endregion

# region Main
if __name__=='__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    
    # Start the background thread to generate the image periodically
    threading.Thread(target=generate_ranking_image_periodically, daemon=True).start()
    
    app.run(host=host, port=port, debug=debug)
# endregion