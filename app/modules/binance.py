import json
import requests
import logging

from app.settings import BINANCE_SERVICE_URL

class Binance(object):
    
    def __init__(self):
        self.url = BINANCE_SERVICE_URL
        
    def create_account(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                return response.text
        except Exception as e:
            logging.error(e)
            return json.dumps({'error': str(e)})