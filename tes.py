from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.app import MDApp

from kivy.lang import Builder
from kivy.clock import Clock

KV = '''
<DropdownSerial@MDCard>:
    icon_button: icon_button 
    label_button: label_button 

    orientation: 'horizontal'
    md_bg_color: app.theme_cls.primary_color

    MDFlatButton:
        id: label_button
        size_hint: 0.8, 1
        md_bg_color: [0,0,0,0] 
        halign: 'center'
        text: "Comport"
        pos_hint: {"center_x": .5, "center_y": .5}
    MDIconButton:
        id: icon_button
        icon:'chevron-down'
        size_hint: 0.2, 1
        pos_hint: {'center_x': 0.50,'center_y': 0.50}
        on_release: root.menu.open()

MDScreen:
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: 10 
        DropdownSerial:
            size_hint: 0.3, 0.8
            md_bg_color: 'gray'
            pos_hint: {'center_x': 0.50,'center_y': 0.50 }
     
'''

class DropdownSerial( MDCard ):
    icon_button = ObjectProperty() 
    label_button = ObjectProperty() 
    menu_items = ListProperty() 
    menu = ObjectProperty() 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_items = [{
                "text": f"Item {i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Item {i}": self.select_item(x),
            } for i in range(10)
        ]
        self.menu = MDDropdownMenu(
            items=self.menu_items,
            width_mult=4,
        )
        Clock.schedule_once( self.do_bind, 0.1 )
    
    def do_bind( self, ce ): 
        self.icon_button.bind( on_release = self.open_menu)

    def open_menu(self, *args):
        self.menu.caller = self.icon_button
        self.menu.open()

    def select_item(self, text_item):
        self.label_button.text = text_item
        self.menu.dismiss() 
        print(text_item)
        



class Test(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
    def build(self):
        return self.screen
Test().run()