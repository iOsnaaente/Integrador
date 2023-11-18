from View.Widgets.SideBar.side_bar import SideBar 
from View.base_screen import BaseScreenView
from kivy.graphics import *

from View.Widgets.Serial.serial_conf import SerialConfiguration 
from libs.kivy_garden.graph import SmoothLinePlot

from kivy.properties import ObjectProperty
from kivy.clock import Clock

import math 

class SerialScreenView(BaseScreenView):

    side_bar : SideBar

    Serial  = ObjectProperty()
    
    Azimute = ObjectProperty()
    azimute_motor = None 
    azimute_sensor = None 

    Zenite = ObjectProperty() 
    zenite_motor = None 
    zenite_sensor = None 

    already_draw = False 
    
    MAX_POINTS_GRAPH_CANVAS = 1000  
    _x = [0]

    def __init__(self, **kw):
        super().__init__(**kw)


    def on_kv_post(self, base_widget):
        # Side bar 
        self.side_bar = SideBar( model = self.model ) 
        self.ids.float_content.add_widget   ( self.side_bar )
        
        # Serial configuration 
        self.Serial = SerialConfiguration()
        self.ids.serial.add_widget          ( self.Serial   )
        
        # Zenite
        self.zenite_motor = SmoothLinePlot(color=[ 0, 0, 1, 1 ])
        self.zenite_sensor = SmoothLinePlot(color=[ 1, 0, 0, 1 ])
        self.ids.zenith_graph.add_plot( self.zenite_motor )
        self.ids.zenith_graph.add_plot( self.zenite_sensor )
        
        # Azimute 
        self.azimute_motor = SmoothLinePlot(color=[ 0, 0, 1, 1 ])
        self.azimute_sensor = SmoothLinePlot(color=[ 1, 0, 0, 1 ])
        self.ids.azimuth_graph.add_plot( self.azimute_motor )
        self.ids.azimuth_graph.add_plot( self.azimute_sensor )

        #Clock.schedule_interval( self.render, 0.1 )
        BaseScreenView.on_kv_post(self, base_widget)
    

    # Callback para entrar na tela
    def on_enter(self, *args):
        # Coloca o side bar no lugar 
        self.side_bar = SideBar( model = self.model) 
        self.ids.float_content.add_widget( self.side_bar )
        BaseScreenView.on_enter(self, *args)
    
    # Callback qundo sair da tela
    def on_leave( self, *args ):
        self.ids.float_content.remove_widget( self.side_bar )
        BaseScreenView.on_leave(self, *args)


    def render( self, clk_event ):
        self._x.append( self._x[-1] + clk_event )
        self.ids.zenith_graph.xmin  = math.ceil( self._x[ 0 ] )
        self.ids.zenith_graph.xmax  = math.ceil( self._x[-1 ] )
        self.ids.azimuth_graph.xmin = math.ceil( self._x[ 0 ] )
        self.ids.azimuth_graph.xmax = math.ceil( self._x[-1 ] )
        if len(self._x) > self.MAX_POINTS_GRAPH_CANVAS: 
            self._x.pop(0)
        self.azimute_motor.points  = [ ( x, 180*math.sin( x / 100.0 ) ) for x in self._x ]
        self.azimute_sensor.points = [ ( x, 180*math.cos( x / 100.0 ) ) for x in self._x ]
        self.zenite_motor.points  = [ ( x, 90*math.cos( x / 10.0 )**2 ) for x in self._x ]
        self.zenite_sensor.points = [ ( x, 90*math.sin( x / 10.0 )**2 ) for x in self._x ]


    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """