import manage_imports
from manage_imports import *



async def default_page(request: Request):
    """
       The default start up page. Fetches username from session data and displays username if user has logged in.
       Else, displays log in and sign up buttons.
   """
    try:
        first_name = request.session.get("first_name")
        return templates.TemplateResponse("index.html", {"request": request,
                                                         "service_name": "FlavorFusion", "first_name": first_name})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request,
                                                    "service_name": "FlavorFusion"})




async def signup(request: Request):
    """
       Directs user to sign-up page.
   """
    return templates.TemplateResponse("signup.html", {"request": request, "service_name": "FlavorFusion",
                                                      "action": "Sign up"})


async def login(request: Request):
    """
       Directs user to log-in page.
   """
    return templates.TemplateResponse("login.html", {"request": request, "service_name": "FlavorFusion",
                                             "action": "Log in"})


async def logout(request: Request):
    """
       Clears all session data for an user when user logs out.
       Redirects to default page upon logout.
   """
    request.session.pop("first_name", None)
    request.session.pop("last_name", None)
    request.session.pop("email", None)
    request.session.pop("contact", None)
    return RedirectResponse(url="/", status_code=303)


async def validate_login(request: Request):
    """
       Validates log-in credentials when user attempts to log in.
       Upon successful validation, stores user data in session and redirects user to default home page.
       If login unsuccessful, throws an error and stays on log in page.
   """
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")

    user = collection_account_info.find_one({"username": username})
    if user and pwd_context.verify(password, user['password']):
        request.session['first_name'] = user['first_name']
        request.session['last_name'] = user['last_name']
        request.session['email'] = user['email']
        request.session['contact'] = user['contact']
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "service_name": "FlavorFusion",
                                                     "action": "Log in", "error": "Invalid login credentials!"})



async def validate_signup(request: Request):
    """
       Takes all inputs obtained from the sign-up form on attempting to submit.
       Inserts data into 'Accounts' collection on mongoDB. Stores password in encrypted format.
       Saves data in session. Redirects user to default home page.
   """
    form_data = await request.form()
    first_name = form_data.get("first_name")
    last_name = form_data.get("last_name")
    username = form_data.get("username")
    password = form_data.get("password")
    email = form_data.get("email")
    contact = form_data.get("contact")
    address = form_data.get("address")
    unit_suite = form_data.get("unit_suite")
    zip_code = form_data.get("zip_code")
    encrypted_password = pwd_context.hash(password)

    collection_account_info.insert_one({"first_name": first_name, "last_name": last_name, "username": username,
                                         "password": encrypted_password, "email": email, "contact": contact, "address": address,
                                         "unit_suite": unit_suite, "zip_code": zip_code})
    request.session['first_name'] = first_name
    request.session['last_name'] = last_name
    request.session['email'] = email
    request.session['contact'] = contact
    return RedirectResponse(url="/", status_code=303)

