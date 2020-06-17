import json

from app.modules.kms import KMS
from app.utils.validations import create_secret_schema

kms = KMS()

def create_secret(req):
    data = json.load(req)
    
    # Validate request payload
    try:
        create_secret_schema(data)        
    except Exception as e:
        return json.dumps({'error': 'Invalid request', 'message': str(e)})
    
    kms.create_secret(data)
    
    return json.dumps({'success': 'Secret created'})
    
