from View.commom_components.SideBar.side_bar import SideBar 
from View.base_screen import BaseScreenView
from kivy.graphics import *

from kivymd_extensions.akivymd.uix.charts import AKLineChart
from kivymd.uix.card import MDCard

from kivy.lang import Builder 

import os 
PATH = os.path.dirname( __file__ )

class SerialConfiguration( MDCard ):
    ''' Serial Configuration Class '''
    Builder.load_file( PATH + '/serial_conf.kv' )


class SerialScreenView(BaseScreenView):

    already_draw = False 

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter (self, *args):    
        if not self.already_draw:
            self.side_bar = SideBar( model = self.model ) 
            self.ids.float_content.add_widget( self.side_bar  )
            self.already_draw = True 

        return super().on_enter(*args)