import json
import requests

from google.oauth2 import id_token
from google.auth.transport import requests

from app.settings import GOOGLE_ANDROID_ID, GOOGLE_IOS_ID

    
def validate_token(token, platform):
    GOOGLE_CLIENT_ID = GOOGLE_ANDROID_ID if platform == 'android' else GOOGLE_IOS_ID
    request = requests.Request()

    try:
        id_info = id_token.verify_oauth2_token(
            token, 
            request, 
            GOOGLE_CLIENT_ID
        )

        if id_info['iss'] != 'https://accounts.google.com':
            raise ValueError('Wrong issuer.')
        
        return id_info
    except Exception as e:
        raise e
    