from extensions.kivy_garden.graph import Graph, MeshLinePlot 
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.card import MDCard

from datetime import datetime
import math 

HOVER_ENTER_COLOR = [0.5, 0.5, 0.5, 0.40 ] 
HOVER_LEAVE_COLOR = [0.1, 0.1, 0.1, 0.85 ]

class AzimuteAllDay( MDCard, HoverBehavior ):
    azimute = None 
    graph_x = []
    graph = None 
    hover : bool 

    def __init__(self, hover : bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover = hover 
        self.graph = Graph(
                    xlabel = 'Time [h]', 
                    ylabel = 'Azimute Deg [º]', 
                    x_ticks_minor = 5,
                    x_ticks_major = 30,
                    y_ticks_major = 60,
                    y_grid_label = True,
                    x_grid_label = True ,
                    padding = 5 ,
                    x_grid = True, 
                    y_grid = True,
                )
        
        self.graph_x = [ 0 ]

        self.azimute = MeshLinePlot( color = [1, 0, 0, 1] )
        self.graph.add_plot( self.azimute )
        self.ids.graph.add_widget( self.graph )

    def update_graph( self, x_points : list, y_points : list ):
        x_ticks = [(x_point - x_points[0]).total_seconds() for x_point in x_points]
        self.graph.xmax = x_ticks[-1]
        self.graph.x_ticks_major = (x_ticks[-1] - x_ticks[0]) // 10
        self.graph.x_ticks_minor = self.graph.x_ticks_major // 5
        self.graph.x_labels = {
            x: datetime.fromtimestamp(x_points[0].timestamp() + x).strftime('%H:%M:%S')
            for x in range(int(x_ticks[0]), int(x_ticks[-1]) + 1, int(self.graph.x_ticks_major))
        }
        self.azimute.points = [(x, y ) for x, y in zip(x_ticks, y_points)]
        self.azimute.x_ticks = x_ticks
        self.graph.ymin = 0
        self.graph.ymax = 360
    
    def on_enter(self, *args):
        if self.hover:
            self.md_bg_color = HOVER_ENTER_COLOR
    def on_leave(self, *args):
        if self.hover:
            self.md_bg_color = HOVER_LEAVE_COLOR

class ZeniteAllDay( MDCard, HoverBehavior ):
    zenite = None
    graph_x = []
    graph = None 
    hover : bool 

    def __init__(self, hover : bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover = hover 
        self.graph = Graph(
                    xlabel = 'Time [h]', 
                    ylabel = 'Zenite Deg (º)', 
                    x_ticks_minor = 5,
                    x_ticks_major = 7.5,
                    y_ticks_major = 15,
                    y_grid_label = True,
                    x_grid_label = True ,
                    padding = 5 ,
                    x_grid = True, 
                    y_grid = True,
        )
        self.graph_x = [ 0 ]
        self.zenite = MeshLinePlot( color = [1, 0, 0, 1] )
        self.graph.add_plot( self.zenite )
        self.ids.graph.add_widget( self.graph )

    def update_graph( self, x_points : list, y_points : list ):
        x_ticks = [(x_point - x_points[0]).total_seconds() for x_point in x_points]
        self.graph.xmax = x_ticks[-1]
        self.graph.x_ticks_major = (x_ticks[-1] - x_ticks[0]) // 10
        self.graph.x_ticks_minor = self.graph.x_ticks_major // 5
        self.graph.x_labels = {
            x: datetime.fromtimestamp(x_points[0].timestamp() + x).strftime('%H:%M:%S')
            for x in range(int(x_ticks[0]), int(x_ticks[-1]) + 1, int(self.graph.x_ticks_major))
        }
        self.zenite.points = [(x, y)  for x, y in zip(x_ticks, y_points)]
        self.zenite.x_ticks = x_ticks
        self.graph.ymin = 0
        self.graph.ymax = 95

    def on_enter(self, *args):
        if self.hover:
            self.md_bg_color = HOVER_ENTER_COLOR
    def on_leave(self, *args):
        if self.hover:
            self.md_bg_color = HOVER_LEAVE_COLOR