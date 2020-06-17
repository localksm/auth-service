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
    
if __name__ == '__main__':
    token = """eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ4ZWZlYTFmNjZlODdiYjM2YzJlYTA5ZDgzNzMzOGJkZDgxMDM1M2IiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI2NjYyODYwNDU1NzYtNWV2NDI4ZW9hYmxmc2xwZzR0NDUxamxoa25tdW5laTcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI2NjYyODYwNDU1NzYtNWV2NDI4ZW9hYmxmc2xwZzR0NDUxamxoa25tdW5laTcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTcyMTk2NjI5ODU3ODE5MjE4NTMiLCJlbWFpbCI6ImwuYXJyLmNlcnZAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJvd0JnWGI5S1lWWmtUSzdrX0VWWjZnIiwibm9uY2UiOiIwS215YWV4RHRUNFhUaW9EOFdwUndCdjJDbDNjZXBCUjV1V2gzdGdXTk04IiwibmFtZSI6Ikx1aXMgQ2VydmFudGVzIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hLS9BQXVFN21DTGVIXzZZcW5tcDJ0bXBELTBLbEs5WGFzc2tQMTBzRW9VX2Ztbj1zOTYtYyIsImdpdmVuX25hbWUiOiJMdWlzIiwiZmFtaWx5X25hbWUiOiJDZXJ2YW50ZXMiLCJsb2NhbGUiOiJlbiIsImlhdCI6MTU4MTYxNDg1MywiZXhwIjoxNTgxNjE4NDUzfQ.oUK-lQT9ox21LA-pUfiNU5zS5poAz_ecX2SXIWGEu8a6TLkw3cAZUukN1k1WuyfiEoT9j-rsdOhDxq4Ofub8EfWTMSbAvh14Lu5NZEKRG97a7s9VbdatlXwy83k1fckxsdh73L8-bV8umbpy-Z6mjB1B2lNIfBmmqeXj89cpkqbK-P7SOsc-4hLuXVHQvMu-mtXuevHNfCrzW7eMO2fAz-QJNLryt-QlYEU4JKFstBVTNp6vtj2B6C-HXIQN2-RujBpzn9X2a_ZLZN7iSv4YjOye714HnbmIZhnjBsI8npGwgN4IPOBayWwxL81JxaawL0NLOmdqcE-JvyMhF6zDYQ"""
    
    validate_token(token)