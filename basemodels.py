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


class OrderDetails(RestaurantID):
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
