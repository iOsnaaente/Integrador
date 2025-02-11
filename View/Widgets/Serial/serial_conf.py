from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.metrics import dp

from Model.db.database import Database 
from kivymd.app import MDApp 
from kivy.clock import Clock 
from kivy.logger import Logger

from Model.system_model import SystemModel
import libs.Serial as serial
import os 

class SerialConfiguration( MDCard ):
    comport_label = ObjectProperty() 
    comport_icon = ObjectProperty()

    baudrate_label = ObjectProperty()  
    baudrate_icon = ObjectProperty()

    timeout_label = ObjectProperty()
    timeout_icon = ObjectProperty() 

    connection_icon = ObjectProperty() 
    connection_label = ObjectProperty() 
    connection_button = ObjectProperty()
    connection_keep = ObjectProperty()
    
    refresh = ObjectProperty() 
    
    comport_menu: MDDropdownMenu 
    baudrate_menu: MDDropdownMenu 
    timeout_menu: MDDropdownMenu 

    __db: Database = Database()
    is_connected: bool = False   
    comport: str = ''

    app: MDApp = MDApp.get_running_app()
    model: SystemModel | None = None 

    def on_kv_post(self, base_widget = None ):
        Clock.tick()
        self.comport_menu = MDDropdownMenu(
            caller = self.comport_icon,
            items = [ 
                {
                    "text": f"COM{i}",
                    "viewclass": "OneLineListItem",
                    "height": dp(40),
                    "on_release": lambda x = f"COM{i}": self.select_comport( x ),
                } for i in range(25) 
            ],
            width_mult = 2
        )
        self.baudrate_menu = MDDropdownMenu(
            caller = self.baudrate_icon,
            items = [ 
                {
                    "text": i,
                    "viewclass": "OneLineListItem",
                    "height": dp(40),
                    "on_release": lambda x = i : self.select_baudrate( x ),
                } for i in ['9600', '19200', '57600', '115200']
            ],
            width_mult = 2
        )
        self.timeout_menu = MDDropdownMenu(
            caller = self.timeout_icon,
            items = [ 
                {
                    "text": i,
                    "viewclass": "OneLineListItem",
                    "height": dp(40),
                    "on_release": lambda x = i : self.select_timeout( x ),
                } for i in [ '0.001', '0.1', '1', '10', 'None' ]
            ],
            width_mult = 2
        )
        Clock.schedule_once( self.do_bind )
        self.render_event = Clock.schedule_interval( self.render, 0.5 )  
        return super().on_kv_post(base_widget)

    def do_bind(self, *args):
        self.model = self.app.system_model 

        self.comport_icon.bind( on_release = self.open_comport_menu )
        self.baudrate_icon.bind( on_release = self.open_baudrate_menu )
        self.timeout_icon.bind( on_release = self.open_timeout_menu )
        self.connection_button.bind( on_release = self.connect )
        self.refresh.bind( on_release = self.att_comport )
        
        _, state, comp, baud, time = self.__db.serial[0]
        self.comport_label.text = '    ' + comp 
        self.baudrate_label.text = '    ' + baud 
        self.timeout_label.text = '    ' + time 
        
        # Pega o status da conexão 
        if isinstance( self.model, SystemModel ):
            self.is_connected = self.model.connected
        else: 
            self.is_connected = False 
        
        # Verifica se a conexão esta ativa  
        if self.is_connected: 
            self.comport = comp 
        else:
            self.comport = ''

        # Verifica o stado do botão de Keep Conected 
        if state == 'T':
            self.connection_keep.active = True
            self.is_connected = True 
        else: 
            self.connection_keep.active = False 
            self.is_connected = False 
    
    def open_comport_menu( self, *args ): 
        self.comport_menu.open()     

    def open_baudrate_menu( self, *args ): 
        self.baudrate_menu.open()   

    def open_timeout_menu( self, *args ): 
        self.timeout_menu.open() 

    def select_comport(self, comport : str):
        self.comport_label.text = '    ' + comport
        self.comport_menu.dismiss() 

    def select_baudrate( self, baudrate : str  ):
        self.baudrate_label.text = '    ' +  baudrate
        self.baudrate_menu.dismiss() 
    
    def select_timeout( self, timeout : str ):
        self.timeout_label.text = '    ' +  timeout
        self.timeout_menu.dismiss() 
    
    def att_comport( self, att = None ): 
        ports = serial.get_serial_ports() 
        if self.is_connected: 
            ports.append( self.comport )
        self.comport_menu = MDDropdownMenu(
            caller = self.comport_icon,
            items = [ 
                {
                    "text": f"{i}",
                    "viewclass": "OneLineListItem",
                    "height": dp(40),
                    "on_release": lambda x = f"{i}": self.select_comport( x ),
                } for i in ports 
            ],
            width_mult = 2
        )
        Logger.debug( 'Att comports ')

    def connect( self, con = None ): 
        comp = self.comport_label.text.replace('    ', '')
        baud = self.baudrate_label.text.replace('    ', '')
        time = self.timeout_label.text.replace('    ', '')
        if self.connection_keep.active == True:
            self.__db.set_serial( 'T', comp, baud, time )
        else:
            Logger.debug( comp, baud, time, 'check False' )    
            pass 
        if self.model != None:  
            self.model.connect_device( 0x12, comp, baud, time ) 
        else:
            Logger.debug( f'Model is None into {os.path.dirname(__file__)}' )
            return False 
    
    
    def render( self, dt = None ):
        if isinstance( self.model, SystemModel ):
            conn =  self.model.is_connected()
        else: 
            conn = False  
        if conn: 
            self.ids.connection_icon.icon_color = [ 0,1,0,0.8] 
            self.ids.connection_label.text = "Serial Connected"
        else:
            self.ids.connection_icon.icon_color = [ 1,0,0,0.8]
            self.ids.connection_label.text = "Serial Disconnected" 