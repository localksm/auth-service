import json
import requests

from app.settings import KSM_SERVICE_URL

def create_ksm_keys():
    try:        
        res = requests.get(KSM_SERVICE_URL + "/generate-keys")
        obj = json.loads(res.text)
        return obj
    except Exception as e:
        raise e