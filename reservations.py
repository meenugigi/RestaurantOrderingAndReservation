import ast

import manage_imports
from manage_imports import *
client = Client(twilio_acoount_sid, twilio_auth_token)


async def make_reservation(request: Request, restaurant_id: int = Form(...)):
    """
        Functionality that allows users to make reservations. Allows users to reverse restaurant tables for next day.
        First fetches all the reservations for a given restaurant. Then fetches restaurant capacity.
        Further checks to see if the current number of bookings for that slot < max capacity of restaurant.
        If yes, then displays that slot on dropdown and is available to reserve.
   """
    user = request.session.get("user")
    first_name = user.get("first_name")
    last_name = user.get("last_name")
    email = user.get("email")
    contact =  user.get("contact")
    RestaurantID(
        restaurant_id=restaurant_id
    )
    reservation_slot_ids = []
    available_reservation_slots = []

    # getting current date and calculating max date until when calendar is open to make reservations.
    min_date = (datetime.now()+ timedelta(days=1)).strftime('%Y-%m-%d')
    max_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # fetch all reservations array for the list containing 'one' dictionary with '_id' as the key and '"reservations"
    # array as the key value. This list includes available and unavailable slots.
    get_all_reservations = (list(collection_restaurant.find({"id": restaurant_id}, {"reservations": 1})))[0]['reservations']

    # call method to get only available slots
    await _helper_get_available_slots(available_reservation_slots, get_all_reservations, reservation_slot_ids, restaurant_id)


    available_to_reserve_slot_list = []
    for reservation, _id, slot in zip(get_all_reservations, reservation_slot_ids, available_reservation_slots):
        # to get only the actual key instead of the format 'dict_keys(['09:00 AM - 09:30 AM'])'
        data = {}
        data['slots'] = slot[0]  # Extract the slot information. (eg slot = ['03:00 PM - 03:30 PM', '_id'])
        data['_id'] = _id  # Assign the _id
        available_to_reserve_slot_list.append(data)

    return templates.TemplateResponse("make_reservation.html", {"request": request,
                                                 "service_name": "FlavorFusion", "first_name": first_name, "email": email,
                                                 "last_name": last_name, "contact": contact, "min_date": min_date, "max_date": max_date,
                                                 "restaurant_id": restaurant_id, "reservation_slots": available_reservation_slots,
                                                 "available_to_reserve_slot_list": available_to_reserve_slot_list})


async def _helper_get_available_slots(available_reservation_slots, get_all_reservations, reservation_slot_ids, restaurant_id):
    """
        Helper method to check if a given slot is available for reservation. Fetches restaurant capacity.
        Further checks to see if the current number of bookings for that slot < max capacity of restaurant.
        If yes, then displays that slot on dropdown and is available to reserve.
   """
    # get_current_time = datetime.now().strftime("%I:%M %p")
    # current_time = datetime.strptime(get_current_time, "%I:%M %p")

    restaurant_capacity = collection_restaurant.find_one({"id": restaurant_id}, {"max_capacity": 1})
    # if the dict value for a slot < max capacity of restaurant, add that slot to available_reservation_slots list
    for reservation in get_all_reservations:
        # to get only the actual key instead of the format 'dict_keys(['09:00 AM - 09:30 AM'])'
        slot = list(reservation.keys())
        # slot[0] to fetch only the dict value for each slot. (eg: slot = ['07:00 PM - 07:30 PM', '_id'] )
        if reservation[slot[0]] < restaurant_capacity['max_capacity']:
            available_reservation_slots.append(list(reservation.keys()))
            reservation_slot_ids.append(reservation['_id'])
    print("capacity:", restaurant_capacity)
        # logic to display time slots greater than current time only. change min_date to today's date.
        # start_time = slot[0].split("-")
        # if((current_time < datetime.strptime(start_time[0].strip(), "%I:%M %p"))):
        #     reservation_slots.append(slot)


async def save_reservation_data(request: Request):
    """
        Save reservation form data into mongoDB 'Reservation' collection.
        Uses Twilio API to send text messages on customer contact to confirm reservation.
   """
    form_data = await request.json()
    user = request.session.get("user")
    reserved_by = user.get("email")
    full_name = form_data.get("full_name")
    email = form_data.get("email")
    contact = form_data.get("contact")
    date = form_data.get("date")
    no_of_guests = int(form_data.get("no_of_guests"))
    slot_reserved = form_data.get('slots', [])
    restaurant_id = int(form_data.get("restaurant_id"))
    slot_ids = form_data.get("slot_ids", [])

    try:
        collection_reservations.insert_one({"reserved_by": reserved_by, "full_name": full_name, "email": email,
                                            "restaurant_id":restaurant_id, "no_of_guests": no_of_guests,
                                            "contact": contact, "reservation_date": date, "slots_booked": slot_reserved})

        for id, dict_key in zip(slot_ids, slot_reserved):
            slot_id = ObjectId(id)
            collection_restaurant.update_one({"id": restaurant_id, "reservations._id": slot_id},
                                         {"$inc": {f"reservations.$.{dict_key}": no_of_guests}})

        send_text_message = Client(twilio_acoount_sid, twilio_auth_token).messages.create(
            body="Your reservation is successful! Thank you.",
            from_=twilio_phone_number,
            to=contact
        )
        print("status ", send_text_message.status)
    except Exception as e:
        print("Reservation failed!", e)




async def show_reservations(request: Request):
    """
        Fetches all reservations made by logged in user. Displays only upcoming reservations
        i.e displays only those reservations that have 'reservation_date' in mongoDB < today's date.
        Fetches restaurant_name from 'Restaurant' collection using 'id' attribute since 'Reservations' collection does
        not store restaurant name to maintain database independency.
   """
    user = request.session.get("user")
    first_name = user.get("first_name")
    email = user.get("email")
    current_date = datetime.now().strftime('%Y-%m-%d')

    get_bookings = list(collection_reservations.find({"reserved_by": email, "reservation_date": {"$gte": current_date}}))
    restaurant_ids = []
    restaurant_names = []

    for booking in get_bookings:
        restaurant_id = booking.get('restaurant_id')
        if restaurant_id:
            restaurant_ids.append(restaurant_id)

    # fetching restaurant_name for given restaurant_id.
    for id in restaurant_ids:
        name = collection_restaurant.find_one({"id": id}, {"name": 1})
        restaurant_names.append(name['name'])

    for booking, name in zip(get_bookings, restaurant_names):
        booking['restaurant_name'] = name


    return templates.TemplateResponse("show_reservations.html", {"request": request, "first_name": first_name,
                                             "service_name": "FlavorFusion", "get_bookings": get_bookings})



async def cancel_reservation(request: Request, reservation_id: str = Form(...)):
    """
        Fetches the reservation_id of the reservation that needs to be cancelled.
        Removes the reservation from mongoDB.
   """
    ReservationID(
        reservation_id=reservation_id
    )

    collection_reservations.delete_one({'_id': ObjectId(reservation_id)})


