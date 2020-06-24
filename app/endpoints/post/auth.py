import json
import requests
import jwt
import time

from app.utils.validations import create_user_schema, login_user_schema, logout_schema, reset_password_schema
from app.db.main import DB
from app.modules.crypto import Crypto
from app.modules.kms import KMS
from app.modules.validate_google_token import validate_token
from app.modules.validate_facebook_token import validate_fb_token
from app.modules.validate_twitter_token import validate_twitter_token
from app.modules.generate_jwt import generate_jwt
from app.settings import JWT_SECRET
from app.utils.logger import logger

from app.modules.ksm import create_ksm_keys

db = DB()
cp  = Crypto()
kms = KMS()


def create_user(req, new_user=None):
    """Description:
    Creates a new user using email or social credentials
    """
    data = json.load(req)
    
    def handle_keys(new_user):
        # Generate keypairs
        data    = {}

        ksm_keys = create_ksm_keys()
        # Build kms secret data
        data['ksm'] = { 'public_key': ksm_keys['public_key'], 'private_key': ksm_keys['private_key'], 'account_id': ksm_keys['account_id'], 'SS58_address': ksm_keys['SS58_address'], 'phrase': ksm_keys['phrase'] }

        # Generate kms key reference
        name = cp.generate_random_key()

        # Encrypt and store in AWS Secret Manager
        try:
            kms.create_secret(name, data, new_user)
        except Exception as e:
            
            return json.dumps({'error': str(e)})                
        
        # Insert new kms_key and user balance into database
        try:
            print("inserting key")
            pk_data = {'user_id': int(new_user), 'kms_key': name }
            db.insert_kms_key(pk_data)
        
        except Exception as e:
            
            return json.dumps({'error': str(e)})
    
    # Validate request payload
    try:
        create_user_schema(data)        
    except Exception as e:
        return json.dumps({'error': 'Invalid request', 'message': str(e)})
    
    # Handle request types
    try:
        # Handle email request
        if data['type'] == 'email':
            
            # Insert user
            try:
                new_user = db.insert_user(data)
            except Exception as e:
                
                return json.dumps({'error': str(e)})
                
            # Generate keypairs
            handle_keys(new_user)
            
            # If everything is ok return the success response                
            return json.dumps({
                'status': 'success',
                'code': 200,
                'new_user_id': new_user
            })       
        
        # Handle google request
        if data['type'] == 'google':
            
            token = data['token']
            
            try:
                validation = validate_token(token, data['platform'])
                if validation['email'] == data['email']:                    
                    # Insert user
                    try:
                        new_user = db.insert_user(data)
                    except Exception as e:
                        
                        return json.dumps({'error': str(e)})
                    
                    # Generate keypairs
                    handle_keys(new_user)

                    
                    # If everything is ok return the success response
                    return json.dumps({
                        'status': 'success',
                        'code': 200,
                        'new_user_id': new_user
                    })
                
                else:
                    return json.dumps({'error': 'Wrong email'})
            except Exception as e:
                print(e)
                return json.dumps({'error': str(e)})
            
        # Handle facebook request
        if data['type'] == 'facebook':
            token = data['token']
            
            try:
                validation = validate_fb_token(token)
                if validation['user_id'] == data['userFBID']:
                    # Insert user
                    try:
                        new_user = db.insert_user(data)
                    except Exception as e:
                        
                        return json.dumps({'error': str(e)})
                    
                    # Generate keypairs
                    handle_keys(new_user)
                   
                    
                    # If everything is ok return the success response
                    return json.dumps({
                        'status': 'success',
                        'code': 200,
                        'new_user_id': new_user
                    })
                else:
                    return json.dumps({'error': 'Invalid facebook token'})

            except Exception as e:
                return json.dumps({'error': str(e)})
            
        # Handle twitter request
        if data['type'] == 'twitter':
            token        = data['token']
            secret_token = data['tw_token_secret']
            
            try:
               
                validation = validate_twitter_token(token, secret_token)
                if data['userTWID'] == validation.id_str:
                    # Insert user
                    try:
                        new_user = db.insert_user(data)
                    except Exception as e:
                        
                        return json.dumps({'error': str(e)})
                    
                    # Generate keypairs
                    handle_keys(new_user)                   
                    
                    # If everything is ok return the success response
                    return json.dumps({
                        'status': 'success',
                        'code': 200,
                        'new_user_id': new_user
                    })
                else:
                    return json.dumps({'error': 'Invalid twitter token'})
            
            except Exception as e:
                        
                return json.dumps({'error': str(e)})   
                
    except Exception as e:
        return json.dumps({'error': 'Database error', 'message': str(e)})
        
def login(req):
    """Description:
    Authenticates a user with email or social credentials
    """
    data = json.load(req)
    
    # Validate request payload
    try:
        login_user_schema(data)        
    except Exception as e:
        
     
        return json.dumps({'error': 'Invalid request', 'message': str(e)})
    
    # Validate that there are no active sessions for the given user
    current_session = None
    if 'email' in data:
        current_session = db.validate_existing_session(data['email'])
    else:
        current_session = db.validate_existing_session_with_name(data['name'])

    # Handle email request
    if data['type'] == 'email':
        try:
            user = db.login_user_with_email(data)
            return json.dumps({'user': user[0], 'is_auth': True})
        except Exception as e:
            
            
            return json.dumps({'authentication_error': 'There was an error during authentication'})
        
    # Handle google request
    if data['type'] == 'google':
        
        token = data['token']
                
        try:
            validation = validate_token(token, data['platform'])       
            if validation['email'] == data['email']:                    
                user = db.login_user_with_social_credentials(data)
                return json.dumps({'user': user[0], 'is_auth': True})
            else:
                return json.dumps({'error': 'invalid token for given user'})
             
        except Exception as e:
            
            
            return json.dumps({'error': 'Wrong credentials', 'message': str(e)})
            
            
    # Handle facebook request
    if data['type'] == 'facebook':
        
        token = data['token']
        
        try:
            validation = validate_fb_token(token)       
            if validation['user_id'] == data['userFBID']:                    
                user = db.login_user_with_social_credentials(data)
                return json.dumps({'user': user[0], 'is_auth': True})
            else:
                return json.dumps({'error': 'invalid token for given user'})
             
        except Exception as e:
            
            
            return json.dumps({'error': 'Wrong credentials'})
        
    # Handle twitter request
    if data['type'] == 'twitter':

        token        = data['token']
        secret_token = data['tw_token_secret']
        
        try:
            
            validation = validate_twitter_token(token, secret_token)     
            print(validation)
            if data['userTWID'] == validation.id_str:                    
                user = db.login_user_with_social_credentials(data)
                return json.dumps({'user': user[0], 'is_auth': True})
            else:
                return json.dumps({'error': 'invalid token for given user'})
             
        except Exception as e:
            return json.dumps({'error': 'Wrong credentials', 'error': str(e)})
                 
def logout(req):
    data = json.load(req)
    
    try:
    
        logout_schema(data)
    
    except Exception as e:
        
        
        return json.dumps({'error': str(e)})        
    
    try:
    
        db.log_out(data['email'])
    
    except Exception as e:
        
        
        return json.dumps({'error': str(e)})
    
    return json.dumps({'session': None})         
         
def get_token(req):
    data = json.load(req)
    
    # Check if user exists
    check_result = db.verify_user(data['email'])

    if not check_result['exists']:
        return json.dumps({
            'message': 'User does not exists',
            'error': True,
            'code': 401
        })
    else:
        
        # Expiration to 10min.
        unix_ts = int(time.time())
        exp = unix_ts + 60 * 10
        
        # Set the token data
        token_data = {
            'exp': exp,
            'email': data['email'],
            'type': 'password_recovery'
        }
        
        # Generate token
        jwt = generate_jwt(token_data, JWT_SECRET)
        
        # Insert token into database
        db.insert_token(data['email'], jwt)

        return json.dumps({
            'jwt': jwt, 
            'message': 'success', 
            'error': False, 
            'code': 200
        })
        
def reset_password(req, decoded=None):
    data = json.load(req)    
    
    # Validate request payload
    try:
        reset_password_schema(data)        
    except Exception as e:
        
        
        return json.dumps({
            'message': str(e), 
            'error': True,
            'code': 500
        })
    
    # Decode token
    try:        
        decoded = jwt.decode(
            data['token'], 
            str(JWT_SECRET), 
            algorithms=['HS256']
        )
        
        # Verify token integrity
        verify = db.verify_token(data['token'])

        if verify['exists'] and decoded['email'] == verify['email']:
            try:
                # Reset password
                db.set_password(decoded['email'], data['password'])       

                return json.dumps({
                    'message': 'Password update success',
                    'error': False,
                    'code': 200
                })
            except Exception as e:
                return json.dumps({
                    'message': str(e),
                    'error': True,
                    'code': 500
            })
        else:
            return json.dumps({
                'message': 'Incorrect token audience',
                'error': True,
                'code': 401
            })
    except Exception as e:
                
        return json.dumps({
            'message': str(e),
            'error': True,
            'code': 401
        })
    