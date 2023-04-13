from kivy.clock import Clock
from datetime import datetime 

class SharedData:

    __username : str = ''
    __last_access : str = ''
    __level_access : str = '' 
    __photo : bytearray = b''
    __login_index : int = 0 

    __date : str = '00:00:00 01/01/2001'

    __connected = False 

    def __init__(self):
        Clock.schedule_interval( self.update_date, 1 )
        self.username = ""
        self.email = ""

    def update_date( self, dt ):
        self.datetime =  datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    @property
    def datetime( self ): 
        return self.__date 
    @datetime.setter
    def datetime( self, value : str ):
        self.__date = value 
    @property 
    def time(self):
        return self.__date.split(' ')[0]
    @property
    def date(self):
        return self.__date.split(' ')[1]
    
    @property
    def connected(self):
        return self.__connected

    @property
    def username( self ):
        return self.__username 
    @username.setter
    def username( self, value ): 
        self.__username = value 

    @property
    def last_access( self ):
        return self.__last_access 
    @last_access.setter
    def last_access( self, value ): 
        self.__last_access = value 

    @property
    def level_access( self ):
        return self.__level_access 
    @level_access.setter
    def level_access( self, value ): 
        self.__level_access = value 

    @property
    def photo( self ):
        return self.__photo 
    @photo.setter
    def photo( self, value ): 
        self.__photo = value 
    
    @property
    def login_index( self ):
        return self.__login_index 
    @login_index.setter
    def login_index( self, value ): 
        self.__login_index = value 