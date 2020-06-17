import json
import requests

from app.settings import CELO_SERVICE_URL, CELO_FUNDING_KEY

def create_celo_account():
    try:        
        res = requests.get(CELO_SERVICE_URL + "/create_account")
        obj = json.loads(res.text)
        return obj
    except Exception as e:
        raise e
    
def fund_wallet(key):
    try:
        payload = {'asset': 'cgld', 'amount':'1', 'sender_kms_key': CELO_FUNDING_KEY, 'receiver_kms_key': key}
        res = requests.post(CELO_SERVICE_URL + "/send", data=payload)    
        print(res.text)
    except Exception as e:
        raise e


