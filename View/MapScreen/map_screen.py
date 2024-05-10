from libs.kivy_garden.mapview import MapView, MapMarkerPopup
from View.Widgets.SideBar.side_bar import SideBar 
from kivymd.uix.button import MDFlatButton
from kivymd.uix.widget import MDWidget 
from kivy.graphics import Line, Color
from kivymd.uix.label import MDLabel 
from kivy.clock import Clock 

from View.base_screen import BaseScreenView
from View.Widgets.Graphs.graph_sun_path import AzimuteAllDay, ZeniteAllDay 

#####################################
from libs.Sun import SunPosition 
import math 
#####################################

import os 
MAP_SOURCE_ICON = os.path.dirname(__file__).removesuffix('\\View\\MapScreen') + '/assets/icons/marker_popup.png' 

class Ecliptica( MDWidget ):

    SUN_DATA: SunPosition 
    latitude: float 
    longitude: float 

    # Norte = MDLabel( text = 'N', color = [0,0,1,1], bold = True, font_size = 16, size_hint =  [None, None] )
    # Lest  = MDLabel( text = 'L', color = [0,1,0,1], bold = True, font_size = 16, size_hint =  [None, None] )
    # Oeste = MDLabel( text = 'O', color = [1,0,0,1], bold = True, font_size = 16, size_hint =  [None, None] )
    
    def __init__(self, sun_data, size, pos, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = size
        self.pos_hint = pos 
        self.SUN_DATA = sun_data
        self.latitude  = sun_data.latitude
        self.longitude = sun_data.longitude
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
        
        # Atualiza os valores de lat, lon e hora 
        self.SUN_DATA.set_parameters( self.latitude, self.longitude, 300 )
        self.SUN_DATA.update_date()

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
        # self.Norte.pos = [center[0] - (r + 20), center[1] -10 ]    # Oeste -> pos    = [center[0] - (r + 20), center[1] -10 ]   )  
        # self.Lest.pos  = [center[0] + (r +  5), center[1] -10 ]    # Leste -> pos    = [center[0] + (r +  5), center[1] -10 ]   )  
        # self.Oeste.pos = [center[0] - 10 , center[1] - (r + 25) ]  # Norte -> pos    = [center[0] - 10 , center[1] - (r + 25) ] ) 
            
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
            MapMarkerPopup( lat=-29.71332542661317, lon=-53.71766381408064, source = MAP_SOURCE_ICON ) 
        ]
    markers[0].add_widget( MDFlatButton(text=f'Informações do sistema\nlat={markers[0].lat}\nlon={markers[0].lon}\nNot connected', md_bg_color='gray' ) )

    already_draw = False 
    ecliptica : Ecliptica 

    azimute_all_day : AzimuteAllDay
    zenite_all_day : ZeniteAllDay

    render_clock = None 

    def on_kv_post( self, *args ):
        self.side_bar = SideBar( model = self.model ) 
        self.ids.float_content.add_widget( self.side_bar )
        BaseScreenView.on_kv_post(self, *args )

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter (self, *args):    
        if not self.already_draw:
            #
            # Map view 
            self.map_view = MapView(size_hint = [0.99, 0.99], 
                    pos_hint = {'center_x': 0.50, 'center_y': 0.5 }, 
                    zoom = 25 , 
                    lon = self.markers[0].lon-0.00005, 
                    lat = self.markers[0].lat 
                )
            self.ids.float_content.add_widget( self.map_view  )
            #
            # Ecliptica draw 
            self.ecliptica = Ecliptica( 
                    sun_data = self.controller.get_sundata(), 
                    size = [1, 1], 
                    pos = {'center_x': 0.5,'center_y': 0.5} 
                )
            self.ids.float_content.add_widget( self.ecliptica ) 
            #
            # Graphs Zenite and Azimute 
            self.zenite_graph = ZeniteAllDay( hover = True )   
            self.ids.zenite_graph.add_widget( self.zenite_graph )
            self.azimute_graph = AzimuteAllDay( hover = True ) 
            self.ids.azimute_graph.add_widget( self.azimute_graph )
            
            #
            # Side bar 
            self.ids.float_content.remove_widget( self.side_bar )
            self.side_bar = SideBar( model = self.model ) 
            self.ids.float_content.add_widget( self.side_bar )
            
            #
            # Markers popup
            for marker in self.markers:
                # Faz a verificação se o marker já possui um parente
                if marker.parent is None:    
                    self.map_view.add_widget( marker )
                # Se ele possuir, temos que retira-lo e adicionar de novo 
                else: 
                    marker.parent.remove_widget(marker)
                    self.map_view.add_widget( marker )
            
            #
            # Flag already draw
            self.already_draw = True
            # Já atualiza a página
            Clock.schedule_once( self.render_page )
            Clock.schedule_once( self.att_graphs )

        # Quando entrar na página, executa o timer de 1 em 1 segundo 
        self.render_clock = Clock.schedule_interval( self.render_page, 1 )
        BaseScreenView.on_enter( self, *args)
    

    def on_leave(self, *args):
        # Quando sair da página, verifique se o timer esta ativo e desative-o
        if self.render_clock and self.render_clock in Clock.get_events():
            Clock.unschedule(self.render_clock)
        BaseScreenView.on_leave(self, *args)


    def on_touch_move(self, touch):
        coord = self.map_view.get_latlon_at(touch.pos[0], touch.pos[1])
        lat, lon = coord.lat, coord.lon 
        self.ids.latitude.text  = str( round(lat, 10) )
        self.ids.longitude.text = str( round(lon, 10) ) 
        self.ids.altitude.text = '325m'
        self.ecliptica.latitude = lat 
        self.ecliptica.longitude = lon 
        BaseScreenView.on_touch_move(self, touch)


    def render_page( self, clock_event ):
        # Atualiza a posição da ecliptica 
        self.ecliptica.update_canvas() 
        # Atualiza a hora correta
        self.ids.hora_att.text = self.controller.get_time() 
        self.ids.dia_att.text = self.controller.get_date()
        self.ids.hora_att_sun_progress.value = 100-(self.ecliptica.SUN_DATA.total_seconds/(24*3600))*-100
        
        # Atualiza a hora medida 
        if not self.controller.is_connected():
            self.ids.hora_sys.text = 'Not connected'
            self.ids.dia_sys.text = 'Not connected'
            self.ids.dia_sys_sun_progress.value = 0
        else: 
            self.ids.hora_sys.text = self.controller.get_sys_time()
            self.ids.dia_sys.text = self.controller.get_sys_date()
            self.ids.dia_sys_sun_progress.value = self.controller.get_sys_count()
        
        # Atualiza as informações do sistema 
        self.ids.daylight.text = str(self.ecliptica.SUN_DATA.get_sunlight_hours()).split('.')[0]
        self.ids.rising.text = str(self.ecliptica.SUN_DATA.rising.strftime('%H:%M:%S') )
        self.ids.culminant.text = str(self.ecliptica.SUN_DATA.transit.strftime('%H:%M:%S') )
        self.ids.sunset.text = str( self.ecliptica.SUN_DATA.sunset.strftime('%H:%M:%S') )
        

    def att_graphs( self, clock_event = None ): 
        data = self.model.SunData.trajetory( resolution = 50, all_day = False )
        azi, alt, time = [], [], []
        for az, al, dt in data: 
            azi.append( math.degrees(az - math.pi) if az > math.pi else math.degrees(az + math.pi) )
            alt.append( math.degrees(al) if al < math.pi else 0  )
            time.append(dt)
        self.zenite_graph.update_graph ( x_points = time, y_points = alt ) 
        self.azimute_graph.update_graph( x_points = time, y_points = azi )
