from kivy.clock import Clock

from datetime import datetime 

from System.Tags import * 


class SharedData:
    _username : str = ''
    _last_access : str = ''
    _level_access : str = '' 
    _photo : bytes = b''
    _login_index : int = 0 
    _date : str = '00:00:00 01/01/2001'
    _connected = False

    SYSTEM_TABLE = {
        "INPUT_POS_GIR"       : 0.0,  "INPUT_POS_ELE"       : 0.0,
        "INPUT_AZIMUTE"       : 0.0,  "INPUT_ZENITE"        : 0.0,
        "INPUT_GENERATION" 	  : 0.0,     
        "INPUT_TEMP"          : 0.0,  "INPUT_PRESURE"       : 0.0,
        "INPUT_SENS_CONF_GIR" : 0.0,  "INPUT_SENS_CONF_ELE" : 0.0,
        "INPUT_YEAR"          : 0  ,  "INPUT_MONTH"         : 0  ,  "INPUT_DAY"           : 0  ,
        "INPUT_HOUR"          : 0  ,  "INPUT_MINUTE"        : 0  ,  "INPUT_SECOND"        : 0  ,
        
        "HR_PV_GIR"           : 0.0,  "HR_KP_GIR"           : 0.0,  "HR_KI_GIR"           : 0.0, "HR_KD_GIR"           : 0.0,  
        "HR_AZIMUTE"          : 0.0,  
        "HR_PV_ELE"           : 0.0,  "HR_KP_ELE"           : 0.0,  "HR_KI_ELE"           : 0.0, "HR_KD_ELE"           : 0.0,
        "HR_ALTITUDE"         : 0.0,  "HR_LATITUDE"         : 0.0,  "HR_LONGITUDE"        : 0.0,
        "HR_STATE"            : 0,
        "HR_YEAR"             : 0,    "HR_MONTH"            : 0,  "HR_DAY"                : 0,
        "HR_HOUR"             : 0,    "HR_MINUTE"           : 0,  "HR_SECOND"             : 0,
        
        "DISCRETE_FAIL"       : False,
        "DISCRETE_POWER"      : False,
        "DISCRETE_TIME"       : False,
        "DISCRETE_GPS"        : False,

        "COIL_POWER"          : False, "COIL_LED"            : False,
        "COIL_M_GIR"          : False, "COIL_M_ELE"          : False,
        "COIL_LEDR"           : False, "COIL_LEDG"           : False,   "COIL_LEDB"           : False,
        "COIL_SYNC_DATE"      : False,
    } 

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
    
    @connected.setter
    def connected(self, value : bool ) -> None:
        self._connected = value 

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
