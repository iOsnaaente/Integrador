from kivy.properties import ObjectProperty 
from kivymd.uix.card import MDCard
from kivy.clock import Clock

class SerialConfiguration( MDCard ):
    comport  = ObjectProperty()
    baudrate = ObjectProperty()
    timeout  = ObjectProperty()

    ''' Serial Configuration Class
        KV file: serial_conf.kv 
        ids: [
            serial_comp_select
            serial_baudrate_select
            serial_timeout_select
            serial_status_connection
        ]
        Main widgets: [
            Dropdown box 
            Refresh button 
            Connection button
            Icon status    
        ]
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once( self.draw, 0.1 )

    def draw(self, clock ):
        ''' Fazer a mágica '''