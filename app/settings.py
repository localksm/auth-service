# settings.py
import os

from dotenv import load_dotenv
from pathlib import Path  # python3 only

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# CORE
JWT_SECRET             = os.getenv('JWT_SECRET')

# DB
POSTGRES_USER          = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD      = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB            = os.getenv('POSTGRES_DB')
POSTGRES_PORT          = os.getenv('POSTGRES_PORT')
POSTGRES_HOST          = os.getenv('POSTGRES_HOST')

# SOCIAL
FB_CLIENT_ID           = os.getenv('FB_CLIENT_ID')
FB_CLIENT_SECRET       = os.getenv('FB_CLIENT_SECRET')

TW_CONSUMER_KEY        = os.getenv('TW_CONSUMER_KEY')
TW_CONSUMER_SECRET     = os.getenv('TW_CONSUMER_SECRET')

GOOGLE_IOS_ID          = os.getenv('GOOGLE_IOS_ID')
GOOGLE_ANDROID_ID      = os.getenv('GOOGLE_ANDROID_ID')

# BLOCKCHAIN
FUNDING_LUMENS_AMOUNT  = os.getenv('FUNDING_LUMENS_AMOUNT')
FUNDING_ACCOUNT_SECRET = os.getenv('FUNDING_ACCOUNT_SECRET')
FUNDING_ACCOUNT_PK     = os.getenv('FUNDING_ACCOUNT_PK')
NETWORK_URL            = os.getenv('NETWORK_URL')

BINANCE_SERVICE_URL    = os.getenv('BINANCE_SERVICE_URL')
CELO_SERVICE_URL       = os.getenv('CELO_SERVICE_URL')

CELO_FUNDING_KEY       = os.getenv('CELO_FUNDING_KEY')

# AWS
REGION                 = os.getenv('REGION')
KMS_KEY_ID             = os.getenv('KMS_KEY_ID')
AWS_ACCESS_KEY_ID      = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY  = os.getenv('AWS_SECRET_ACCESS_KEY')

# MAILING
MAILING_SERVICE_URL    = os.getenv('MAILING_SERVICE_URL')

# SERVICES KEYS
GET_RESET_PASSWORD_TOKEN_KEY = os.getenv('GET_RESET_PASSWORD_TOKEN_KEY')