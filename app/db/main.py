import time
import json
import jwt
import sqlalchemy
import requests
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime, timedelta

from app.settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT, POSTGRES_HOST, JWT_SECRET, NETWORK_URL
from app.modules.generate_jwt import generate_jwt
from app.modules.kms import KMS
from app.db.statements import insert_user_with_email, insert_user_with_social_credentials

class DB(object):
    
    def __init__(self):

        self.engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')
        self.kms = KMS()
    
    def insert_user(self, user):
        
        with self.engine.connect() as con:
            
            if user['type'] == 'email':
        
                return con.execute(                
                    insert_user_with_email.bindparams(
                        name     = user['name'], 
                        email    = user['email'],
                        password = user['password'],
                        type     = user['type'],
                        status   = user['status']
                    )
                ).scalar()
            else:
                
                return con.execute(                
                    insert_user_with_social_credentials.bindparams(
                        name     = user['name'], 
                        email    = user['email'],
                        type     = user['type'],
                        status   = user['status']
                    )
                ).scalar()
        
    def __authenticate_user(self, email, password):
        try:
            with self.engine.connect() as con:
                auth_statement = text(f"""
                    SELECT id, email, name, kms_key 
                    FROM auth.users_view u 
                    WHERE email='{email}' 
                    AND crypt('{password}', u."password") = u."password";
                """)
                
                social_auth_statement = text(f"""
                    SELECT id, email, name, kms_key 
                    FROM auth.users_view u WHERE email='{email}';
                """)

                auth_result = con.execute(auth_statement if password is not None else social_auth_statement)
                data = []
                user_keys = {}
                for row in auth_result:
                    
                    user_keys = self.kms.get_secret(row[3])
                    user_keys = json.loads(user_keys['SecretString'])
                    
                    data.append({
                        'id': row[0],
                        'email': row[1],
                        'name': row[2],
                        'kms_key': row[3],
                        'issued_at': int(time.time()),
                    })

                user_id = data[0]['id']

                con.close()
                return data
        except Exception as e:
            raise e
    
    def login_user_with_email(self, user):
        data = self.__authenticate_user(user['email'], user['password'])        
        data[0]['exp']   = int(time.time() + 60 * 60)            
        data[0]['token'] = str(generate_jwt(data[0], JWT_SECRET))
            
        # Remove unwanted data from response
        del data[0]['exp']
        del data[0]['kms_key']
        del data[0]['issued_at']
        
        self.__set_login(data[0]['token'], user['email'])        
        
        return data
        
        
    def login_user_with_social_credentials(self, user):
        data = self.__authenticate_user(user['email'], None)        
        data[0]['exp']   = int(time.time() + 60 * 60)            
        data[0]['token'] = str(generate_jwt(data[0], JWT_SECRET))
            
        # Remove unwanted data from response
        del data[0]['exp']
        del data[0]['kms_key']
        del data[0]['issued_at']
        
        self.__set_login(data[0]['token'], user['email'])        
        
        return data
        
        
    def __set_login(self, token, email):
        
        with self.engine.connect() as con:
            statement = text(f"""
                    UPDATE auth.users 
                    SET 
                        token = '{token}',
                        is_logged = TRUE,
                        last_login = NOW()
                    WHERE email = '{email}';                 
            """)
            con.execute(statement)
            
            con.close()
            
    def log_out(self, email):
        with self.engine.connect() as con:
            try:
                statement = text(f"""
                        UPDATE auth.users 
                        SET 
                            token = NULL,
                            is_logged = FALSE
                        WHERE email = '{email}';                 
                """)
                
                con.execute(statement)
                
                con.close()
            except Exception as e:
                raise e
            
    # JWT AND SECURITY     
    def validate_existing_session(self, email):
        with self.engine.connect() as con:
            try:
                statement = text(
                    f"""
                        SELECT token FROM auth.users WHERE email='{email}';
                    """
                )
                
                resultproxy = con.execute(statement)
                token = None
                
                for rowproxy in resultproxy:
                    token = rowproxy[0]
                
                con.close()
                #return {'token': token, 'expired': False}
                try:
                    if token is not None and token != '':
                        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                        
                    
                    return {'token': token, 'expired': False}
                    
                except jwt.ExpiredSignatureError:
                    # Signature has expired
                    return {'token': token, 'expired': True}
                
                
            except Exception as e:
                raise e
        
        
    def verify_token(self, token):
        with self.engine.connect() as con:
            try:
                statement = text(f"""
                    SELECT 
                        email,
                        token,
                        exists(select 1 FROM auth.users WHERE token = '{token}')
                    FROM auth.users
                    WHERE token = '{token}';
                """)
                
                resultproxy = con.execute(statement)
                result = {}
                
                for rowproxy in resultproxy:
                    result['email'] = rowproxy[0]
                    result['token']  = rowproxy[1]
                    result['exists'] = rowproxy[2]
                
                con.close()
                
                return result
            except Exception as e:
                raise e
            
    def verify_user(self, email):
        with self.engine.connect() as con:
            try:
                statement = text(f"""
                    SELECT EXISTS (SELECT * FROM auth.users WHERE email='{email}');
                """)
                
                result_proxy = con.execute(statement)
                result = {}
                
                for row in result_proxy:
                    result['exists'] = row[0]
                    
                con.close()
                
                return result
            except Exception as e:
                raise e
 
    def insert_token(self, email, token):
        with self.engine.connect() as con:
            try:
                statement = text(
                    f"""
                        UPDATE auth.users
                            SET token='{token}'
                        WHERE email='{email}';
                    """
                )
                
                result_proxy = con.execute(statement)
                
                con.close()
                
                return json.dumps({
                    'message' : 'success',
                    'error': False,
                    'code'    : 200
                })
                
            except Exception as e:
                return json.dumps({
                    'message' : e,
                    'error': True,
                    'code'    : 500
                })
    
    # Set password
    def set_password(self, email, password):
        with self.engine.connect() as con:
            try:
                statement = text(
                    f"""
                        UPDATE auth.users
                            SET password=crypt('{password}', gen_salt('md5')),
                            token=NULL
                        WHERE email='{email}';
                    """
                )
                
                result_proxy = con.execute(statement)
                
                con.close()
                
                return json.dumps({
                    'message' : 'success',
                    'error': False,
                    'code'    : 200
                })
                
            except Exception as e:
                 return json.dumps({
                    'message' : str(e),
                    'error': True,
                    'code'    : 500
                })
    
    def insert_Kusama_public_key(self, data):
        with self.engine.connect() as con:
            try:
                statement = text(f"""
                    INSERT INTO kms.keys (
                        user_id,
                        kms_key    
                    ) VALUES (
                      {data['user_id']},  
                      '{data['kms_key']}'  
                    ) RETURNING id;              
                """)
                res = con.execute(statement).scalar()
                con.close()
                return res
            except Exception as e:
                return json.dumps({'error': str(e)})
            
    def insert_lumens_balance(self, data):
        with self.engine.connect() as con:
            try:
                statement = text(f"""
                    INSERT INTO platform.user_balances (
                        user_id,
                        lumens
                    ) VALUES (
                        {data['user_id']},
                        {data['balance']}
                    ) RETURNING id;
                """)
                res = con.execute(statement).scalar()
                con.close()
                return res
            except Exception as e:
                return json.dumps({'error': str(e)}) 
            
    def insert_busd_balance(self, data):
        with self.engine.connect() as con:
            try:
                statement = text(f"""
                    INSERT INTO platform.user_balances (
                        user_id,
                        busd
                    ) VALUES (
                        {data['user_id']},
                        {data['balance']}
                    ) RETURNING id;
                """)
                res = con.execute(statement).scalar()
                con.close()
                return res
            except Exception as e:
                return json.dumps({'error': str(e)})            