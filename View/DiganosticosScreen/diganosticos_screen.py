from libs.kivy_garden.graph import Graph, MeshLinePlot
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
        return super().on_enter(*args)


    # Callback qundo sair da tela
    def on_leave( self, *args ):
        self.ids.float_content.remove_widget( self.side_bar )
        return super().on_leave(*args)
    

    def setup_graph( self, dt_clock = None ):
        pass 
        # Recupera o widget MDCard que conterá o gráfico
        # self.graph_card = self.ids.graph_zone
        # # Cria o widget Graph
        # graph = Graph(
        #     xlabel='X',
        #     ylabel='Y',
        #     x_ticks_minor=5,
        #     x_ticks_major=25,
        #     y_ticks_minor=5,
        #     y_ticks_major=25,
        #     y_grid_label=True,
        #     x_grid_label=True,
        #     padding=5,
        #     x_grid=True,
        #     y_grid=True,
        #     xmin=0,
        #     xmax=100,
        #     ymin=0,
        #     ymax=100
        # )
        # # Cria uma plotagem de exemplo (linha vermelha) com pontos simulados
        # plot_data = MeshLinePlot(color=[1, 0, 0, 1])
        # plot_data.points = [(x, x) for x in range(0, 101, 10)]
        # graph.add_plot(plot_data)

        # # Remove o conteúdo inicial (label) e adiciona o gráfico
        # self.graph_card.clear_widgets()
        # self.graph_card.add_widget(graph)


    def show_date_picker(self, focus):
        date_dialog = MDDatePicker(
            min_date = datetime.date( 
                datetime.date.today().year,
                datetime.date.today().month,
                datetime.date.today().day - 1,
            ),
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
        end_date    = datetime.datetime.combine(date_range[1], datetime.time.max)
        Logger.debug( f"Start date: {start_date} \tEnd date: {end_date}")
        
        """ 
            Busca os valores no banco de dados 
        """
        h_regs = self.model.device_manager.database.read_data_by_date_range( 'holding_register', start_date, end_date )
        Logger.debug( f"Registros encontrados: {h_regs}" )


        """
            Filtrar dados 
            1. Valores de PV ( Azimute e Zenite ) 
            2. Valores de MV ( Sensor Azi e Zen ) 
            3. Valores de Produção 
            4. Data e hora 
        """ 


        """ Definir intervalo de Plot """
        xmin = date_range[ 0].toordinal()
        xmax = date_range[-1].toordinal()
        if ( xmax - xmin ) == 0:
            xmin = date_range[ 0 ].toordinal()
            xmax = date_range[-1 ].toordinal() + 1  # Para incluir o dia de inicio no gráfico
            dt = 1 
        else: 
            dt = xmax - xmin

        """ Cria o widget Graph com os limites definidos """ 
        graph = Graph(
            xlabel = "Data",
            ylabel = "Registro",
            x_ticks_minor =  1,
            x_ticks_major =  3,
            y_ticks_minor = 15,
            y_ticks_major = 25,
            xmin = 0,
            xmax = dt*24,
            ymin = -200,
            ymax = 200,
            padding = 5,
            x_grid = True,
            y_grid = True
        )

        # Cria uma plotagem dos valore (linha vermelha) com pontos para cada dia do intervalo
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        points = []
        current_date = date_range[0]
        while current_date <= date_range[-1]:
            x = current_date.toordinal()
            y = 0  
            points.append((x, y))
            current_date += datetime.timedelta(days=1)
        plot.points = points
        graph.add_plot(plot)

        # Atualiza a área do gráfico: limpa e adiciona o novo widget Graph
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