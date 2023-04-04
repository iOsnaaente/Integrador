import hashlib
import pickle
import hmac

import struct 
UNIQUE_CODE = struct.pack( 'ff', 12.05, 19.99 )

class Dummy:
    import json 
    def __init__( self, whatever : json = json.dumps('') ):
        self.we = whatever
    def __str__(self) -> str:
        print('Dammy class for examples')
obj = Dummy()


def encode_object( obj : object, separator : str = '\n' ) -> bytes: 
    data = pickle.dumps( obj )
    digest = hmac.new( UNIQUE_CODE, data, hashlib.blake2b ).hexdigest()
    return digest.encode() + separator.encode() + data


data = encode_object( obj )
with open('temp.txt', 'wb') as output:
    output.write( data )
# ---------------------------------------------------------------------#
with open('temp.txt', 'rb') as file:
    digest = file.readline()[:-1]
    data = file.readline()

def check_recv( digest : bytes, data : bytes, __debug : bool = False ) -> object:
    import secrets
    expected_digest = hmac.new( UNIQUE_CODE, data, hashlib.blake2b ).hexdigest()
    if not secrets.compare_digest( digest, expected_digest.encode() ):
        if __debug: 
            print('Invalid signature')
        return False 
    else: 
        if __debug:
            print( 'Right signatures')
        return pickle.loads( data )


data = check_recv( digest, data, True)
data.__str__() 
