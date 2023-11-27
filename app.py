import threading

from bson import ObjectId
from fastapi import FastAPI, HTTPException, BackgroundTasks
import schedule
from fastapi.security import APIKeyCookie
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import stripe
import pymongo
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from datetime import datetime, timedelta, time
import asyncio

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

cookie_key = "secret_key_here"  # Replace with your secret key
security = APIKeyCookie(name="session", auto_error=False)

SECRET_KEY = "my-secret-key"
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Password hashing helper using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection URL
MONGODB_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGODB_URL)
database = client['RestaurantOrderingAndReservation']
collection_restaurant = database['Restaurant']
collections_menu = database['Menu']
collections_food_cart = database['Food-Cart']
collections_orders = database['Orders']
collections_account_info = database['Accounts']


class Restaurant(BaseModel):
    name: str
    location: str

class MenuItem(BaseModel):
    name: str
    description: str
    price: float

class Reservation(BaseModel):
    date_time: str
    party_size: int

class OrderItem(BaseModel):
    item_id: int
    quantity: int


# Set up session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)






async def start_background_task():
    asyncio.create_task(update_order_status())

@app.on_event("startup")
async def startup_event():
    await start_background_task()


@app.get("/")
async def default_page(request: Request):
    try:
        first_name = request.session.get("first_name")
        return templates.TemplateResponse("index.html", {"request": request,
                                                         "service_name": "FlavorFusion", "first_name": first_name})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request,
                                                    "service_name": "FlavorFusion"})


@app.post("/sign-up")
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "service_name": "FlavorFusion",
                                                      "action": "Sign up"})

@app.post("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "service_name": "FlavorFusion",
                                             "action": "Log in"})

@app.post("/logout")
async def logout(request: Request):
    request.session.pop("first_name", None)
    request.session.pop("last_name", None)
    request.session.pop("email", None)
    request.session.pop("contact", None)
    return RedirectResponse(url="/", status_code=303)


@app.post("/validate-login")
async def validate_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    user = collections_account_info.find_one({"username": username})
    if user and pwd_context.verify(password, user['password']):
        request.session['first_name'] = user['first_name']
        request.session['last_name'] = user['last_name']
        request.session['email'] = user['email']
        request.session['contact'] = user['contact']
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "service_name": "FlavorFusion",
                                                     "action": "Log in", "error": "Invalid login credentials!"})


@app.post("/submit-form")
async def validate_signup(request: Request):
    form = await request.form()
    first_name = form.get("first_name")
    last_name = form.get("last_name")
    username = form.get("username")
    password = form.get("password")
    email = form.get("email")
    contact = form.get("contact")
    address = form.get("address")
    unit_suite = form.get("unit_suite")
    zip_code = form.get("zip_code")

    encrypted_password = pwd_context.hash(password)

    collections_account_info.insert_one({"first_name": first_name, "last_name": last_name, "username": username,
                                         "password": encrypted_password, "email": email, "contact": contact, "address": address,
                                         "unit_suite": unit_suite, "zip_code": zip_code})

    request.session['first_name'] = first_name
    request.session['last_name'] = last_name
    request.session['email'] = email
    request.session['contact'] = contact
    return RedirectResponse(url="/", status_code=303)




@app.post("/get-restaurants")
async def get_restaurants(request: Request):
    form_data = await request.form()
    first_name = request.session.get("first_name")
    # takes address, zipcode, restaurant name as input
    input = form_data["search-input"]
    # Query MongoDB to find restaurants where the full address contains the obtained input
    # matched_restaurants = collection_restaurant.find({"full_address": {"$regex": address, "$options": "i"}})
    matched_restaurants = list(collection_restaurant.find({
        "$or": [
            {"full_address": {"$regex": input, "$options": "i"}},
            {"zipcode": {"$regex": input, "$options": "i"}},
            {"restaurant_name": {"$regex": input, "$options": "i"}}
        ]
    }))

    return templates.TemplateResponse("restaurants.html", {"request": request,"service_name": "FlavorFusion",
                                             "first_name": first_name, "matched_restaurants": matched_restaurants})


@app.post('/get-menu')
async def get_menu(request: Request):
    data = await request.form()
    restaurant_id = int(data.get('restaurant_id'))
    restaurant_name = collection_restaurant.find_one({"id": restaurant_id}, {"name": 1})

    first_name = request.session.get("first_name")
    # create pipeline to get menu items from menu collection for the respective restaurant id.
    pipeline = [
        {
            "$match": {"restaurant_id": restaurant_id}  # Filter by restaurant_id obtained previously
        },
        {
            "$group": {
                "_id": "$category",  # Grouping by the category field
                "items": {"$push": "$$ROOT"}  # Push the matching documents into the items array
            }
        }
    ]
    # Perform the aggregation
    menu_category = list(collections_menu.aggregate(pipeline))
    return templates.TemplateResponse("menu.html", {"request": request,"service_name": "FlavorFusion",
                                                   "restaurant_id": restaurant_id, "restaurant_name" : restaurant_name['name'],
                                                     "menu_category": menu_category, "first_name": first_name})


@app.post("/add-to-cart")
async def add_to_cart(request: Request):
    form = await request.form()
    item_name = form.get("item-name")
    item_price = form.get("item-price")
    restaurant_name = form.get("restaurant_name")
    restaurant_id = int(form.get('restaurant_id'))
    email = request.session.get("email")

    existing_item = collections_food_cart.find_one({
        'restaurant_id': restaurant_id,
        'item_name': item_name,
        'item_price': item_price,
    })
    if existing_item:
        collections_food_cart.update_one({
            "_id": existing_item["_id"]
        },
{
            "$inc": {"quantity": 1}
        })
    else:
        collections_food_cart.insert_one({'email': email,
            'restaurant_id': restaurant_id, 'restaurant_name': restaurant_name,
            'item_name': item_name, 'item_price': item_price, 'quantity': 1})
    return {"item name:", item_name}


@app.post("/get-cart-items")
async def get_cart_items(request: Request):
    form = await request.form()
    restaurant_id = int(form.get("restaurant_id"))
    email = request.session.get("email")
    try:
        # Retrieve cart items for the given restaurant_id from MongoDB
        cart_items = list(collections_food_cart.find({"restaurant_id": restaurant_id, "email": email}))

        # Convert ObjectId to string for each document
        for item in cart_items:
            item['_id'] = str(item['_id'])  # Convert _id to string
        return cart_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-checkout-amount")
async def calculate_checkout_amount(request: Request):
    form = await request.form()
    restaurant_id = int(form.get("restaurant_id"))
    try:
        # Retrieve cart items for the given restaurant_id from MongoDB
        cart_items = list(collections_food_cart.find({"restaurant_id": restaurant_id}))
        total_price = 0

        for item in cart_items:
            item_price = item['item_price']
            slice_price = slice(-4)
            item_quantity = item['quantity']
            total_price += (float(item_price[slice_price]) * int(item_quantity))

        return round(total_price, 2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete-from-cart")
async def delete_from_cart(request: Request):
    form = await request.form()
    item_id = form.get("item_id")
    collections_food_cart.delete_one({'_id': ObjectId(item_id)})
    # print("item_id: ", item_id)
    return {"form data", item_id}


@app.post("/decrease-item-quantity-cart")
async def reduce_item_quantity_cart(request: Request):
    form = await request.form()
    item_id = form.get("item_id")
    item_detail = collections_food_cart.find_one({"_id": ObjectId(item_id)})
    if item_detail:
        item_quantity = item_detail.get("quantity")
        if item_quantity > 1:
            collections_food_cart.update_one({
                "_id": item_detail["_id"]
            },
    {
                "$inc": {"quantity": -1}
            })
        elif item_quantity == 1:
            await delete_from_cart(request)
    return ({"quantity: ", item_quantity})


@app.post("/increase-item-quantity-cart")
async def add_item_quantity_cart(request: Request):
    form = await request.form()
    item_id = form.get("item_id")
    item_detail = collections_food_cart.find_one({"_id": ObjectId(item_id)})
    if item_detail:
        collections_food_cart.update_one({
            "_id": item_detail["_id"]
        },
{
            "$inc": {"quantity": 1}
        })
    return ({"quantity: ", item_id})


@app.post("/order-checkout")
async def order_checkout(request: Request):
    form = await request.form()
    first_name = request.session.get("first_name")
    last_name = request.session.get("last_name")
    email = request.session.get("email")
    contact = request.session.get("contact")
    restaurant_name = form.get("restaurant_name")
    restaurant_id = int(form.get("restaurant_id"))

    restaurant_zipcode = collection_restaurant.find_one({"id": restaurant_id}, {"zip_code": 1})
    items_to_checkout = list(collections_food_cart.find({"restaurant_id": restaurant_id}))

    total_amount = await calculate_checkout_amount(request)

    return templates.TemplateResponse("order_checkout.html", {"request": request,"service_name": "FlavorFusion",
                                                   "restaurant_name": restaurant_name, "restaurant_id": restaurant_id,
                                                   "items_to_checkout": items_to_checkout, "total_amount": total_amount,
                                                   "first_name":first_name, "last_name": last_name, "email": email,
                                                   "contact": contact, "restaurant_zipcode": restaurant_zipcode['zip_code']})




@app.post("/place-order")
async def place_order(request: Request):
    (address, card_number, contact, cvc, email, exp_month, exp_year, first_name, last_name, restaurant_id,
     restaurant_name, total_amount, unit_suite, zip_code) = await get_inputs(request)
    first_name = request.session.get("first_name")
    last_name = request.session.get("last_name")
    email = request.session.get("email")
    contact = request.session.get("contact")

    # fetching zipcode to auto fill zipcode input field on form on checkout page.
    restaurant_zipcode = collection_restaurant.find_one({"id": restaurant_id}, {"zip_code": 1})
    # fetch all items to checkout for a specific restaurant id.
    items_to_checkout = list(collections_food_cart.find({"restaurant_id": restaurant_id},
                                                        {"item_name":1, "item_price":1, "quantity":1}))

    try:
        # validate payment credentials
        validate_payment_details(card_number, exp_month, exp_year, cvc, total_amount)
        # creating a structure that contains a list of checked out items for each order placed.
        order_timestamp = str(datetime.now())
        format_datetime = datetime.strptime(order_timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")

        order = {
            "email": email,
            "restaurant_id": restaurant_id,
            "total_amount": total_amount,
            "timestamp": datetime.strptime(format_datetime, "%Y-%m-%d %H:%M:%S"),
            "status": "Order Placed",
            "items": items_to_checkout
        }
        # Insert the created order into the orders collection
        collections_orders.insert_one(order)

        # delete items from food-cart after placing order.
        collections_food_cart.delete_many({"email": email, "restaurant_id": restaurant_id})

        # fetch the mongodb auto generated unique _id for the given email.
        order_id = list(collections_orders.find({"email": email}, {"_id": 1}))
        # insert the newly placed order's _id into the list of orders placed from current account.
        account_details = {
            "first_name": first_name, "last_name" : last_name, "email": email, "contact": contact, "address": address,
            "unit_suite": unit_suite, "zip_code": zip_code, "card_number": card_number, "exp_month": exp_month,
            "exp_year": exp_year, "cvc": cvc, "order_id": order_id
        }

        # check if accounts collections have a record for the given email id.
        account_exist = collections_account_info.find_one({"email": email})

        # if accounts collection does not have an existing record for given email, create a new record.
        # if account exists, add order_id to array containing the list of all orders placed through given email id.
        if account_exist:
            collections_account_info.update_one({
                "_id": account_exist["_id"]
            },
            {
                "$addToSet": {"order_id": order_id}
            })
        else:
            collections_account_info.insert_one(account_details)

    except stripe.error.CardError as e:
        return templates.TemplateResponse("order_checkout.html", {"request": request, "service_name": "FlavorFusion",
                                                   "restaurant_name": restaurant_name, "restaurant_id": restaurant_id,
                                                   "items_to_checkout": items_to_checkout, "total_amount": total_amount,
                                                   "restaurant_zipcode": restaurant_zipcode['zip_code'], "error": e.error.message,
                                                   "first_name":first_name, "last_name": last_name, "email": email,
                                                   "contact": contact})
    return RedirectResponse(url="/view-my-orders", status_code=303)




@app.get("/view-my-orders")
async def get_my_orders(request: Request):
    first_name = request.session.get("first_name")
    email = request.session.get("email")
    restaurant_ids = []
    restaurant_names = []
    format_datetime = []
    current_account_placed_orders = list(collections_orders.find({"email": email}))

    for order in current_account_placed_orders:
        restaurant_id = order.get('restaurant_id')
        timestamp = str(order.get('timestamp'))[:10]
        if timestamp:
            format_datetime.append(timestamp)
        if restaurant_id:
            restaurant_ids.append(restaurant_id)

    for id in restaurant_ids:
        name = collection_restaurant.find_one({"id": id}, {"name": 1})
        restaurant_names.append(name['name'])

    for order, name, order_date in zip(current_account_placed_orders, restaurant_names, format_datetime):
        order['restaurant_name'] = name
        order['formatted_timestamp'] = order_date

    # await update_order_status(request)
    return templates.TemplateResponse("my_orders.html", {"request": request, "service_name": "FlavorFusion",
                                             "first_name": first_name, "current_account_placed_orders": current_account_placed_orders})


async def get_inputs(request):
    form = await request.form()
    restaurant_id = int(form.get("restaurant_id"))
    restaurant_name = form.get("restaurant_name")
    first_name = form.get("first_name")
    last_name = form.get("last_name")
    email = form.get("email")
    contact = form.get("contact")
    address = form.get("address")
    unit_suite = form.get("unit_suite")
    zip_code = form.get("zip_code")
    card_number = form.get("card_number")
    exp_month = form.get("exp_month")
    exp_year = form.get("exp_year")
    cvc = form.get("cvc")
    total_amount = float(form.get("total_amount"))
    return address, card_number, contact, cvc, email, exp_month, exp_year, first_name, last_name, restaurant_id, restaurant_name, total_amount, unit_suite, zip_code


def validate_payment_details(card_number, exp_month, exp_year, cvc, total_amount):
    payment_api = stripe.PaymentIntent.create(
        amount = int(total_amount * 100),
        currency = "USD",
        payment_method_data = {
            "type": "card",
            "card": {
                "number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
        },
        )
    # Confirm the PaymentIntent to proceed with the payment
    stripe.PaymentIntent.confirm(
        payment_api.id,
        return_url="http://127.0.0.1:8000/order-checkout",
    )








async def update_order_status():
    while True:
        all_order = list(collections_orders.find({}))


        current_time = datetime.now()
        print("****************************************************************")
        for order in all_order:
            get_timestamp = order.get('timestamp')
            time_difference = (current_time - get_timestamp).total_seconds()
            # Calculate hours, minutes, and seconds from the total_seconds
            hours = int(time_difference // 3600)
            minutes = int((time_difference % 3600) // 60)
            seconds = int(time_difference % 60)
            time_difference = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            print("OBJECT:----------", time_difference)
            # print(" TIME DIFFERENCE", time_difference)
            threshold_order_accepted = timedelta(minutes=20)
            print("threshold: ", threshold_order_accepted)
            threshold_order_processing = timedelta(minutes=30)
            threshold_order_on_the_way = timedelta(minutes=80)
            threshold_order_delivered = timedelta(minutes=120)
            if time_difference >= threshold_order_accepted and time_difference < threshold_order_processing:
                collections_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "Order Accepted"}
                })
            elif time_difference >= threshold_order_processing and time_difference < threshold_order_on_the_way:
                collections_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "Processing Order"}
                })
            elif time_difference >= threshold_order_on_the_way and time_difference < threshold_order_delivered:
                collections_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "On the way"}
                })
            else:
                collections_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "Delivered"}
                })
        await asyncio.sleep(120)



def my_function():
    print("Inside my_function")

def another_function():
    print("Inside another_function")

if __name__ == "__main__":
    # Code here will be executed only when this script is run directly
    print("This is executed when the script is run directly")
    my_function()
    another_function()




