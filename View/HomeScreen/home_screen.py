from kivymd_extensions.akivymd.uix.progresswidget import AKCircularProgress 
from kivymd.app import MDApp 

from View.Widgets.Graphs.graph_all_day import AzimuteAllDay, ZeniteAllDay 
from View.Widgets.Serial.serial_conf import SerialConfiguration 
from View.Widgets.Graphs.graph_area import Zenite, Azimute 
from View.Widgets.SideBar.side_bar import SideBar 
from View.MapScreen.map_screen import MapView
from View.base_screen import BaseScreenView


import os 
PATH = os.path.dirname( __file__ )
IMAGES = PATH.removesuffix('\\View\\HomeScreen') + '/assets/images/'


class HomeScreenView( BaseScreenView ):

    serial_configuration : SerialConfiguration 
    azimute_graph : Azimute 
    zenite_graph : Zenite 
    map_view : MapView 
    side_bar : SideBar

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_kv_post(self, *args):
        # self.ids.background_image.source = IMAGES + '/panel.png'
        self.side_bar = SideBar( model = self.model ) 
        self.serial_configuration = SerialConfiguration() 
        self.map_view = MapView( 
                            lat = -29.71332542661317, 
                            lon = -53.71766381408064,
                            zoom = 20,  
                            pos_hint = {'center_x': 0.50, 'center_y': 0.5 } 
                        ) 
        self.zenite_graph = Zenite() 
        self.azimute_graph = Azimute() 

        self.ids.box_content.add_widget     ( self.side_bar             )
        self.ids.system_content.add_widget  ( self.serial_configuration )
        self.ids.map_content.add_widget     ( self.map_view             )
        self.ids.azimute_content.add_widget ( self.azimute_graph        ) 
        self.ids.zenite_content.add_widget  ( self.zenite_graph         ) 
        
        return super().on_kv_post(*args)

    # Gambiarra para puxar o nome de usuário e level de acesso
    def on_enter( self, *args ):
        self.side_bar = SideBar( model = self.model ) 
        self.ids.box_content.add_widget( self.side_bar )
        return super().on_enter() 

    @property 
    def username( self ): 
        return self.model.shared_data.username 
    @property 
    def last_access( self ): 
        return self.model.shared_data.last_access 
    @property 
    def level_access( self ): 
        return self.model.shared_data.level_access 
    