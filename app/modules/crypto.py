import json
import coincurve
import random


class Crypto:
    def __init__(self):
        pass
    
    def generate_mesh_keys(self):
        pk = coincurve.PrivateKey()
        pub = pk.public_key.format(False).hex()
                
        return {'public_key': pub, 'private_key': pk.to_hex()}
    
    def generate_random_key(slef):
        ran = random.randrange(10**80)
        _hex = "%064x" % ran

        #limit string to 64 characters
        _hex = _hex[:64]
        
        return _hex
    
    