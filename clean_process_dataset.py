from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import re
import stripe
import pymongo

# MongoDB connection URL
MONGODB_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGODB_URL)
database = client['RestaurantOrderingAndReservation']
collection_restaurant = database['Restaurant']
collections_menu = database['Menu']
collections_food_cart = database['Food-Cart']


def clean_restaurant_collection():
    print("CLEANING RESTAURANT COLLECTION...")
    query_restaurants_without_address = {"$or": [{"zip_code": None}, {"zip_code": ""}]}
    cleaned_collection = collection_restaurant.delete_many(query_restaurants_without_address)

    # restaurant collection - replacing restaurant names containing "&amp;" with "&"
    restaurant_names = list(collection_restaurant.find({"name": {"$regex": "&amp;"}}))
    for restaurant in restaurant_names:
        current_name = restaurant["name"]

        collection_restaurant.update_one({
            "_id": restaurant["_id"]
        },
        {
            "$set": {"name": current_name.replace("&amp;", "&")}
        })
    print("RESTAURANT COLLECTION CLEANED!")


def clean_menu_collection():
    print("CLEANING MENU COLLECTION...")
    print("     Cleaning Category names...")
    menu_category_name = list(collections_menu.find({"category": {"$regex": "&amp;"}}))
    for category in menu_category_name:
        current_category_name = category["category"];

        collections_menu.update_one({
            "_id": category["_id"]
        },
            {
                "$set": {"category": current_category_name.replace("&amp;", "&")}
            })

    print("     Cleaning Item names...")
    menu_item_name = list(collections_menu.find({"name": {"$regex": "&amp;"}}))
    for item in menu_item_name:
        current_item_name = item["name"];

        collections_menu.update_one({
            "_id": item["_id"]
        },
            {
                "$set": {"name": current_item_name.replace("&amp;", "&")}
            })
    print("MENU COLLECTION CLEANED!")


if __name__ == "__main__":
    clean_restaurant_collection()
    clean_menu_collection()