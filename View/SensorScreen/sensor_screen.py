from View.Widgets.SideBar.side_bar import SideBar 
from View.base_screen import BaseScreenView
from kivy.graphics import *

class SensorScreenView(BaseScreenView):

    already_draw = False 
    side_bar : SideBar 

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_kv_post (self, *args):    
        self.side_bar = SideBar( model = self.model ) 
        self.ids.float_content.add_widget( self.side_bar  )
        return super().on_enter(*args)