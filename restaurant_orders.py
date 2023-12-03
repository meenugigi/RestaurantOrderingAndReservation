import manage_imports
from manage_imports import *

async def get_restaurants(request: Request):
    """
       Fetches user-firstname from session data. Takes a restaurant name/ zip/ address location string from the
       search bar and returns list of restaurants from 'Restaurants' collection in mongoDB for that specific location.
   """
    form_data = await request.form()
    first_name = request.session['user'].get("first_name")
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
    }, {"id": 1, "name": 1}))

    return templates.TemplateResponse("restaurants.html", {"request": request,"service_name": "FlavorFusion",
                                             "first_name": first_name, "matched_restaurants": matched_restaurants})




async def get_menu(request: Request):
    """
       Fetches the list of menu items from the 'Menu' collection in mongoDB against the requested restaurant id.
       Groups the menu items by category attribute.
   """
    form_data = await request.form()
    restaurant_id = int(form_data.get('restaurant_id'))
    restaurant_name = collection_restaurant.find_one({"id": restaurant_id}, {"name": 1})
    first_name = request.session['user'].get("first_name")
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
    menu_category = list(collection_menu.aggregate(pipeline))
    return templates.TemplateResponse("menu.html", {"request": request,"service_name": "FlavorFusion",
                                                   "restaurant_id": restaurant_id, "restaurant_name" : restaurant_name['name'],
                                                     "menu_category": menu_category, "first_name": first_name})



async def add_to_cart(request: Request):
    """
       Adds the requested item to cart on clicking the 'Add' button on UI.
       Inserts the item into 'Food-Cart' collection on mongoDB.
       Re-clicking 'Add' button against previously added item, increases quantity by 1 and updates the quantity
       against the same item in the 'Food-Cart' collection in mongoDB.
   """
    form_data = await request.form()
    item_name = form_data.get("item-name")
    item_price = form_data.get("item-price")
    restaurant_name = form_data.get("restaurant_name")
    restaurant_id = int(form_data.get('restaurant_id'))
    email = request.session['user'].get("email")

    existing_item = collection_food_cart.find_one({
        'restaurant_id': restaurant_id,
        'item_name': item_name,
        'item_price': item_price,
    })
    # if item already exists in collection, then increase quantity by 1.
    if existing_item:
        collection_food_cart.update_one({
            "_id": existing_item["_id"]
        },
        {
            "$inc": {"quantity": 1}
        })
    #     if item does not exist in collection, insert item details as new entry into collection.
    else:
        collection_food_cart.insert_one({'email': email,
            'restaurant_id': restaurant_id, 'restaurant_name': restaurant_name,
            'item_name': item_name, 'item_price': item_price, 'quantity': 1})
    return {"item name:", item_name}



async def get_cart_items(request: Request):
    """
       Fetches cart items from 'Food-Cart' collection in mongoDB against the requested restaurant id.
       Displays cart items on menu page when user adds item to cart.
   """
    form_data = await request.form()
    restaurant_id = int(form_data.get("restaurant_id"))
    email = request.session['user'].get("email")
    try:
        # Retrieve cart items for the given restaurant_id from MongoDB
        cart_items = list(collection_food_cart.find({"restaurant_id": restaurant_id, "email": email}))

        # Convert ObjectId to string for each document
        for item in cart_items:
            item['_id'] = str(item['_id'])  # Convert _id to string
        return cart_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def calculate_checkout_amount(request: Request):
    """
       Calculates total checkout amount for all items added to cart for a specific restaurant id.
       The total amount is displayed on the menu page.
   """
    form_data = await request.form()
    restaurant_id = int(form_data.get("restaurant_id"))
    try:
        # Retrieve cart items for the given restaurant_id from MongoDB
        cart_items = list(collection_food_cart.find({"restaurant_id": restaurant_id}))
        total_price = 0

        for item in cart_items:
            item_price = item['item_price']
            slice_price = slice(-4)
            item_quantity = item['quantity']
            total_price += (float(item_price[slice_price]) * int(item_quantity))

        return round(total_price, 2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def delete_from_cart(request: Request):
    """
       Functionality to delete an item from cart on clicking the 'delete icon' on UI.
       Removes the item from 'Food-Cart' collection in mongoDB.
   """
    form_data = await request.form()
    item_id = form_data.get("item_id")
    collection_food_cart.delete_one({'_id': ObjectId(item_id)})
    # print("item_id: ", item_id)
    return {"form data", item_id}



async def reduce_item_quantity_cart(request: Request):
    """
       Functionality to decrease item quantity by 1 if quantity > 1 on clicking 'minus icon' on UI.
       If quantity == 1, deletes item from cart.
       Updates are made in 'Food-Cart' collection on mongoDB.
   """
    form_data = await request.form()
    item_id = form_data.get("item_id")
    item_detail = collection_food_cart.find_one({"_id": ObjectId(item_id)})
    if item_detail:
        item_quantity = item_detail.get("quantity")
        # decrease item quantity by 1 if quantity > 1.
        if item_quantity > 1:
            collection_food_cart.update_one({
                "_id": item_detail["_id"]
            },
    {
                "$inc": {"quantity": -1}
            })
        # if quantity == 1, delete item from cart.
        elif item_quantity == 1:
            await delete_from_cart(request)
    return ({"quantity: ", item_quantity})



async def increase_item_quantity_cart(request: Request):
    """
       Functionality to increase item quantity by 1 on clicking the 'plus icon' on UI.
       Updates are made in 'Food-Cart' collection on mongoDB.
   """
    form_data = await request.form()
    item_id = form_data.get("item_id")
    item_detail = collection_food_cart.find_one({"_id": ObjectId(item_id)})
    if item_detail:
        collection_food_cart.update_one({
            "_id": item_detail["_id"]
        },
{
            "$inc": {"quantity": 1}
        })
    return ({"quantity: ", item_id})







async def order_checkout(request: Request):
    """
       Directs user to order checkout page on clicking 'Checkout' button on menu page.
       Fetches stored session data for logged in user and autofills input fields on place-order page.
       Displays the details of the items to checkout along with price and quantity.
       Displays fields to enter personal details, address and payment details.
   """
    form_data = await request.form()
    first_name = request.session['user'].get("first_name")
    last_name = request.session['user'].get("last_name")
    email = request.session['user'].get("email")
    contact = request.session['user'].get("contact")
    restaurant_name = form_data.get("restaurant_name")
    restaurant_id = int(form_data.get("restaurant_id"))

    restaurant_zipcode = collection_restaurant.find_one({"id": restaurant_id}, {"zip_code": 1})
    items_to_checkout = list(collection_food_cart.find({"restaurant_id": restaurant_id}))

    total_amount = await calculate_checkout_amount(request)

    return templates.TemplateResponse("order_checkout.html", {"request": request,"service_name": "FlavorFusion",
                                                   "restaurant_name": restaurant_name, "restaurant_id": restaurant_id,
                                                   "items_to_checkout": items_to_checkout, "total_amount": total_amount,
                                                   "first_name":first_name, "last_name": last_name, "email": email,
                                                   "contact": contact, "restaurant_zipcode": restaurant_zipcode['zip_code']})





async def place_order(request: Request):
    """
       Autofills data on place-order page for input fields using stored session data.
       Displays the details of items being checked out along with price and quantity details.
       Calls function to validate payment using Stripe API.
       Generates a timestamp to track when the order was placed.
       Generates a structure to store order details in the 'Orders' collection on mongoDB.
       The structure contains an array to store the details of each item in the order.
       Updates 'Accounts' collection to reflect the newly placed order.
       If no account exists in the 'Accounts' collection against given email, create new Account and link the
       _id of the newly placed order with this account.
       If account with given email exists, add _id of newly placed order to array storing the _ids of all orders
       placed from this account.
       If payment and database updates were successful, redirect user to view-my-orders page.
       If payment or database updates were unsuccessful, throw error message and stay on the same place-order page.
   """
    (address, card_number, contact, cvc, email, exp_month, exp_year, first_name, last_name, restaurant_id,
     restaurant_name, total_amount, unit_suite, zip_code) = await _helper_get_inputs(request)
    first_name = request.session['user'].get("first_name")
    last_name = request.session['user'].get("last_name")
    email = request.session['user'].get("email")
    contact = request.session['user'].get("contact")

    # fetching zipcode to auto fill zipcode input field on form on checkout page.
    restaurant_zipcode = collection_restaurant.find_one({"id": restaurant_id}, {"zip_code": 1})
    # fetch all items to checkout for a specific restaurant id.
    items_to_checkout = list(collection_food_cart.find({"restaurant_id": restaurant_id},
                                                       {"item_name":1, "item_price":1, "quantity":1}))

    try:
        # validate payment credentials
        _helper_validate_payment_details(card_number, exp_month, exp_year, cvc, total_amount)
        # get current timestamp
        order_timestamp = str(datetime.now())
        format_datetime = datetime.strptime(order_timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")

        # creating a structure that contains a list of checked out items for each order placed.
        order = {
            "email": email,
            "restaurant_id": restaurant_id,
            "total_amount": total_amount,
            "timestamp": datetime.strptime(format_datetime, "%Y-%m-%d %H:%M:%S"),
            "status": "Order Placed",
            "items": items_to_checkout
        }
        # Insert the created order into the orders collection
        collection_orders.insert_one(order)

        # delete items from food-cart after placing order.
        collection_food_cart.delete_many({"email": email, "restaurant_id": restaurant_id})

        # fetch the mongodb auto generated unique _id for each order from the 'Orders' collection against a given email.
        order_id = list(collection_orders.find({"email": email}, {"_id": 1}))
        # insert the newly placed order's _id into the list of orders placed from current account.
        account_details = {
            "first_name": first_name, "last_name" : last_name, "email": email, "contact": contact, "address": address,
            "unit_suite": unit_suite, "zip_code": zip_code, "card_number": card_number, "exp_month": exp_month,
            "exp_year": exp_year, "cvc": cvc, "order_id": order_id
        }

        # check if a record for the given email id exists in "Accounts" collections in mongoDB.
        account_exist = collection_account_info.find_one({"email": email})

        # if accounts collection does not have an existing record for given email, create a new record.
        # if account exists, add order_id to array containing the list of all orders placed through given email id.
        if account_exist:
            collection_account_info.update_one({
                "_id": account_exist["_id"]
            },
            {
                "$addToSet": {"order_id": order_id}
            })
        else:
            collection_account_info.insert_one(account_details)
    # if payment fails, displays error and stay on place-order page.
    except stripe.error.CardError as e:
        return templates.TemplateResponse("order_checkout.html", {"request": request, "service_name": "FlavorFusion",
                                                   "restaurant_name": restaurant_name, "restaurant_id": restaurant_id,
                                                   "items_to_checkout": items_to_checkout, "total_amount": total_amount,
                                                   "restaurant_zipcode": restaurant_zipcode['zip_code'], "error": e.error.message,
                                                   "first_name":first_name, "last_name": last_name, "email": email,
                                                   "contact": contact})
    # if payment is successful, redirect user to view-my-orders page.
    return RedirectResponse(url="/view-my-orders", status_code=303)





async def get_my_orders(request: Request):
    """
       Directs user to my-orders page to view all orders placed by logged in user.
       Fetches the order details from the 'Orders' collection in mongoDB against the user email.
       Fetches 'restaurant_name' using 'restaurant_id' attribute in 'Orders' collection ('Orders' collection does not
       store 'restaurant_name' to remove data redundancy in database.)
       Formats 'timestamp' value (eg: 2023-11-26T18:54:49.000+00:00 is formatted to display 2023-11-26 on the UI).
   """
    first_name = request.session['user'].get("first_name")
    email = request.session['user'].get("email")
    restaurant_ids = []
    restaurant_names = []
    format_datetime = []
    current_account_placed_orders = list(collection_orders.find({"email": email}))

    for order in current_account_placed_orders:
        restaurant_id = order.get('restaurant_id')
        # format timestamp value
        timestamp = str(order.get('timestamp'))[:10]
        if timestamp:
            format_datetime.append(timestamp)
        if restaurant_id:
            restaurant_ids.append(restaurant_id)

    # fetching restaurant_name for given restaurant_id.
    for id in restaurant_ids:
        name = collection_restaurant.find_one({"id": id}, {"name": 1})
        restaurant_names.append(name['name'])

    for order, name, order_date in zip(current_account_placed_orders, restaurant_names, format_datetime):
        order['restaurant_name'] = name
        order['formatted_timestamp'] = order_date
    return templates.TemplateResponse("my_orders.html", {"request": request, "service_name": "FlavorFusion",
                                             "first_name": first_name, "current_account_placed_orders": current_account_placed_orders})


async def _helper_get_inputs(request):
    """
       Gets user inputted data from place-order page.
   """
    form_data = await request.form()
    restaurant_id = int(form_data.get("restaurant_id"))
    restaurant_name = form_data.get("restaurant_name")
    first_name = form_data.get("first_name")
    last_name = form_data.get("last_name")
    email = form_data.get("email")
    contact = form_data.get("contact")
    address = form_data.get("address")
    unit_suite = form_data.get("unit_suite")
    zip_code = form_data.get("zip_code")
    card_number = form_data.get("card_number")
    exp_month = form_data.get("exp_month")
    exp_year = form_data.get("exp_year")
    cvc = form_data.get("cvc")
    total_amount = float(form_data.get("total_amount"))
    return address, card_number, contact, cvc, email, exp_month, exp_year, first_name, last_name, restaurant_id, restaurant_name, total_amount, unit_suite, zip_code




def _helper_validate_payment_details(card_number, exp_month, exp_year, cvc, total_amount):
    """
       Validates payment using Stripe API.
   """
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
        all_order = list(collection_orders.find({}))
        current_time = datetime.now()
        for order in all_order:
            get_timestamp = order.get('timestamp')
            time_difference = (current_time - get_timestamp).total_seconds()
            # Calculate hours, minutes, and seconds from the total_seconds
            hours = int(time_difference // 3600)
            minutes = int((time_difference % 3600) // 60)
            seconds = int(time_difference % 60)
            time_difference = timedelta(hours=hours, minutes=minutes, seconds=seconds)

            threshold_order_accepted = timedelta(minutes=20)
            threshold_order_processing = timedelta(minutes=30)
            threshold_order_on_the_way = timedelta(minutes=80)
            threshold_order_delivered = timedelta(minutes=120)
            if time_difference >= threshold_order_accepted and time_difference < threshold_order_processing:
                collection_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "Order Accepted"}
                })
            elif time_difference >= threshold_order_processing and time_difference < threshold_order_on_the_way:
                collection_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "Processing Order"}
                })
            elif time_difference >= threshold_order_on_the_way and time_difference < threshold_order_delivered:
                collection_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "On the way"}
                })
            else:
                collection_orders.update_one({
                    "_id": order['_id']
                },
                {
                    "$set": {"status": "Delivered"}
                })
        await asyncio.sleep(120)