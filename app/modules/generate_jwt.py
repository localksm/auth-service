import jwt
import json
from app.settings import JWT_SECRET

def generate_jwt(payload, password):
    try:
        encoded_jwt = jwt.encode(payload, str(JWT_SECRET), algorithm='HS256').decode('utf-8')

    
        return encoded_jwt
    
    except Exception as e:
        raise e
