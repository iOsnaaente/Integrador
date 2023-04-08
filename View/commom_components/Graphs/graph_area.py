from extensions.kivy_garden.graph import Graph, MeshLinePlot 
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.card import MDCard

from kivy.properties import ObjectProperty 
import math 

MAX_POINTS_GRAPH_CANVAS = 1000

class Azimute( MDCard, HoverBehavior ):
    ''' Azimute Graph Class 
    KV file: graph_area.kv
    ids: [
        title_label
        graph
    ]
    Main widgets: [
        kivy_garden.graph linechart graph 
    ]
    '''
    azimute_motor = None 
    azimute_sensor = None
    graph_x = []
    graph = None 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = Graph(
                    xlabel = 'X', 
                    ylabel = 'Y', 
                    x_ticks_minor = 5,
                    x_ticks_major = 10,
                    y_ticks_major = 0.5,
                    y_grid_label = True,
                    x_grid_label = True ,
                    padding = 5 ,
                    x_grid = True, 
                    y_grid = True, 
                    xmin = -0, 
                    xmax = 100, 
                    ymin = -1*1.1, 
                    ymax = 1*1.1
                )
        
        self.graph_x = [ 0 ]

        self.azimute_motor = MeshLinePlot( color = [1, 0, 0, 1] )
        self.azimute_sensor = MeshLinePlot( color = [1, 0, 0, 1] ) 

        self.graph.add_plot( self.azimute_motor )
        self.graph.add_plot( self.azimute_sensor )

        self.ids.graph.add_widget( self.graph )
        self.update_graph( )

    def update_graph( self, clock_event = 1 ):
        '''print( f'Must update the {self.title} graph')'''
        self.graph_x.append( self.graph_x[-1]+clock_event )
        self.graph.xmin = self.graph_x[ 0 ]
        self.graph.xmax = self.graph_x[-1 ]
        if len(self.graph_x) > MAX_POINTS_GRAPH_CANVAS: 
            self.graph_x.pop(0)
        self.azimute_motor.points  = [ ( x, math.sin( x / 1.0 ) ) for x in self.graph_x ]
        self.azimute_sensor.points = [ ( x, math.cos( x / 1.0 ) ) for x in self.graph_x ]


class Zenite( MDCard ):
    ''' Azimute Graph Class 
    KV file: graph_area.kv
    ids: [
        title_label
        graph
    ]
    Main widgets: [
        kivy_garden.graph linechart graph 
    ]
    '''
    zenite_motor = None 
    zenite_sensor = None
    graph_x = []
    graph = None 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = Graph(
                    xlabel = 'X', 
                    ylabel = 'Y', 
                    x_ticks_minor = 5,
                    x_ticks_major = 10,
                    y_ticks_major = 0.5,
                    y_grid_label = True,
                    x_grid_label = True ,
                    padding = 5 ,
                    x_grid = True, 
                    y_grid = True, 
                    xmin = -0, 
                    xmax = 100, 
                    ymin = -1*1.1, 
                    ymax = 1*1.1
                )
        
        self.graph_x = [ 0 ]

        self.zenite_motor = MeshLinePlot( color = [1, 0, 0, 1] )
        self.zenite_sensor = MeshLinePlot( color = [1, 0, 0, 1] ) 

        self.graph.add_plot( self.zenite_motor )
        self.graph.add_plot( self.zenite_sensor )

        self.ids.graph.add_widget( self.graph )
        self.update_graph( )

    def update_graph( self, clock_event = 1 ):
        '''print( f'Must update the {self.title} graph')'''
        self.graph_x.append( self.graph_x[-1]+clock_event )
        self.graph.xmin = self.graph_x[ 0 ]
        self.graph.xmax = self.graph_x[-1 ]
        if len(self.graph_x) > MAX_POINTS_GRAPH_CANVAS: 
            self.graph_x.pop(0)
        self.zenite_motor.points  = [ ( x, math.sin( x / 10.0 ) ) for x in self.graph_x ]
        self.zenite_sensor.points = [ ( x, math.cos( x / 10.0 ) ) for x in self.graph_x ]
