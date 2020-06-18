import json
import boto3
import base64

from app.settings import REGION, KMS_KEY_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from app.utils.logger import logger

class KMS():
    def __init__(self):
        self.session = boto3.session.Session()
        self.key_id  = KMS_KEY_ID
        self.secret_manager_client = self.session.client(
            service_name="secretsmanager",
            region_name=REGION, 
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )


    def create_secret(self, name, data, id):
        try:
            self.secret_manager_client.create_secret(
                Name=name, 
                SecretString=json.dumps(
                    {
                        'keys': data,
                        'owner': id
                    }
                )
            )
        except Exception as e:
            logger(str(e))
            raise e
        
    def get_secret(self, key):
        return self.secret_manager_client.get_secret_value(SecretId=key)

            
        
if __name__ == '__main__':
    kms = KMS()
    kms.encrypt('Text to encrypt')

