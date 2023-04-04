import View.MapScreen.map_screen

# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
import importlib
importlib.reload(View.MapScreen.map_screen)




class MapScreenController:
    """
    The `MapScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """
    def __init__(self, model):
        self.model = model  # Model.map_screen.MapScreenModel
        self.view = View.MapScreen.map_screen.MapScreenView(controller=self, model=self.model)
    def get_view(self) -> View.MapScreen.map_screen:
        return self.view


    