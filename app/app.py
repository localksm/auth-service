# main.py

#!/usr/bin/env python3
import json, sys, os, re
import time
import base64
import importlib
import logging
import jwt


import falcon
from falcon import HTTPStatus

from urllib.parse import urlparse

from app.settings import JWT_SECRET, GET_RESET_PASSWORD_TOKEN_KEY
from app.db.main import DB

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')
        
        
        
class AuthMiddleware(object):

    def process_request(self, req, resp):
        path = req.path.split("/v1/")
        
        open_paths = [
            'auth/login',
            'auth/create_user',
            'auth/verify_token',
            'auth/reset_password'   
            'auth/logout'   
        ]

        if path[1] == 'auth/get_token':
            key = req.get_header('Authorization')
            print(key)
            if key == GET_RESET_PASSWORD_TOKEN_KEY:
                return
            else:
                raise falcon.HTTPUnauthorized({'error': 'invalid authorization key'})

        if path[1] in open_paths:
            return 
        
        token = req.get_header('Authorization')
        challenges = ['Token type="Fernet"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges)

        if not self._token_is_valid(token):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges)

    def _token_is_valid(self, token):
        
        db = DB()
        current_time = time.time()
        decoded = jwt.decode(token, str(JWT_SECRET), algorithms=['HS256'])

        # Check for token expriation
        if int(current_time) > decoded['exp']: 
            
            return json.dumps({'error': 'token expired'})
        
        # Check for token in db
        verify = db.verify_token(token)
        
        if verify['exists'] and verify['token'] == token:
            return True
        else:
            return  json.dumps({'error': 'invalid token'})   
        
        


""" Process the GET requests
"""
class ProcessResource(object):
    def on_get(self, req, res, endpoint, method):
        
        # Add endpoints path
        sys.path.insert(0, f'{os.getcwd()}/app/endpoints/get')

        # Import request module
        mod = None
        f = None

        try:
            mod = importlib.import_module(endpoint)
        except Exception as e:
            logging.error(e)
            res.status = falcon.HTTP_400
            res.content_type = 'application/json'
            res.body = json.dumps({ 'message': 'Module not found', 'code': 400 })
        
        try:
            if mod is not None:
                
                try:
                    f = getattr(mod, str(method))
                
                except Exception as e:
                    logging.error(e)
                    res.status = falcon.HTTP_400
                    res.content_type = 'application/json'
                    res.body = json.dumps({ 'message': 'Method not found', 'code': 400 })
                
                if f is not None:
                    res.status = falcon.HTTP_200
                    res.content_type = 'application/json'
                    params = urlparse(req.url)
                    res.body = (f(params))
        
        except ValueError as e:
            logging.error(e)
            res.status = falcon.HTTP_500
            res.body = 'Internal server error'

    def on_post(self, req, res, endpoint, method):
        
        # Add endpoints path
        sys.path.insert(0, f'{os.getcwd()}/app/endpoints/post')

        # Import request endpoint
        mod = None
        f = None
        
        try:
            mod = importlib.import_module(endpoint)
        except Exception as e:
            logging.error(e)
            res.status = falcon.HTTP_404
            res.content_type = 'application/json'
            res.body = json.dumps({ 'message': 'Module not found', 'code': 404 })
        
        try:
            if mod is not None:
        
                try:
                    f = getattr(mod, str(method))
        
                except Exception as e:
                    res.status = falcon.HTTP_404
                    res.content_type = 'application/json'
                    res.body = json.dumps({ 'message': 'Method not found', 'code': 404 })
        
                if f is not None:
                    res.status = falcon.HTTP_200
                    res.content_type = 'application/json'
                    res.body = (f(req.stream))
        
        except ValueError as e:
            logging.error(e)
            res.status = falcon.HTTP_500
            res.body = 'Internal server error'
 


# Create the Falcon application object
app = falcon.API(middleware=[HandleCORS(), AuthMiddleware()])

# Instantiate the ProcessResource class
get_resource = ProcessResource()

# Routes
app.add_route('/api/v1/{endpoint}/{method}', get_resource)