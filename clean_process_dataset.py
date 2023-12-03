import random
from datetime import datetime, timedelta

import bson
from pymongo import MongoClient


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

    menu_item_name = list(collections_menu.find({"name": {"$regex": "'"}}))
    for item in menu_item_name:
        current_item_name = item["name"];

        collections_menu.update_one({
            "_id": item["_id"]
        },
            {
                "$set": {"name": current_item_name.replace("'", "")}
            })
    print("MENU COLLECTION CLEANED!")


def update_restaurant_collection():
    opening_times = ['9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM']
    closing_times = ['5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM', '8:00 PM', '8:30 PM',
                     '9:00 PM', '9:30 PM', '10:00 PM', '10:30 PM', '11:00 PM']
    restaurant_list = list(collection_restaurant.find({}))


    for restaurant in restaurant_list:
        random_opening_time = random.choice(opening_times)
        random_closing_time = random.choice(closing_times)
        random_capacity = random.randint(40, 250)

        start_time = datetime.strptime(random_opening_time, "%I:%M %p")
        close_time = datetime.strptime(random_closing_time, "%I:%M %p")
        # time_intervals = generate_time_intervals(start_time, close_time)
        time_intervals = []
        for i, interval in enumerate(generate_time_intervals(start_time, close_time)):
            interval['_id'] = bson.ObjectId()  # Generate a unique ObjectId for each interval
            time_intervals.append(interval)

        collection_restaurant.update_one({
            "_id": restaurant['_id']
        },
            {
                "$set": {"opens_at": random_opening_time,
                        "closes_at": random_closing_time,
                         "max_capacity": random_capacity,
                         "reservations": time_intervals}

            })
    print("UPDATE ON 'RESTAURANT' COLLECTION SUCCESSFUL!")




def generate_time_intervals(start_time, end_time):
    time_intervals = []
    current_time = start_time

    while current_time < end_time:
        end_interval_time = current_time + timedelta(minutes=30)
        if end_interval_time > end_time:
            end_interval_time = end_time

        interval_dict = {
            f"{current_time.strftime('%I:%M %p')} - {end_interval_time.strftime('%I:%M %p')}": 0
        }
        time_intervals.append(interval_dict)
        current_time = end_interval_time

    return time_intervals



if __name__ == "__main__":
    # clean_restaurant_collection()
    clean_menu_collection()
    # update_restaurant_collection()