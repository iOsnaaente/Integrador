from View.commom_components.SideBar.side_bar import SideBar 
from kivymd.uix.floatlayout import MDFloatLayout 
from kivy_garden.mapview import MapMarkerPopup
from kivy_garden.mapview import MapView 
from kivymd.uix.widget import MDWidget 
from kivymd.uix.label import MDLabel 

from View.base_screen import BaseScreenView
from kivy.graphics import *

from kivymd_extensions.akivymd.uix.charts import AKLineChart

#####################################
from libs.Model import SunPosition 
import math 
#####################################



class Ecliptica( MDWidget ):

    SUN_DATA : SunPosition 

    Norte = MDLabel( text = 'N', color = [0,0,1,1], bold = True, font_size = 16, size_hint =  [None, None] )
    Lest  = MDLabel( text = 'L', color = [0,1,0,1], bold = True, font_size = 16, size_hint =  [None, None] )
    Oeste = MDLabel( text = 'O', color = [1,0,0,1], bold = True, font_size = 16, size_hint =  [None, None] )
    
    def __init__(self, sun_data, size, pos, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = size
        self.pos_hint = pos 
        self.SUN_DATA = sun_data
        self.bind( pos  = self.update_canvas )
        self.bind( size = self.update_canvas )

        # self.float_label.add_widget( self.Norte )
        # self.float_label.add_widget( self.Lest  )
        # self.float_label.add_widget( self.Oeste )
        
        self.update_canvas() 

    def update_canvas( self, *args ):
        # Parametros da tela 
        width, height = self.size[0], self.size[1]
        center        = [ width//2, height//2 ]
        r             = width//2 - 20 if width+20 <= height else height//2 - 20
        
        # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
        azi = self.SUN_DATA.get_pos_from_date( self.SUN_DATA.rising )[1]
        alt = self.SUN_DATA.get_pos_from_date( self.SUN_DATA.sunset )[1] # [ alt , azi ]
        
        # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
        dots = self.SUN_DATA.trajetory( 100, all_day = False )
        dots = [ [ x - math.pi/2 ,  y ] for x, y, _ in dots ]
        ndots = [ [ center[0] + math.cos(x)*r, center[1] - math.sin(x)*math.cos(y)*r ] for x, y in dots ]
        dots = []
        for dot in ndots:
            dots.extend( dot )

        # Labels 
        self.Norte.pos = [center[0] - (r + 20), center[1] -10 ]    # Oeste -> pos    = [center[0] - (r + 20), center[1] -10 ]   )  
        self.Lest.pos  = [center[0] + (r +  5), center[1] -10 ]    # Leste -> pos    = [center[0] + (r +  5), center[1] -10 ]   )  
        self.Oeste.pos = [center[0] - 10 , center[1] - (r + 25) ]  # Norte -> pos    = [center[0] - 10 , center[1] - (r + 25) ] ) 
            
        # DESENHO DO SOL NA SUA POSIÇÃO 
        sun = [  self.SUN_DATA.azi - math.pi/2, self.SUN_DATA.alt ] 
        sun = [ center[0] + math.cos(sun[0])*r, center[1] - math.sin(sun[0])*math.cos(sun[1])*r ]
        
        if sun[1] < center[1] - r*math.sin(alt-math.pi/2): 
            sun_color = 'under'
        else: 
            sun_color = 'over'

        # DESENHO ESTÁTICO
        self.canvas.clear() 
        with self.canvas:
            # Horizonte
            Color( 0.5, 0.4, 0.5, 1 )
            Line( pos = self.pos, points = [ center[0] - r, center[1], center[0] + r, center[1] ], width = 1  )
            # Nascente 
            Color( 0.5, 0.5, 0.5, 0.8)
            Line( pos = self.pos, points = [ center[0], center[1], center[0] + r*math.cos(azi-math.pi/2), center[1] - r*math.sin(azi-math.pi/2) ], width = 2  )
            # Poente
            Color( 1, 1, 0, 0.8 )
            Line( pos = self.pos, points = [ center[0], center[1], center[0] + r*math.cos(alt-math.pi/2), center[1] - r*math.sin(alt-math.pi/2) ], width = 2  )
            # Trajetória 
            Color( 1, 1, 0.0, 0.85)
            Line( pos = self.pos, points = dots, width = 2 )
            # Circulos 
            Color( 0.3, 0.3, 0.3, 0.3)
            Line( pos = self.pos, points = self.draw_circle( center = center, radius = r ), width = 2)
            Color( 0.3, 0.3, 0.3, 1 )
            Line( pos = self.pos, points = self.draw_circle( center = center, radius = r ), width = 1)
            # Sun 
            Color( 0.7, 0.7, 0.7, 1)
            Line( pos = self.pos, points = [ center[0], center[1], sun[0], sun[1] ], width = 2 )
            if sun_color == 'over':
                Color( 1, 1, 0.0, 1)
            elif sun_color == 'under':
                Color( 0.7, 0.7, 0.7, 1)
            Line( pos = self.pos, points = self.draw_circle( center = sun, radius = 10, segments = 20 ), width = 10 )
            # Center
            Color( 1, 1, 1, 1)
            Line( pos = self.pos, points = self.draw_circle( center = center, radius = 1 ), width = 3)


    def draw_circle( self, center, radius, segments = 100, closed = True ):
        points = [] 
        drange = 2*math.pi / segments 
        for seg in range( segments + 1 if closed else 0 ): 
            x = center[0] + radius*math.cos( drange*seg )
            y = center[1] + radius*math.sin( drange*seg )
            points.append( x )
            points.append( y )
        return points 


class MapScreenView(BaseScreenView):
    
    map_view : MapView 
    side_bar : SideBar 
    markers = [ 
            MapMarkerPopup( lat=-29.71332542661317, lon=-53.71766381408064 ) 
        ]

    already_draw = False 
    ecliptica : Ecliptica 

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """


    def on_enter (self, *args):    
        if not self.already_draw:
            self.side_bar = SideBar(
                    model = self.model 
                ) 
            self.ecliptica = Ecliptica( 
                    sun_data = self.model.SunData, 
                    size = [1, 1], 
                    pos = {'center_x': 0.5,'center_y': 0.5} 
                ) 
            self.map_view = MapView(size_hint = [0.99, 0.99], 
                    pos_hint = {'center_x': 0.50, 'center_y': 0.5 }, 
                    zoom = 25 , 
                    lon = self.markers[0].lon, 
                    lat = self.markers[0].lat 
                )
            
            # for marker in self.markers:
            #     self.map_view.add_widget( marker )

            self.ids.float_content.add_widget( self.map_view  )
            self.ids.float_content.add_widget( self.ecliptica ) 
            self.ids.float_content.add_widget( self.side_bar  )
        
            self.already_draw = True 

        return super().on_enter(*args)