import manage_imports


from manage_imports import *



async def default_page(request: Request):
    """
       The default start up page. Fetches username from session data and displays username if user has logged in.
       Else, displays log in and sign up buttons.
   """
    try:
        user = request.session['user']
        first_name = user.get("first_name")
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
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=303)


async def validate_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
       Validates log-in credentials when user attempts to log in. On attempting to log in, queries mongoDB
       collection to verify if username exists. If yes, fetches username and corresponding password.
       Matches the password and username with the data in the 'Accounts' collection in mongoDB.
       Upon successful validation, stores user data in session and redirects user to default home page.
       If login unsuccessful, throws an error and stays on log in page.
   """
    # validate data against basemodel.
    user = UserLogin(
        username=username,
        password=password
    )
    user = collection_account_info.find_one({"username": username})
    if user and pwd_context.verify(password, user['password']):
        user_data = {
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "email": user['email'],
            "contact": user['contact'],
            "address": user['address'],
            "unit_suite": user['unit_suite'],
            "zip_code": user['zip_code']
        }
        request.session['user'] = user_data

        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "service_name": "FlavorFusion",
                                                     "action": "Log in", "error": "Invalid login credentials!"})



async def validate_signup(request: Request, first_name: str = Form(...), last_name: str = Form(...),
                          username: str = Form(...), password: str = Form(...), email: str = Form(...),
                          contact: str = Form(...), address: str = Form(...), unit_suite: str = Form(...),
                          zip_code: str = Form(...)):
    """
       Takes all inputs obtained from the sign-up form on attempting to submit.
       Inserts data into 'Accounts' collection on mongoDB. Stores password in encrypted format.
       Saves data in session. Redirects user to default home page.
   """
    print("==------ ", username, password, type(username), type(password))
    # validate data against basemodel
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=password,
        email=email,
        contact=contact,
        address=address,
        unit_suite=unit_suite,
        zip_code=zip_code
    )
    encrypted_password = pwd_context.hash(password)

    collection_account_info.insert_one({"first_name": first_name, "last_name": last_name, "username": username,
                                         "password": encrypted_password, "email": email, "contact": contact, "address": address,
                                         "unit_suite": unit_suite, "zip_code": zip_code})
    # create a dictionary for each user to store user related data in session.
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "contact": contact,
        "address": address,
        "unit_suite": unit_suite,
        "zip_code": zip_code
    }
    request.session['user'] = user_data
    # request.session['first_name'] = first_name

    return RedirectResponse(url="/", status_code=303)

