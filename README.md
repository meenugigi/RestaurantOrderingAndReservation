# Restaurant Ordering and Reservation Web Application
This project is a Python-based web application built with FastAPI, offering functionalities for restaurant ordering and reservation. It enables users to sign up, log in, search for restaurants, order food items, manage their cart, place orders, and reserve tables at restaurants.

## Dataset used
Uber Eats USA Restaurants and Menus: https://www.kaggle.com/datasets/ahmedshahriarsakib/uber-eats-usa-restaurants-menus/
restaurants.csv 
restaurant-menus.csv

## Functional Requirements

### User Authentication
1. **User Signup, Login, and Authentication:** Users can sign up, log in securely, and authenticate their identity.

### Restaurant Search and Menu Viewing
1. **Search Functionality:** Users can search for restaurants using their name, food item names, or zip codes.
2. **Restaurant Details:** Clicking on a restaurant displays all available menu items categorized by item categories.

### Ordering System
1. **Categorized Menu:** Menu items for each restaurant are categorized based on item categories.
2. **Real-time Cart Management:** Adding items to the cart updates item quantity and checkout amount without page refresh.
3. **Order Placement:** Users can place orders after entering basic information, address, and payment details.
4. **Payment Validation:** Payment validation is integrated to ensure successful and secure transactions.
5. **Order Confirmation:** Orders are placed only if the payment validation is successful.

### Order Tracking
1. **Order History:** Users can view all previously placed orders.
2. **Live Order Status:** Upon placing an order, users can view the live order status (e.g., order placed, order accepted, order processing, on the way, order delivered).

### Table Reservation System
1. **Table Reservations:** Users can reserve tables for restaurants.
2. **Reservation Availability:** Reservations are open only for the next day.
3. **Capacity Management:** Reservations are limited based on the restaurant's maximum capacity.

### Communication and Notifications
1. **Notification System:** Users receive text messages on their phones upon successful table reservations.
2. **Reservation View:** Users can view all upcoming reservations on the 'My Reservations' page.


## Technologies Used
- **Backend:** FastAPI, Python, MongoDB (database)
- **Frontend:** HTML, CSS, JavaScript, Jinja templates
- **AJAX & jQuery:** For seamless and dynamic user experience
- **Payment Integration:** Stripe API for secure payment transactions
- **Communication Integration:** Twilio for text message notifications
