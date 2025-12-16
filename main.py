from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior

# Fix the window size
#Window.size = (400, 600)

# Define your button callbacks
def func_1():
    print("Button 1 clicked")

def func_2():
    print("Button 2 clicked")

# Create an image button
class ImageButton(ButtonBehavior, Image):
    def __init__(self, image_source, callback, **kwargs):
        super().__init__(**kwargs)
        self.source = image_source
        self.allow_stretch = True
        self.keep_ratio = False
        self.on_press_callback = callback

    def on_press(self):
        self.on_press_callback()

# Main layout
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [50, 100, 50, 100]  # [left, top, right, bottom]

        self.add_widget(Widget())  # Spacer

        btn1 = ImageButton("image_1.png", func_1, size_hint=(1, None), height=100)
        btn2 = ImageButton("image_2.png", func_2, size_hint=(1, None), height=100)

        self.add_widget(btn1)
        self.add_widget(btn2)

        self.add_widget(Widget())  # Spacer

# App class
class MyApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    MyApp().run()
