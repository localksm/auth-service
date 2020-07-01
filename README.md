# Air-Auth

## Scope:
This service is intended to manage the users for Air Protocol's applications, this would handle user signup, user login and application authentication through API keys and secrets.

## Signup Flow
Users can signup using their email and password or using social credentials (Google, Facebook or Twitter). 

## Email/Password
The user is able to input a valid email and a password (8 character lenght as min) to register into our application, the password is ecnrypted on sigunup. When the user log in into the app they must do that using their email and password (the same used in the registration process).

## Social
The auth service uses the information retrieved from the third party platform to verify the user actually exists and then creates the user in the auth database. We do not keep the token returned from the social platform since the tokens returned from the social platforms are not in the same format. Due to that format differences we generate jwt's, by doing this we are able to use our own format for all our users regardless of the method they used to register.

## The actual flow
**What actually happens when a user register into the application?**
When a user register using email and password the process is pretty straightforward, the application sends to the auth service the email and password and we create the new user (notice the email field is marked as `UNIQUE`) in the database. When the user choose to use social credentials we need to validate the token sent by the third party platform and then create the user with the token information. We do not store tokens from third party platforms.

Once the user is created, we need to create a Kusama account. The client application sends a single request and the auth service handles the whole process.

So after the signup flow is the following:
1. Auth service receives the client application request and creates a new user into `auth.users`
2. The service generates a new Kusama keypairs for the new user and creates the account in the network for the user. 
3. The new created secret is encrypted and stored into `AWS Secret Manager`.
4. We store the `public_key` into `kms.kusama` along with the `user_id` in order to identify later the `public_key` to retrieve the `secret` from `AWS Secret Manager`.

## Key Secret Management
As we create a keypair for new registered users we must:
- 1 Encrypt the secret
- 2 Store the secret using AWS KMS service
- 3 Since we need to retrieve the secret to sign transactions then we will need to save the public key and the `secret_name` (`public_key`) into the auth database.

# Technical Docs
## Getting started
### To get started (Unix systems):
- 1. Clone this repo
- 2. Create a python virtual environment with Python 3.6.5, you can do so with `virtualenv`. To install virtualenv you can use `pip install virtualenv`, once you have created your `virtualenv` now you can create a new `virtualenv` with the followign commands:
    - `virtualenv -p python3 venv` <-- This will create a new `venv` directory in the root of the project
- 3. Activate your new virtualenv with: `source venv/bin/activate`. If everything is fine now you can proceed to install the project dependencies.
- 4. Install project dependencies: `pip install -r requirements.txt`
- 5. That's it! now you can run: `sh run.sh database` and then `sh run.sh server` (If you want to run the app on docker then run `sh run.sh deploy_to_docker`)
- 6. Profit!

## Usage
**Endpoints:**
- `http://localhost:5000/api/v1/auth/create_user`: This endpoint is in charge of creating new users for our platform. You can consume it by sending a `POST`  request as following:

**For email users**:
```javascript
{
    "email": "example@catalyst.com.mx",
    "name": "Bruce Wayne",
    "password": "1234567890",
    "type": "email"
}
```

**For google users**:
```javascript
{
    "email": "example@gmail.com",
    "name": "John Wick",
    "token": "<google token sent by client>",
    "type": "google"
}
```

**For facebook users**:
```javascript
{
    "email": "test@gmail.com",
    "name": "John Wick",
    "token": "<facebook token>",
    "type": "facebook",
    "userFBID": "<facebook user id>"
}
```

**For twitter users**:
```javascript
{
    "email": "testing_twitter@gmail.com",
    "name": "John Wick",
    "token": "<twitter authToken>",
    "tw_token_secret": "<twitter authTokenSecret>",
    "userTWID": "<tiwtter userID>",
    "type": "twitter"
}
```

- `http://localhost:5000/api/v1/auth/login`: This endpoint is in charge of authenticating users in our system, they can be authenticated with email and password or social credentials.

**For email users**:
```javascript
{
    "email": "example@catalyst.com.mx",
    "password": "1234567890",
    "type": "email"
}
```
**For google users**:
```javascript
{
    "email": "l.arr.cerv@gmail.com",
    "token": "<google token sent by client>",
    "type": "google"
}
```

**For facebook users**:
```javascript
{
    "email": "test@gmail.com",
    "token": "<facebook token>",
    "userFBID": "<facebook userID>",
    "type": "facebook"
}
```

**For twitter users**:
```javascript
{
    "email": "testing_twitter@gmail.com",
    "token": "<twitter authToken>",
    "tw_token_secret": "<twitter authTokenSecret>",
    "userTWID": "<tiwtter userID>",
    "type": "twitter"
}
```
- `http://localhost:5000/api/v1/auth/logout`: As the name says, logout the current user (Requires header Authorization containing user jwt)
```javascript
{
    "email": "example@catalyst.com.mx"
}
```

- `http://localhost:5000/api/v1/auth/verify_token`: Verifies the given token and return the data related to token
```javascript
{
    "token": "<jwt>"
}
```

## Development
This project uses and abstraction pattern in order to make easier the scallbility of the project, so the project structure is like following:

```.
├── __pycache__
│   ├── app.cpython-36.pyc
│   └── app.cpython-37.pyc
├── db
│   └── main.py
├── endpoints
│   ├── get
│   │   └── __init__.py
│   └── post
│       └── auth.py
├── modules
│   ├── generate_jwt.py
│   └── validate_google_token.py
├── social
├── utils
│   └── validations.py
├── __init__.py
└── app.py
```

### The API pattern
The main file of the project is `app/app.py` this file should not be touched regularly unless we need to add new features to the core of the API such as an auth middleware.

The `app.py` file contains a main class called `ProcessResource`, this class has to methods `on_get` and `on_post` (there should be another one called `on_patch`).

Each of this methods is in charge of handling `GET` and `POST`requests by implementing dynamic imports. As you can see in our project strucutre we have an `endpoints` directory and inside we have the directories `get` and `post`, is in this directories where we are going to add our new endpoints depending on what we need. 

The name of the file will be the first part of the endpoint, for example in our `post` direcotry we have the file `auth.py` this would mean that our endpoint would have the first path as `/api/v1/auth/...` and then inside the script we define our methods, for example `create_user` then our API will interpret this as `/api/v1/auth/create_user` and so on.

With that brief explanation the way to add new endpoints to our API is to create a new file inside the corresponding directory (get or post) and then add a new method on that file. You also can use the existing scripts and just add new mehotds if they are in the same context, for example if you are adding a method for password recovery this should be added at: `endpoints/post/auth.py`.

In order to keep our endpoints as clean as posible we are going to handle the core functionallity of our endpoints in the `modules` directory, there we are going to add all the core functionallity of the app such as validating tokens, generating new ones or any other process or feature we need with exception of database transactions which are handled in our `db/main.py` script.
