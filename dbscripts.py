"""
There's probably a better way to do this, but...

... I'm lazy ¯\_(ツ)_/¯

these aren't actually used in the code, just used whenever i need to mass update something in the db
"""
import tokens
from pymongo import MongoClient

cluster = MongoClient(tokens.db_url)
db = cluster["test"]

def update_all_users(key, value):
    for user in db["users"].find():
        if user["_id"] == "placeholder":
            continue
        db["users"].update_one({"_id": user["_id"]}, {"$set": {key: value}})

def unset_from_all_users(key):
    for user in db["users"].find():
        if user["_id"] == "placeholder":
            continue
        db["users"].update_one({"_id": user["_id"]}, {"$unset": {key: 1}})

update_all_users("military", {"troops": 0, "tanks": 0, "artillery": 0, "frigates": 0, "destroyers": 0, "cruisers": 0, "submarines": 0, "aircraft_carriers": 0, "fighter_aircraft": 0, "bomber_aircraft": 0, "attack_aircraft": 0})