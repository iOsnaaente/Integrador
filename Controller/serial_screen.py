import View.SerialScreen.serial_screen
from kivy.logger import Logger

class SerialScreenController:
    """
    The `LoginScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """
    card_widget = None 

    def __init__(self, model, _debug: bool = False ):
        self.model = model  # Model.login_screen.LoginScreenModel
        self.view = View.SerialScreen.serial_screen.SerialScreenView( controller = self, model = self.model )
        self._debug = _debug 
        
        self.azimute = [0,0]
        self.zenite = [0,0]

    def get_view(self) -> View.SerialScreen.serial_screen.SerialScreenView:
        return self.view
    
    def get_shared_data( self ):
        return self.model
    
    def get_model( self ) :
        return self.model 

    def is_connected( self ):
        return self.model.is_connected()

    def update_values( self ) -> None:
        data = self.model.get_azimute_zenite_data()
        self.azimute = data[:2]
        self.zenite  = data[2:]

    def get_azimute_motor( self ) -> float:
        return self.azimute[0] if self.azimute[0] > 0 else -self.azimute[0] 
    def get_azimute_sensor( self ) -> float:
        return self.azimute[1] if self.azimute[1] > 0 else -self.azimute[1] 
    
    def get_zenite_motor( self ) -> float:
        return self.zenite[0] if self.zenite[0] > 0 else -self.zenite[0] 
    
    def get_zenite_sensor( self ) -> float:
        return self.zenite[1] if self.zenite[1] > 0 else -self.zenite[1]

                
    def change_operation_mode( self, type: str, value: bool  ):
        try:
            if type == 'AUTO' and value:
                self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.AUTOMATIC 
                self.view.ids.modo_manual.active = False 
                Logger.debug( f"{type}  {value}" )
                self.model.system.write = True
    
            elif type == 'MANUAL' and value :
                self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.REMOTE
                self.view.ids.modo_auto.active = False
                Logger.debug( f"{type}  {value}" )
                self.model.system.write = True

        except Exception as err:
            if self._debug:
                Logger.debug( f"{err}" )


    def check_motors_moving( self ):
        # Se o motor Azimute estiver ativo, ele muda de cor do icon para verde  
        if self.model.SYSTEM_TABLE['COIL_M_GIR']:
            self.view.ids.azimuth_moving.color = [ 0.1, 1.0, 0.1, 0.75 ]
        else:
            self.view.ids.azimuth_moving.color = [ 1.0, 0.1, 0.1, 0.75 ]
        
        # Se o motor Zenite estiver ativo, ele muda de cor do icon para verde 
        if self.model.SYSTEM_TABLE['COIL_M_ELE']:
            self.view.ids.zenith_moving.color = [ 0.1, 1.0, 0.1, 0.75 ]
        else:
            self.view.ids.zenith_moving.color = [ 1.0, 0.1, 0.1, 0.75 ]
        

    def turn_on_off_motors( self, state : bool ) -> None:
        try:
            if state:
                # Coloca em modo Remoto
                self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.REMOTE 
            else: 
                self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.AUTOMATIC                 
            # Aciona o relé dos motores 
            self.model.SYSTEM_TABLE['COIL_POWER'] = state
            # Habilita escrita 
            self.model.system.write = True
            if self._debug:
                Logger.debug( f'Turn On/Off motors: {state}' )
        except Exception as err: 
            if self._debug:
                Logger.debug( f"{err}" )
            

    def get_power_motors( self ) -> bool:
        try: 
            # Pega o estado do Coil Power e retorna 
            state = self.model.SYSTEM_TABLE['COIL_POWER']
            return state 
        except Exception as err: 
            return False
        
    def send_motors_vel( self ) -> None:
        Logger.debug( 'send_motors_vel' )
        try: 
            # Pega o valor de azimute  
            azi_text = self.view.ids.vel_azimute.text 
            # Transforam em numero e seta os limites 
            azi = float( azi_text ) if azi_text != '' else 0.0 
            azi = -100 if azi < -100 else 100 if azi > 100 else azi 
            # Se for 0 então o motor para, se não ele liga 
            if azi == 0:
                self.model.SYSTEM_TABLE['COIL_M_GIR'] = False 
            else:
                self.model.SYSTEM_TABLE['COIL_M_GIR'] = True 
            # Atualiza os valores para escrita 
            self.model.SYSTEM_TABLE['HR_AZIMUTE'] = azi
            # Habilita para ser escrito no sistema 
            self.model.system.write = True
        except Exception as err :
            Logger.debug( f"{err}" )
        try: 
            # Pega o valor de azimute  
            zeni_text = self.view.ids.vel_zenite.text
            # Transforam em numero e seta os limites 
            zeni = float( zeni_text ) if zeni_text != '' else 0.0 
            zeni = -100 if zeni < -100 else 100 if zeni > 100 else zeni 
            # Se for 0 então o motor para, se não ele liga 
            if zeni == 0:    
                self.model.SYSTEM_TABLE['COIL_M_GIR'] = False
            else: 
                self.model.SYSTEM_TABLE['COIL_M_GIR'] = True 
            # Atualiza os valores para escrita 
            self.model.SYSTEM_TABLE['HR_ZENITE'] = zeni
            # Habilita para ser escrito no sistema 
            self.model.system.write = True
        except Exception as err :
            if self._debug:
                Logger.debug( f"{err}" )


    def go_home_system( self ):
        Logger.debug('go home system')
        try: 
            # Coloca em condição de FAIL STATE 
            self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.REMOTE 
            # Liga os motores 
            self.model.SYSTEM_TABLE['COIL_M_GIR'] = True 
            self.model.SYSTEM_TABLE['COIL_M_ELE'] = True 
            # Escreve a posição de Home 
            self.model.SYSTEM_TABLE['HR_AZIMUTE'] = self.model.system_state.AZI_HOME 
            self.model.SYSTEM_TABLE['HR_ZENITE'] = self.model.system_state.ZEN_HOME
            # Habilita escrita
            self.model.system.write = True
        except Exception as err:    
            if self._debug:
                Logger.debug( f"{err}" ) 
            

    def att_zenith_graph_slider( self ):
        try: 
            # Lê a posição do slider  
            value = self.view.ids.zenith_graph_slider.value 
            # Escreve a posição do Slider no ZENITE 
            self.model.SYSTEM_TABLE['HR_PV_GIR'] = value*3.6
            # Muda o modo de operação para REMOTE 
            self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.REMOTE
            # Aciona o motor de ZENITE 
            self.model.SYSTEM_TABLE['COIL_M_ELE'] = True 
            self.model.system.write = True
            Logger.debug( f"{value}" ) 
        except Exception as err:
            Logger.debug( f"{err}" )

    def att_azimuth_graph_slider( self   ):
        try:
            # Lê a posição do slider  
            value = self.view.ids.azimuth_graph_slider.value
            # Escreve a posição do slider no AZIMUTE 
            self.model.SYSTEM_TABLE['HR_PV_ELE'] = value*3.6
            # Aciona o motor de AZIMUTE 
            self.model.SYSTEM_TABLE['COIL_M_GIR'] = True 
            # Muda o modo de operação para REMOTE 
            self.model.SYSTEM_TABLE['HR_STATE'] = self.model.system_state.REMOTE 
            self.model.system.write = True
            Logger.debug( f"{value}" ) 
        except Exception as err:
            Logger.debug( f"{err}" )
            
