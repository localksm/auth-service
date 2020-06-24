import json
import twitter

from app.settings import TW_CONSUMER_KEY, TW_CONSUMER_SECRET

def validate_twitter_token(token, token_secret, credentials=None):
    
    oauth_consumer_key     = TW_CONSUMER_KEY
    oauth_consumer_secret  = TW_CONSUMER_SECRET  
    
    try:
        
        api = twitter.Api(consumer_key=oauth_consumer_key,
                    consumer_secret=oauth_consumer_secret,
                    access_token_key=token,
                    access_token_secret=token_secret)
        
        credentials = api.VerifyCredentials()

    except Exception as e:
        
        return json.dumps({'error': 'invalid twitter credentials', 'error':str(e)})
        
    return credentials

