from View.commom_components.SideBar.side_bar import SideBar 
from View.base_screen import BaseScreenView
from kivy.graphics import *

from kivy.properties import ObjectProperty
from kivy.clock import Clock

from View.commom_components.Serial.serial_conf import SerialConfiguration 
from View.commom_components.Graphs.graph_area import Azimute, Zenite 

class SerialScreenView(BaseScreenView):

    Serial  = ObjectProperty()
    Azimute = ObjectProperty()
    Zenite = ObjectProperty() 

    serial = ObjectProperty() 

    already_draw = False 


    def __init__(self, **kw):
        super().__init__(**kw)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter (self, *args):    
        if not self.already_draw:
            self.Azimute =  Azimute(
                                size_hint = [0.3, 1],
                                pos_hint = {'center_x': 0.5,'top': 1 },
                                md_bg_color = [0.5, 0.5, 0.5, 1 ]
                            )
            self.Zenite =   Zenite(
                                size_hint = [0.3, 1],
                                pos_hint = {'center_x': 0.5,'top': 1 },
                                md_bg_color = [0.5, 0.5, 0.5, 1 ]
                            )
            self.Serial = SerialConfiguration()
            self.serial.add_widget( self.Serial )

            Clock.schedule_interval( self.Azimute.update_graph, 0.1 )
            Clock.schedule_interval( self.Zenite.update_graph, 0.1 )
            
            self.side_bar = SideBar( model = self.model ) 
            
            self.ids.float_content.add_widget    ( self.side_bar )
            self.ids.serial_and_graphs.add_widget( self.Azimute  )
            self.ids.serial_and_graphs.add_widget( self.Zenite   )

            self.already_draw = True 
        return super().on_enter(*args)