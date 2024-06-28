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
    zenite_motor: SmoothLinePlot | None = None 
    zenite_sensor: SmoothLinePlot | None = None 

    already_draw = False 
    count_disconn = 0 

    MAX_POINTS_GRAPH_CANVAS = 100
    _x = [0]

    def __init__(self, **kw):
        super().__init__(**kw)


    def on_kv_post(self, base_widget):
        # Side bar 
        self.side_bar = SideBar( model = self.model ) 
        self.ids.float_content.add_widget   ( self.side_bar )
        
        # Serial configuration 
        self.Serial = SerialConfiguration(  )
        self.ids.serial.add_widget       ( self.Serial   )
        
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

        # Adiciona o Callback dos Sliders 
        # self.ids.azimuth_graph_slider.bind( on_value_pos = self.controller.att_azimuth_graph_slider )
        # self.ids.zenith_graph_slider.bind( on_value_pos = self.controller.att_zenith_graph_slider )

        
        Clock.schedule_interval( self.render, 0.1 )
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

        if self.controller.is_connected():  
            # Se o sistema estiver conectado, ele remove a marca d'agua 
            self.ids.graph_system_off.pos_hint = {'center_x': 500.0 }
            self.ids.power_widget_switch.active = self.controller.get_power_motors()
            
            self.count_disconn = 0 

        else:      
            self.count_disconn += 1
            if self.count_disconn > 25:                         
                # Se não estiver conectado, ele não atualiza os valores do gráfico
                self.ids.graph_system_off.pos_hint = {'center_x': 0.50 }
                self.ids.power_widget_switch.active = False 
            return 
        


        # Ativa e desativa os sliders 
        if self.model.SYSTEM_TABLE['HR_STATE'] == self.model.REMOTE: 
            self.ids.azimuth_graph_slider.disabled = False  
            self.ids.zenith_graph_slider.disabled  = False 
        else: 
            self.ids.azimuth_graph_slider.disabled = True   
            self.ids.zenith_graph_slider.disabled  = True  

        # Atualiza os valores de acionamento dos motores 
        self.controller.check_motors_moving( )


        # Atualiza os valores dos pontos dos gráficos
        if len(self._x) > self.MAX_POINTS_GRAPH_CANVAS: 
            self.azimute_motor.points.pop(0)
            self.azimute_sensor.points.pop(0)
            self.zenite_motor.points.pop(0)
            self.zenite_sensor.points.pop(0)
            self._x.pop(0)
        self._x.append( self._x[-1] + clk_event )
        self.ids.zenith_graph.xmin  = math.ceil( self._x[ 0 ] )
        self.ids.zenith_graph.xmax  = math.ceil( self._x[-1 ] )
        self.ids.azimuth_graph.xmin = math.ceil( self._x[ 0 ] )
        self.ids.azimuth_graph.xmax = math.ceil( self._x[-1 ] )
        self.controller.update_values()
        self.azimute_motor.points.append ( (self._x[-1], self.controller.get_azimute_motor()    ) )
        self.azimute_sensor.points.append( (self._x[-1], self.controller.get_azimute_sensor()   ) )
        self.zenite_motor.points.append  ( (self._x[-1], self.controller.get_zenite_motor()     ) )
        self.zenite_sensor.points.append ( (self._x[-1], self.controller.get_zenite_sensor()  ) )



    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """