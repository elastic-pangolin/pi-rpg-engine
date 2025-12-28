from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from buttons import *

# Menu layout
class MenuLayout(BoxLayout):
    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def __init__(self, image_source, **kwargs):
        super().__init__(**kwargs)
        
        self.source = image_source
        #self.size = img_size
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [50, 100, 50, 100]  # [left, top, right, bottom]

        with self.canvas.before:
            self.bg = Rectangle(source=self.source, size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)
        self._update_bg()

    def add_button(self, func, text=None, img=None):
        if img:
            #size_hint=(1,None), height=100
            self.add_widget(ImageButton(str(img), func))
        elif text:
            self.add_widget(TextButton(str(text), func, size_hint=(1, None), height=40))
        else:
            self.add_widget(Widget())  # Spacer
