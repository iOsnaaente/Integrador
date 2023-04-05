from kivymd_extensions.akivymd.uix.progresswidget import AKCircularProgress 
from View.base_screen import BaseScreenView

from View.commom_components.SideBar.side_bar import SideBar 


import os 
PATH = os.path.dirname( __file__ )
IMAGES = PATH.removesuffix('\\View\\HomeScreen') + '/images/'



class HomeScreenView( BaseScreenView ):

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self, *args):
        self.ids.box_content.add_widget( SideBar( model = self.model ) ) 
        return super().on_enter(*args)