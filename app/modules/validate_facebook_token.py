import json
import requests

from app.settings import FB_CLIENT_ID, FB_CLIENT_SECRET

def validate_fb_token(userToken):
    clientId = FB_CLIENT_ID
    clientSecret = FB_CLIENT_SECRET
    
    appLink = f'https://graph.facebook.com/oauth/access_token?client_id={clientId}&client_secret={clientSecret}&grant_type=client_credentials'
    
    # From appLink, retrieve the second accessToken: app access_token
    appToken = requests.get(appLink).json()['access_token']
    link = 'https://graph.facebook.com/debug_token?input_token=' + userToken + '&access_token=' + appToken
    try:
        user = requests.get(link).json()['data']
    except Exception as error:
        return error
    return user

