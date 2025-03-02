from libs.kivy_garden.graph import Graph, MeshLinePlot, Mesh
from View.Widgets.SideBar.side_bar import SideBar
from View.base_screen import BaseScreenView
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard 
from kivy.logger import Logger 
from kivy.clock import Clock

import datetime


class DiganosticosScreenView(BaseScreenView):
    # Card que armazena o gráfico
    graph_card: MDCard

    def __init__(self, **kw):
        super().__init__(**kw)
    
    def on_kv_post (self, *args):
        Clock.schedule_once( self.setup_graph, 0 )
        return super().on_kv_post(*args)


    # Callback para entrar na tela
    def on_enter(self, *args):
        # Coloca o side bar no lugar 
        self.side_bar = SideBar( model = self.model) 
        self.ids.float_content.add_widget( self.side_bar )
        self.ids.start_date.text = (datetime.date.today() - datetime.timedelta(days = 2 )).strftime("%d/%m/%Y")
        self.ids.end_date.text = datetime.date.today().strftime("%d/%m/%Y")
        return super().on_enter(*args)


    # Callback qundo sair da tela
    def on_leave( self, *args ):
        self.ids.float_content.remove_widget( self.side_bar )
        return super().on_leave(*args)
    

    def setup_graph( self, dt_clock = None ):
        # Recupera o widget MDCard que conterá o gráfico
        self.graph_card = self.ids.graph_zone
        # Cria o widget Graph
        graph = Graph(
            xlabel = "Data (hi)",
            ylabel = "Registro (°)",
            x_ticks_minor =  2,
            x_ticks_major =  6,
            y_ticks_minor = 45,
            y_ticks_major = 90,
            y_grid_label = True,
            x_grid_label = True,
            xmin = 0,
            xmax = 48,
            ymin = 0,
            ymax = 365,
            padding = 5,
            x_grid = True,
            y_grid = True
        )

        # Cria uma plotagem de exemplo (linha vermelha) com pontos simulados
        plot_data = MeshLinePlot(color=[1, 0, 0, 1])
        plot_data.set_mesh_size( 12 )
        plot_data.points = [ (x, y) for x, y in zip( range(0, 49, 1 ), range(0, 360, 360//49 ) ) ]
        graph.add_plot(plot_data)

        # Remove o conteúdo inicial (label) e adiciona o gráfico
        self.graph_card.clear_widgets()
        self.graph_card.add_widget(graph)


    def show_date_picker(self, focus):
        date_dialog = MDDatePicker(
            min_date = datetime.date.today() - datetime.timedelta( days = 2 ),
            max_date = datetime.date.today(),
            max_year = datetime.date.today().year,
            min_year = datetime.date.today().year - 1,
            title = "Periodo",
            mode = 'range',
            radius = [10,10,10,10]
        )
        date_dialog.bind( on_save = self.on_save_date, on_cancel = self.on_cancel_date )
        date_dialog.open()

    def on_save_date(self, instance, value, date_range):
        """ Atualiza os campos de texto com as datas selecionadas (formatação dd/mm/yyyy) """
        self.ids.start_date.text = date_range[0].strftime("%d/%m/%Y")
        self.ids.end_date.text = date_range[-1].strftime("%d/%m/%Y")
        
        """ Define o intervalo de busca no banco de dados """
        start_date  = datetime.datetime.combine(date_range[0], datetime.time.min)
        end_date    = datetime.datetime.combine(date_range[-1], datetime.time.max)
        Logger.debug( f"Start date: {start_date} \tEnd date: {end_date}")
        
        """ 
            Busca os valores no banco de dados 
        """        
        with self.model.db_lock:
            sensor_ele = self.model.system_database.read_data_by_date_range( 'history_sensor_ele', start_date, end_date )
            sensor_gir = self.model.system_database.read_data_by_date_range( 'history_sensor_gir', start_date, end_date )
            azimute = self.model.system_database.read_data_by_date_range( 'history_azimute', start_date, end_date )
            zenite = self.model.system_database.read_data_by_date_range( 'history_zenite', start_date, end_date )
            generation = self.model.system_database.read_data_by_date_range( 'history_generation', start_date, end_date )
        Logger.debug( f"Fim da busca por registros" )


        """
            Condiciona o tempo das medições para ser aceito no Plot 
        """ 
        if sensor_ele:
            x_values = [datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f%z") for row in sensor_ele]
        else: 
            x_values = []

        """ Definir intervalo de Plot """
        x_numeric = [d.timestamp() for d in x_values]  # Converte os datetime para números (timestamp)

        if len(x_numeric) > 1:
            xmin = x_numeric[0]
            xmax = x_numeric[-1]
            dt = (xmax - xmin) / (len(x_numeric) - 1)
        else:
            # Se houver somente um ponto, define xmin e xmax como o mesmo valor e dt como 1 (valor arbitrário)
            xmin = xmax = x_numeric[0] if x_numeric else 0
            dt = 1

        """
            Condiciona os dados medidos 
        """
        series = {
            'sensor_ele': {
                'y_values': [row[2] for row in sensor_ele],
                'color': [1, 0, 0, 1]  # Vermelho
            },
            'sensor_gir': {
                'y_values': [row[2] for row in sensor_gir],
                'color': [0, 1, 0, 1]  # Verde
            },
            'azimute': {
                'y_values': [row[2] for row in azimute],
                'color': [0, 0, 1, 1]  # Azul
            },
            'zenite': {
                'y_values': [row[2] for row in zenite],
                'color': [1, 1, 0, 1]  # Amarelo
            },
            'generation': {
                'y_values': [row[2] for row in generation],
                'color': [0, 1, 1, 1]  # Ciano
            }
        }


        # Atualiza a área do gráfico: limpa e adiciona o novo widget Graph
        """ Cria o widget Graph com os limites definidos """ 
        graph = Graph(
            xlabel = "Data (hi)",
            ylabel = "Registro (°)",
            x_ticks_minor =  2,
            x_ticks_major =  6,
            y_ticks_minor = 45,
            y_ticks_major = 90,
            y_grid_label = True,
            x_grid_label = True,
            xmin = xmin,
            xmax = xmax,
            ymin = 0,
            ymax = 365,
            padding = 5,
            x_grid = True,
            y_grid = True
        )

        ''' Adiciona os plots '''
        # Para cada série, cria um MeshLinePlot usando x_numeric como eixo X e os valores y correspondentes
        for name, props in series.items():
            plot = MeshLinePlot(color=props['color'])
            points = []
            
            # Garante que a lista de valores y tenha o mesmo comprimento que x_numeric
            for x_val, y_val in zip(x_numeric, props['y_values']):
                # Se necessário, converte o y_val para float
                try:
                    y_val = float(y_val)
                except Exception:
                    y_val = 0
                points.append((x_val, y_val))
                
            plot.points = points
            graph.add_plot(plot)
            Logger.info(f"Plot adicionado para a série {name}")

        self.ids.graph_zone.clear_widgets()
        self.ids.graph_zone.add_widget(graph)


    def on_cancel_date(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''
        print( instance, value )

    def gerar_relatorio(self):
        # Implementar a lógica para geração de relatório
        print("Gerar Relatório acionado!")
        # Aqui você pode adicionar a lógica de processamento e exibição do relatório

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """