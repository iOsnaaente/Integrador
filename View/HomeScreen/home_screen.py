from kivymd_extensions.akivymd.uix.progresswidget import AKCircularProgress 
from kivymd.app import MDApp 

from View.commom_components.Graphs.graph_all_day import AzimuteAllDay, ZeniteAllDay 
from View.commom_components.Serial.serial_conf import SerialConfiguration 
from View.commom_components.Graphs.graph_area import Zenite, Azimute 
from View.commom_components.SideBar.side_bar import SideBar 

from View.base_screen import BaseScreenView


import os 
PATH = os.path.dirname( __file__ )
IMAGES = PATH.removesuffix('\\View\\HomeScreen') + '/assets/images/'


class HomeScreenView( BaseScreenView ):

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self, *args):
        self.ids.box_content.add_widget( SideBar( model = self.model ) ) 
        self.ids.background_image.source = IMAGES + '/panel.png'

        return super().on_enter(*args)

    @property 
    def username( self ): 
        return self.model.shared_data.username 
    @property 
    def last_access( self ): 
        return self.model.shared_data.last_access 
    @property 
    def level_access( self ): 
        return self.model.shared_data.level_access 
    