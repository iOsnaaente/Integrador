from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard
from kivy.clock import Clock

from Model.db.database import Database 

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

    __db = Database()

    def on_kv_post(self, base_widget):
        Clock.tick()
        self.comport_menu = MDDropdownMenu(
            caller = self.comport_icon,
            items = [ 
                {
                    "text": f"COM{i}",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x = f"COM{i}": self.select_comport( x ),
                } for i in range(25) 
            ],
            width_mult = 4
        )
        self.baudrate_menu = MDDropdownMenu(
            caller = self.baudrate_icon,
            items = [ 
                {
                    "text": i,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x = i : self.select_baudrate( x ),
                } for i in ['9600', '19200', '57600', '115200']
            ],
            width_mult = 4
        )
        self.timeout_menu = MDDropdownMenu(
            caller = self.timeout_icon,
            items = [ 
                {
                    "text": i,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x = i : self.select_timeout( x ),
                } for i in [ '0.001', '0.1', '1', '10', 'None' ]
            ],
            width_mult = 4
        )
        Clock.schedule_once( self.do_bind )
        return super().on_kv_post(base_widget)

    def do_bind(self, *args):
        self.comport_icon.bind( on_release = self.open_comport_menu )
        self.baudrate_icon.bind( on_release = self.open_baudrate_menu )
        self.timeout_icon.bind( on_release = self.open_timeout_menu )
        self.connection_button.bind( on_release = self.connect )
        self.refresh.bind( on_release = self.att_comport )
        
        _, state, comp, baud, time = self.__db.serial[0]
        self.comport_label.text = '    ' + comp 
        self.baudrate_label.text = '    ' + baud 
        self.timeout_label.text = '    ' + time 
        if state == 'T':
            self.connection_keep.active = True
        else: 
            self.connection_keep.active = False 

    
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
        print( 'Att comports ')

    def connect( self, con = None ): 
        comp = self.comport_label.text.replace('    ', '')
        baud = self.baudrate_label.text.replace('    ', '')
        time = self.timeout_label.text.replace('    ', '')
        if self.connection_keep.active == True:
            self.__db.set_serial( 'T', comp, baud, time )
            print( comp, baud, time, 'check True' )
            
        else:
            print( comp, baud, time, 'check False' )
        print( 'Implementar a conexão serial em Views/commom_components/serial_conf')