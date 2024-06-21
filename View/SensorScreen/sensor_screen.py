from View.Widgets.SideBar.side_bar import SideBar 
from View.base_screen import BaseScreenView
from kivymd.uix.label import MDLabel 
import os

from kivy.clock import Clock

PATH  = os.path.dirname( __file__ ).removesuffix( os.path.join('View', 'SensorScreen' ) )
PATH += os.path.join( 'assets', '3D' )


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

    
    def on_enter(self, *args):
        # Atualiza as tagas do sistema 
        if self.controller.is_connected():
            for tag in self.controller.get_tags():
                print( tag )
        else: 
            # Retira a Label de sistema não conectado
            pass 

        # Atualiza o side bar 
        self.side_bar = SideBar( model = self.model) 
        self.ids.float_content.add_widget( self.side_bar )
        BaseScreenView.on_enter(self, *args)    


    # Callback quando sair da tela
    def on_leave( self, *args ):
        self.ids.float_content.remove_widget( self.side_bar )
        BaseScreenView.on_leave(self, *args)