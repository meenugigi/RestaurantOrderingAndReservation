from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.security import APIKeyCookie
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import stripe
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from datetime import datetime, timedelta
import asyncio
from fastapi import Form
import basemodels
from basemodels import *

from twilio.rest import Client

from env import *

# for payment using stripe api
stripe.api_key = STRIPE_API_KEY
# for storing session data for user login and logout
cookie_key = COOKIE_KEY  # Replace with your secret key
security = APIKeyCookie(name="session", auto_error=False)
SECRET_KEY = SESSION_SECRET_KEY
twilio_acoount_sid = TWILIO_ACCOUNT_SID
twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_phone_number = TWILIO_PHONE_NUMBER


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Password hashing helper using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client = Client(twilio_acoount_sid, twilio_auth_token)

# MongoDB connection URL
MONGODB_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGODB_URL)
database = client['RestaurantOrderingAndReservation']
collection_restaurant = database['Restaurant']
collection_menu = database['Menu']
collection_food_cart = database['Food-Cart']
collection_orders = database['Orders']
collection_account_info = database['Accounts']
collection_reservations = database['Reservations']

