from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine

KV = '''
#THE CONTENT GOES ABOVE EVERYTHING ELSE EVEN THE 1ST SCREEN.#
#IT IS REFERENCED LATER IN WHICH EVER SCREEN IT IS TO APPEAR USING MDGridLayout AND A def LATER ON#
#It should also always have these angle brackets <>#
<Content>
    size_hint_y: None
    height: self.minimum_height
    orientation: 'vertical'
    OneLineIconListItem:
        text: 'Dark theme'
        on_release:app.theme_changer2()
        divider: None
        IconLeftWidget:
            icon: 'weather-night'
            on_release:app.theme_changer2()
    OneLineIconListItem:
        text: 'Light theme'
        on_release:app.theme_changer()
        divider: None
        IconLeftWidget:
            icon: 'white-balance-sunny'
            on_release:app.theme_changer()

<Content2>
    size_hint_y: None
    height: self.minimum_height
    orientation: 'vertical'
    OneLineIconListItem:
        text: 'I try to explain what i think are key points to note'
        on_release:app.theme_changer2()
        divider: None
        IconLeftWidget:
            icon: 'weather-night'
            on_release:app.theme_changer2()
    OneLineIconListItem:
        text: 'Hope this helps someone else'
        on_release:app.theme_changer()
        divider: None
        IconLeftWidget:
            icon: 'white-balance-sunny'
            on_release:app.theme_changer()

MDScreen:
    MDNavigationLayout:
        ScreenManager:
            id: manager
            MDScreen:
                name: 'Home'
                #The location of this MDGridLayout shows it appears in the 1st screen.#
                MDGridLayout:
                    cols: 1
                    adaptive_height: True
                    #This id is used to reference what content goes to which expansion panel#
                    id: box2
                MDRaisedButton:
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    text: "PRESS ME"
                    on_release: manager.current = 'Home2'
            MDScreen:
                name: 'Home2'
                MDBoxLayout:
                    orientation: "vertical"
                    MDTopAppBar:
                        id: mdt_color
                        elevation: 10
                    ScrollView:
                        divider: 'None'
                        #The location of this MDGridLayout shows it appears in the 2nd screen.#
                        MDGridLayout:
                            cols: 1
                            adaptive_height: True
                            id: box
                MDIconButton:
                    pos_hint: {"center_x": 0.05, "center_y": 0.945}
                    icon: "keyboard-backspace"
                    on_release: manager.current = 'Home'

'''
# Every expansion panel should have a class corresponding to it's name e.g.#
class Content(MDBoxLayout):
    pass
# The class name is referenced in the contents= section below#
class Content2(MDBoxLayout):
    pass
class MainApp(MDApp):
    def theme_changer(self):
        self.theme_cls.theme_style = "Light"
        self.root.ids.mdt_color.md_bg_color = [1, 1, 1, 1]
    def theme_changer2(self):
        self.theme_cls.theme_style = "Dark"
        self.root.ids.mdt_color.md_bg_color = [0, 0, 0, 1]
    def build(self):
        return Builder.load_string(KV)
    def on_start(self):
        # Here you see the id box used#
        self.root.ids.box.add_widget(
            MDExpansionPanel(
                icon="theme-light-dark",
                # Here the content name Content is referenced in content=#
                content=Content(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Theme",
                )
            )
        )
        # Here you see the id box2 used#
        self.root.ids.box2.add_widget(
            MDExpansionPanel(
                icon="theme-light-dark",
                # Here the content name Content2 is referenced in content=#
                content=Content2(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Read the code #comments# for details",
                )
            )
        )
ma = MainApp()
ma.run()