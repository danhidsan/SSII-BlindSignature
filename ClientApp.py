import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config

kivy.require('1.9.0')

Config.set('graphics', 'width', 400)
Config.set('graphics', 'height', 200)


class Container(BoxLayout):
    None


class MainApp(App):
    title = "Puntuality Voting App"

    def build(self):
        return Container()


if __name__ == '__main__':
    MainApp().run()