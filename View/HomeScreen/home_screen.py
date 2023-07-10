from kivymd_extensions.akivymd.uix.progresswidget import AKCircularProgress 
from View.MapScreen.map_screen import MapMarkerPopup 
from View.Widgets.SideBar.side_bar import SideBar 
from View.MapScreen.map_screen import MapView
from View.base_screen import BaseScreenView
from kivy.animation import Animation
from kivymd.app import MDApp 

from kivy.clock import Clock 

from libs.kivy_garden.graph import SmoothLinePlot
from libs.kivy_garden.graph import BarPlot
from libs.kivy_garden.graph import Graph


APP = MDApp.get_running_app()

import os 
PATH = os.path.dirname( __file__ )
IMAGES = PATH.removesuffix('\\View\\HomeScreen') + '/assets/images/'
MAP_ICON = PATH.removesuffix('\\View\\HomeScreen') + '/assets/icons/marker_popup.png' 

class HomeScreenView( BaseScreenView ):

    side_bar : SideBar
    
    map_view : MapView 
    
    graph : Graph 
    bar_plot: BarPlot
    line_plot: SmoothLinePlot 

    render_event = None 

    graphs_active: bool = False 


    # Quando o arquivo KV já terminou de instanciar as classes dentro do arquivo
    #   
    def on_kv_post(self, *args):
        # Side bar init 
        self.side_bar = SideBar( model = self.model ) 
        # Map view init 
        self.map_view = MapView ( 
            lat = -29.71302542661317, 
            lon = -53.71766381408064,
            zoom = 18,  
            pos_hint = {'center_x': 0.50, 'center_y': 0.5 } 
        ) 
        marker = MapMarkerPopup( 
            lat = -29.71332542661317, 
            lon = -53.71766381408064, 
            source = MAP_ICON,
            popup_size = [25, 25]
        ) 
        self.map_view.add_widget( marker )
        self.ids.box_content.add_widget     ( self.side_bar             )
        self.ids.map_content.add_widget     ( self.map_view             )
        
        # Generation Ploter init 
        points = [  6461,  5963, 4967,  3891,  2809,  2333,  2563,  3323,  3774,  4927,  6275,  6809 ]
        mean = sum( points ) / len( points )
        major = max( points )
        self.graph = Graph(
            xlabel = 'Time [months]', 
            ylabel = 'Power generated [Wh/m².dia]', 
            xmin = 0,
            xmax = 12,
            ymax = 10_000,
            x_ticks_minor = 1,
            x_ticks_major = 2,
            y_ticks_major = major//4,
            y_grid_label = True,
            x_grid_label = True,
            padding = 5 ,
            x_grid = False, 
            y_grid = True,
        )

        self.bar_plot = BarPlot( 
            color = [226/255, 141/255, 0, 1 ],
            bar_width = 1, #self.ids.log_content.width//3,
            points = zip( [i for i in range(12)], [  6461,  5963, 4967,  3891,  2809,  2333,  2563,  3323,  3774,  4927,  6275,  6809 ] )
        ) 
        self.line_plot = SmoothLinePlot( 
            color = [ 1, 0.25, 0.2, 0.85 ],
            points = zip( 
                [ i for i in range(12) ], 
                [ 2*mean - i for i in [  6461,  5963, 4967,  3891,  2809,  2333,  2563,  3323,  3774,  4927,  6275,  6809 ]]
            )
        )
        self.graph.add_plot( self.bar_plot )
        self.graph.add_plot( self.line_plot ) 
        self.ids.log_content.add_widget( self.graph )
        
        self.render_event = Clock.schedule_interval(self.render, 0.1)        
        return super().on_kv_post(*args)


    # Callback para entrar na tela
    def on_enter(self, *args):
        # Inicia a conexão do sistema
        if self.controller.auto_connect():
            if not self.controller.already_connected():
                self.controller.connect_system()
        # Coloca o side bar no lugar 
        self.side_bar = SideBar(model=self.model) 
        self.ids.box_content.add_widget( self.side_bar )
        self.render_event = Clock.schedule_interval(self.render, 0.1)
        # Animação do plot bar 
        self.bar_plot.bar_width = 0
        Animation( bar_width =  self.ids.log_content.width//15, duration = 1 ).start( self.bar_plot )
        return super().on_enter() 


    # Quando sai da tela, deve desativar os schedules 
    def on_leave(self, *args):
        self.bar_plot.bar_width = 0
        Clock.unschedule( self.render_event )
        self.render_event = None 
        BaseScreenView.on_leave(self, *args)

    # Quando a tela é redimensionada, é importante mexer nos valores do BarPlot 
    def on_size( self, *args ): 
        Animation( bar_width =  self.ids.log_content.width//15, duration = 0.15 ).start( self.bar_plot )

    # Render da página. Situações dinâmicas 
    def render( self, dt = None ):
        if self.controller.system_connected():
            # self.ids.icon_system_status.color = 
            # self.ids.icon_geracao.color = 
            # self.ids.label_geracao.
            # self.ids.label_system_status.
            print('Sistema conectado')
            
        else: 
            print('Sistema Não conectado')
            

    @property 
    def username( self ): 
        return self.model.shared_data.username 
    @property 
    def last_access( self ): 
        return self.model.shared_data.last_access 
    @property 
    def level_access( self ): 
        return self.model.shared_data.level_access


    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
