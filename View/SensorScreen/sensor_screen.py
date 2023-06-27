from View.Widgets.SideBar.side_bar import SideBar 
from View.base_screen import BaseScreenView
import os

from kivy.clock import Clock

PATH = os.path.dirname( __file__ ).removesuffix('\\View\\SensorScreen') + '/assets/3D'

class SensorScreenView(BaseScreenView):

    already_draw = False 
    side_bar : SideBar

    def __init__(self, **kw):
        super().__init__(**kw)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_kv_post (self, *args):    
        self.side_bar = SideBar( model = self.model ) 
        self.ids.float_content.add_widget( self.side_bar  )

        ids = [ 'label_motor_vertical', 
                'label_encoder_vertical'
                'label_motor_horizontal',
                'label_encoder_horizontal',
                'icon_system_status',
                'label_system_status',
                'icon_geracao',
                'label_geracao',
        ]

        return super().on_enter(*args)

        
