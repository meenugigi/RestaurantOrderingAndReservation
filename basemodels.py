from typing import List

from pydantic import BaseModel, SecretStr, EmailStr

class UserLogin(BaseModel):
    username: str
    password: SecretStr


class User(UserLogin):
    first_name: str
    last_name: str
    # username: str
    # password: SecretStr
    email: EmailStr
    contact: str
    address: str
    zip_code: str
    unit_suite: str



class RestaurantID(BaseModel):
    restaurant_id: int

class RestaurantName(BaseModel):
    restaurant_name: str

class OrderDetails(RestaurantID, RestaurantName):
    restaurant_name: str
    first_name: str
    last_name: str
    email: EmailStr
    contact: str
    address: str
    unit_suite: str
    zip_code: str
    card_number: str
    exp_month: str
    exp_year: str
    cvc: str
    total_amount: float


class ItemDetails(RestaurantID, RestaurantName):
    item_name: str
    item_price: str

class ItemId(BaseModel):
    item_id: str

class ReservationID(BaseModel):
    reservation_id: str

class Reservation(RestaurantID):
    full_name: str
    email: EmailStr
    contact: str
    date: str
    no_of_guests: int
    slot_reserved: List[str] = []
    slot_ids: List[str] = []
