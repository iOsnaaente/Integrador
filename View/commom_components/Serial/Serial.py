from kivy.properties import ObjectProperty 
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.button import MDFlatButton 

from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem
from kivy.properties import ListProperty
from kivymd.uix.card import MDCard
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown

from kivymd.uix.menu import MDDropdownMenu


class Dropdown(MDCard):

    dropdown = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = DropDown()
        self.main_button = None
        self.create_menu()

    def set_main_button(self, main_button):
        self.main_button = main_button

    def menu_callback(self, text):
        self.main_button.text = text

    def create_menu(self):
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            } for i in range(9600, 19200, 9600)
        ]

        for item in menu_items:
            self.dropdown.add_widget(Builder.template(item['viewclass'])(text=item['text'], on_release=item['on_release']))

    def open(self, caller):
        self.dropdown.open(caller)
        
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
