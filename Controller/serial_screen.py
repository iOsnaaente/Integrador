import importlib

import View.SerialScreen.serial_screen

from Model.shared_data import SharedData 

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.SerialScreen.serial_screen)


class SerialScreenController:
    """
    The `LoginScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """
    card_widget = None 

    _shared_data : SharedData 

    def __init__(self, model, shared_data: SharedData, _debug: bool = False ):
        self.model = model  # Model.login_screen.LoginScreenModel
        self.view = View.SerialScreen.serial_screen.SerialScreenView( controller = self, model = self.model )
        self._shared_data = shared_data 
        self._debug = _debug 
        
        self.azimute = [0,0]
        self.zenite = [0,0]

    def get_view(self) -> View.SerialScreen.serial_screen:
        return self.view
    
    def get_shared_data( self ) -> SharedData:
        return self._shared_data

    def is_connected( self ):
        return self.model.is_connected()

    def update_values( self ) -> None:
        data = self.model.get_azimute_zenite_data()
        self.azimute = data[:2]
        self.zenite  = data[2:]

    def get_azimute_motor( self ) -> float:
        return self.azimute[0]
    def get_azimute_sensor( self ) -> float:
        return self.azimute[1]
    
    def get_zenite_motor( self ) -> float:
        return self.zenite[0]
    
    def get_zenite_sensor( self ) -> float:
        return self.zenite[1]


    def init_serial_conection( self ):
        pass 

    def refresh_serial_comports( self ):
        pass 

    def change_operation_mode( self ):
        pass 

    def turn_on_off_motors( self, state : bool ) -> None:
        if self._debug:
            print( 'Turn On Off motors: ', state)
        self.model.shared_data.SYSTEM_TABLE['COIL_POWER'] = state
        self.model.system.write = True

    def get_power_motors( self ) -> bool:
        return self.model.shared_data.SYSTEM_TABLE['COIL_POWER']

    def send_motors_vel( self ) -> None: 
        try: 
            azi = float( self.get_view().ids.vel_azimute.text.replace('Vel. Azi.:', '') )
            if azi > 100:       azi =  100 
            elif azi < -100:    azi = -100 
            zeni = float( self.get_view().ids.vel_zenite.text.replace('Vel. Zen.:','') )
            if zeni > 100:       zeni =  100 
            elif zeni < -100:    zeni = -100
            
            if azi == 0:
                self.model.shared_data.SYSTEM_TABLE['COIL_M_GIR'] = False 
            else:
                self.model.shared_data.SYSTEM_TABLE['COIL_M_ELE'] = True 
            if zeni == 0:
                self.model.shared_data.SYSTEM_TABLE['COIL_M_GIR'] = False
            else: 
                self.model.shared_data.SYSTEM_TABLE['COIL_M_GIR'] = True 
            self.model.shared_data.SYSTEM_TABLE['HR_ZENITE'] = zeni
            self.model.shared_data.SYSTEM_TABLE['HR_AZIMUTE'] = azi
            self.model.system.write = True
        except Exception as err :
            print( err )

    def go_home_system( self ):
        pass 