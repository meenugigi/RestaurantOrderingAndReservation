import reservations
import restaurant_orders
import user_authentication
import manage_imports
from manage_imports import *

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

# class SearchInput(BaseModel):
#     search_input: str



# Set up session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)



async def start_background_task():
    asyncio.create_task(restaurant_orders.update_order_status())

@app.on_event("startup")
async def startup_event():
    await start_background_task()


@app.get("/")
async def default_page(request: Request):
    """
       The default start up page. Fetches username from session data and displays username if user has logged in.
       Else, displays log in and sign up buttons.
   """
    try:
        response = await user_authentication.default_page(request)
        return response
    except Exception as e:
        print("Failure on Default-Page ", e)


@app.post("/sign-up")
async def signup(request: Request):
    """
       Directs user to sign-up page.
   """
    try:
        response = await user_authentication.signup(request)
        return response
    except Exception as e:
        print("Failure on Signup-Page ", e)


@app.post("/login")
async def login(request: Request):
    """
       Directs user to log-in page.
   """
    try:
        response = await user_authentication.login(request)
        return response
    except Exception as e:
        print("Failure on Login-Page ", e)

@app.post("/logout")
async def logout(request: Request):
    """
       Clears all session data for an user when user logs out.
       Redirects to default page upon logout.
   """
    try:
        response = await user_authentication.logout(request)
        return response
    except Exception as e:
        print("Failure on Logout-Page ", e)


@app.post("/validate-login")
async def validate_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
       Validates log-in credentials when user attempts to log in. On attempting to log in, queries mongoDB
       collection to verify if username exists. If yes, fetches username and corresponding password.
       Matches the password and username with the data in the 'Accounts' collection in mongoDB.
       Upon successful validation, stores user data in session and redirects user to default home page.
       If login unsuccessful, throws an error and stays on log in page.
   """
    try:
        response = await user_authentication.validate_login(request, username, password)
        return response
    except Exception as e:
        print("Failure on Validate-Login-Page ", e)


@app.post("/submit-form")
async def validate_signup(request: Request, first_name: str = Form(...), last_name: str = Form(...),
                          username: str = Form(...), password: str = Form(...), email: str = Form(...),
                          contact: str = Form(...), address: str = Form(...), unit_suite: str = Form(...),
                          zip_code: str = Form(...)):
    """
       Takes all inputs obtained from the sign-up form on attempting to submit.
       Inserts data into 'Accounts' collection on mongoDB. Stores password in encrypted format.
       Saves data in session. Redirects user to default home page.
   """
    try:
        response = await user_authentication.validate_signup(request, first_name, last_name, username, password, email,
                                                         contact, address, unit_suite, zip_code)
        return response
    except Exception as e:
        print("Failure on Validate-Signup-Page ", e)


@app.post("/get-restaurants")
async def get_restaurants(request: Request):
    """
       Fetches user-firstname from session data. Takes a restaurant name/ zip/ address location string from the
       search bar and returns list of restaurants from 'Restaurants' collection in mongoDB for that specific location.
   """
    try:
        response = await restaurant_orders.get_restaurants(request)
        return response
    except Exception as e:
        print("Failure on Get-Restaurants-Page ", e)


@app.post('/get-menu')
async def get_menu(request: Request, restaurant_id: int = Form(...)):
    """
       Fetches the list of menu items from the 'Menu' collection in mongoDB against the requested restaurant id.
       Groups the menu items by category attribute.
   """
    try:
        response = await restaurant_orders.get_menu(request, restaurant_id)
        return response
    except Exception as e:
        print("Failure on Get-Menu-Page ", e)

@app.post("/add-to-cart")
async def add_to_cart(request: Request, restaurant_id: int = Form(...), restaurant_name: str = Form(...),
                      item_name: str = Form(...), item_price: str = Form(...)):
    """
       Adds the requested item to cart on clicking the 'Add' button on UI.
       Inserts the item into 'Food-Cart' collection on mongoDB.
       Re-clicking 'Add' button against previously added item, increases quantity by 1 and updates the quantity
       against the same item in the 'Food-Cart' collection in mongoDB.
   """
    try:
        response = await restaurant_orders.add_to_cart(request, restaurant_id, restaurant_name, item_name, item_price)
        return response
    except Exception as e:
        print("Failure on Add-To-Cart-Page ", e)


@app.post("/get-cart-items")
async def get_cart_items(request: Request, restaurant_id: int = Form(...)):
    """
       Fetches cart items from 'Food-Cart' collection in mongoDB against the requested restaurant id.
       Displays cart items on menu page when user adds item to cart.
   """
    try:
        response = await restaurant_orders.get_cart_items(request, restaurant_id)
        return response
    except Exception as e:
        print("Failure on Get-Cart-Items-Functionality ", e)


@app.post("/calculate-checkout-amount")
async def calculate_checkout_amount(request: Request, restaurant_id: int = Form(...)):
    """
       Calculates total checkout amount for all items added to cart for a specific restaurant id.
       The total amount is displayed on the menu page.
   """
    try:
        response = await restaurant_orders.calculate_checkout_amount(request, restaurant_id)
        return response
    except Exception as e:
        print("Failure on Calculate-Checkout-Amount-Functionality ", e)


@app.post("/delete-from-cart")
async def delete_from_cart(request: Request, item_id: str = Form(...)):
    """
       Functionality to delete an item from cart on clicking the 'delete icon' on UI.
       Removes the item from 'Food-Cart' collection in mongoDB.
   """
    try:
        response = await restaurant_orders.delete_from_cart(request, item_id)
        return response
    except Exception as e:
        print("Failure on Delete-From-Cart-Functionality ", e)


@app.post("/decrease-item-quantity-cart")
async def reduce_item_quantity_cart(request: Request, item_id: str = Form(...)):
    """
       Functionality to decrease item quantity by 1 if quantity > 1 on clicking 'minus icon' on UI.
       If quantity == 1, deletes item from cart.
       Updates are made in 'Food-Cart' collection on mongoDB.
   """
    try:
        response = await restaurant_orders.reduce_item_quantity_cart(request, item_id)
        return response
    except Exception as e:
        print("Failure on Reduce-Item-From-Cart-Functionality ", e)


@app.post("/increase-item-quantity-cart")
async def increase_item_quantity_cart(request: Request, item_id: str = Form(...)):
    """
       Functionality to increase item quantity by 1 on clicking the 'plus icon' on UI.
       Updates are made in 'Food-Cart' collection on mongoDB.
   """
    try:
        response = await restaurant_orders.increase_item_quantity_cart(request, item_id)
        return response
    except Exception as e:
        print("Failure on Increase-Item-From-Cart-Functionality ", e)

@app.post("/order-checkout")
async def order_checkout(request: Request, restaurant_id: int = Form(...), restaurant_name: str = Form(...)):
    """
       Directs user to order checkout page on clicking 'Checkout' button on menu page.
       Fetches stored session data for logged in user and autofills input fields on place-order page.
       Displays the details of the items to checkout along with price and quantity.
       Displays fields to enter personal details, address and payment details.
   """
    try:
        response = await restaurant_orders.order_checkout(request, restaurant_id, restaurant_name)
        return response
    except Exception as e:
        print("Failure on Order-Checkout-Page ", e)


@app.post("/place-order")
async def place_order(request: Request, restaurant_id: int = Form(...), restaurant_name: str = Form(...),
                      first_name: str = Form(...), last_name: str = Form(...), email: EmailStr = Form(...),
                      contact: str = Form(...), address: str = Form(...), unit_suite: str = Form(...),
                      zip_code: str = Form(...), card_number: str = Form(...), exp_month: str = Form(...),
                      exp_year: str = Form(...), cvc: str = Form(...), total_amount: float = Form(...)):
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
    try:
        response = await restaurant_orders.place_order(request, restaurant_id, restaurant_name, first_name, last_name,
                                                       email, contact, address, unit_suite, zip_code, card_number,
                                                       exp_month, exp_year, cvc, total_amount)
        return response
    except Exception as e:
        print("Failure on Place-Order-Page ", e)



@app.get("/view-my-orders")
async def get_my_orders(request: Request):
    """
       Directs user to my-orders page to view all orders placed by logged in user.
       Fetches the order details from the 'Orders' collection in mongoDB against the user email.
       Fetches 'restaurant_name' using 'restaurant_id' attribute in 'Orders' collection ('Orders' collection does not
       store 'restaurant_name' to remove data redundancy in database.)
       Formats 'timestamp' value (eg: 2023-11-26T18:54:49.000+00:00 is formatted to display 2023-11-26 on the UI).
   """
    try:
        response = await restaurant_orders.get_my_orders(request)
        return response
    except Exception as e:
        print("Failure on Get-My-Orders_page ", e)


@app.post("/make_reservation")
async def make_reservation(request: Request, restaurant_id: int = Form(...)):
    """
        Functionality that allows users to make reservations. Allows users to reverse restaurant tables for next day.
        First fetches all the reservations for a given restaurant. Then fetches restaurant capacity.
        For every reservation, mongoDB increments the dict value corresponding to slot key with the 'no of guests' value.
        Further checks to see if the dict value corresponding to slot key < max capacity of restaurant.
        If yes, then displays that slot on dropdown and is available to reserve.
   """
    try:
        response = await reservations.make_reservation(request, restaurant_id)
        return response
    except Exception as e:
        print("Failure on Make-Reservation-Page ", e)


@app.post("/save-reservation-data")
async def save_reservation_data(request: Request):
    """
        Save reservation form data into mongoDB 'Reservation' collection.
        Uses Twilio API to send text messages on customer contact to confirm reservation.
   """
    try:
        response = await reservations.save_reservation_data(request)
        return response
    except Exception as e:
        print("Failure on Save-Reservation-Functionality ", e)


@app.get("/show-reservations")
async def show_reservations(request: Request):
    """
        Fetches all reservations made by logged in user. Displays only upcoming reservations
        i.e displays only those reservations that have 'reservation_date' in mongoDB < today's date.
        Fetches restaurant_name from 'Restaurant' collection using 'id' attribute since 'Reservations' collection does
        not store restaurant name to maintain database independency.
   """
    try:
        response = await reservations.show_reservations(request)
        return response
    except Exception as e:
        print("Failure on Show-Reservations-Functionality ", e)



@app.post("/cancel-reservation")
async def cancel_reservation(request: Request, reservation_id: str = Form(...)):
    """
        Fetches the reservation_id of the reservation that needs to be cancelled.
        Removes the reservation from mongoDB.
   """
    try:
        response = await reservations.cancel_reservation(request, reservation_id)
        return response
    except Exception as e:
        print("Failure on Cancel-Reservations-Functionality ", e)



if __name__ == "__main__":
    print("To run this application, open terminal and run command 'uvicorn app:app --reload'.")




