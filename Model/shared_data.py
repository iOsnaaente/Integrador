from kivy.clock import Clock
from datetime import datetime 

class SharedData:

    _username : str = ''
    _last_access : str = ''
    _level_access : str = '' 
    _photo : bytes = b''
    _login_index : int = 0 
    _date : str = '00:00:00 01/01/2001'
    _connected = False 

    def __init__(self):
        Clock.schedule_interval( self.update_date, 1 )
        self.username = ""
        self.email = ""

    def update_date( self, dt = None ):
        self.datetime =  datetime.now().strftime("%H:%M:%S %d/%m/%Y")



    @property
    def datetime( self ): 
        return self._date 
    
    @datetime.setter
    def datetime( self, value : str ):
        self._date = value
         
    @property 
    def time(self):
        return self._date.split(' ')[0]
    @property
    def date(self):
        return self._date.split(' ')[1]
    @property
    def connected(self):
        return self._connected
    @property
    def username( self ):
        return self._username 
    @username.setter
    def username( self, value ): 
        self._username = value 
    @property
    def last_access( self ):
        return self._last_access 
    @last_access.setter
    def last_access( self, value ): 
        self._last_access = value 
    @property
    def level_access( self ):
        return self._level_access 
    @level_access.setter
    def level_access( self, value ): 
        self._level_access = value 
    @property
    def photo( self ):
        return self._photo 
    @photo.setter
    def photo( self, value ): 
        self._photo = value 
    @property
    def login_index( self ):
        return self._login_index 
    @login_index.setter
    def login_index( self, value ): 
        self._login_index = value 
