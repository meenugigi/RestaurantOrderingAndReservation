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
    response = await user_authentication.default_page(request)
    return response


@app.post("/sign-up")
async def signup(request: Request):
    """
       Directs user to sign-up page.
   """
    response = await user_authentication.signup(request)
    return response

@app.post("/login")
async def login(request: Request):
    """
       Directs user to log-in page.
   """
    response = await user_authentication.login(request)
    return response

@app.post("/logout")
async def logout(request: Request):
    """
       Clears all session data for an user when user logs out.
       Redirects to default page upon logout.
   """
    response = await user_authentication.logout(request)
    return response


@app.post("/validate-login")
async def validate_login(request: Request):
    """
       Validates log-in credentials when user attempts to log in.
       Upon successful validation, stores user data in session and redirects user to default home page.
       If login unsuccessful, throws an error and stays on log in page.
   """
    response = await user_authentication.validate_login(request)
    return response


@app.post("/submit-form")
async def validate_signup(request: Request):
    """
       Takes all inputs obtained from the sign-up form on attempting to submit.
       Inserts data into 'Accounts' collection on mongoDB. Stores password in encrypted format.
       Saves data in session. Redirects user to default home page.
   """
    response = await user_authentication.validate_signup(request)
    return response


@app.post("/get-restaurants")
async def get_restaurants(request: Request):
    """
       Fetches user-firstname from session data. Takes a restaurant name/ zip/ address location string from the
       search bar and returns list of restaurants from 'Restaurants' collection in mongoDB for that specific location.
   """
    response = await restaurant_orders.get_restaurants(request)
    return response


@app.post('/get-menu')
async def get_menu(request: Request):
    """
       Fetches the list of menu items from the 'Menu' collection in mongoDB against the requested restaurant id.
       Groups the menu items by category attribute.
   """
    response = await restaurant_orders.get_menu(request)
    return response

@app.post("/add-to-cart")
async def add_to_cart(request: Request):
    """
       Adds the requested item to cart on clicking the 'Add' button on UI.
       Inserts the item into 'Food-Cart' collection on mongoDB.
       Re-clicking 'Add' button against previously added item, increases quantity by 1 and updates the quantity
       against the same item in the 'Food-Cart' collection in mongoDB.
   """
    response = await restaurant_orders.add_to_cart(request)
    return response


@app.post("/get-cart-items")
async def get_cart_items(request: Request):
    """
       Fetches cart items from 'Food-Cart' collection in mongoDB against the requested restaurant id.
       Displays cart items on menu page when user adds item to cart.
   """
    response = await restaurant_orders.get_cart_items(request)
    return response


@app.post("/calculate-checkout-amount")
async def calculate_checkout_amount(request: Request):
    """
       Calculates total checkout amount for all items added to cart for a specific restaurant id.
       The total amount is displayed on the menu page.
   """
    response = await restaurant_orders.calculate_checkout_amount(request)
    return response


@app.post("/delete-from-cart")
async def delete_from_cart(request: Request):
    """
       Functionality to delete an item from cart on clicking the 'delete icon' on UI.
       Removes the item from 'Food-Cart' collection in mongoDB.
   """
    response = await restaurant_orders.delete_from_cart(request)
    return response


@app.post("/decrease-item-quantity-cart")
async def reduce_item_quantity_cart(request: Request):
    """
       Functionality to decrease item quantity by 1 if quantity > 1 on clicking 'minus icon' on UI.
       If quantity == 1, deletes item from cart.
       Updates are made in 'Food-Cart' collection on mongoDB.
   """
    response = await restaurant_orders.reduce_item_quantity_cart(request)
    return response


@app.post("/increase-item-quantity-cart")
async def increase_item_quantity_cart(request: Request):
    """
       Functionality to increase item quantity by 1 on clicking the 'plus icon' on UI.
       Updates are made in 'Food-Cart' collection on mongoDB.
   """
    response = await restaurant_orders.get_cart_items(increase_item_quantity_cart)
    return response


@app.post("/order-checkout")
async def order_checkout(request: Request):
    """
       Directs user to order checkout page on clicking 'Checkout' button on menu page.
       Fetches stored session data for logged in user and autofills input fields on place-order page.
       Displays the details of the items to checkout along with price and quantity.
       Displays fields to enter personal details, address and payment details.
   """
    response = await restaurant_orders.order_checkout(request)
    return response


@app.post("/place-order")
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
    response = await restaurant_orders.place_order(request)
    return response




@app.get("/view-my-orders")
async def get_my_orders(request: Request):
    """
       Directs user to my-orders page to view all orders placed by logged in user.
       Fetches the order details from the 'Orders' collection in mongoDB against the user email.
       Fetches 'restaurant_name' using 'restaurant_id' attribute in 'Orders' collection ('Orders' collection does not
       store 'restaurant_name' to remove data redundancy in database.)
       Formats 'timestamp' value (eg: 2023-11-26T18:54:49.000+00:00 is formatted to display 2023-11-26 on the UI).
   """
    response = await restaurant_orders.get_my_orders(request)
    return response




@app.post("/make_reservation")
async def make_reservation(request: Request):
    response = await reservations.make_reservation(request)
    return response


@app.post("/save-reservation-data")
async def save_reservation_data(request: Request):
    response = await reservations.save_reservation_data(request)
    return response


@app.get("/show-reservations")
async def show_reservations(request: Request):
    response = await reservations.show_reservations(request)
    return response



@app.post("/cancel-reservation")
async def cancel_reservation(request: Request):
    response = await reservations.cancel_reservation(request)
    return response





if __name__ == "__main__":
    # Code here will be executed only when this script is run directly
    print("Executing...")




