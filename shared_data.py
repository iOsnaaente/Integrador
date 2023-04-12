class SharedData:

    __username : str = ''
    __last_access : str = ''
    __level_access : str = '' 
    __photo : bytearray = b''
    __login_index : int = 0 

    def __init__(self):
        self.username = ""
        self.email = ""

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