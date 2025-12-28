from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp

from buttons import *

# object to hold all layouts
class ScreenRoot(FloatLayout):
    def show(self, widget):
        self.clear_widgets()
        self.add_widget(widget)

# Menu layout
class MenuLayout(BoxLayout):
    def _update_all(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        # Center title near top
        self.title_rect.pos = (
            self.center_x - self.title_rect.size[0] / 2,
            self.top - self.title_rect.size[1] - 40
        )

    def set_title(self, text):
        self.title_label.text = text
        self.title_label.refresh()
        self.title_rect.texture = self.title_label.texture
        self.title_rect.size = self.title_label.texture.size
        self._update_all()

    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        
        self.source = image_source
        #self.size = img_size
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [50, 100, 50, 100]  # [left, top, right, bottom]

        with self.canvas.before:
            self.bg = Rectangle(source=self.source, size=self.size, pos=self.pos)

        # Core text label (drawn, not widget)
        self.title_label = CoreLabel(
            text=text,
            font_name="UI",
            font_size=dp(36),
            color=(1, 1, 1, 1)
        )
        self.title_label.refresh()
        with self.canvas.after:
            self.title_rect = Rectangle(
                texture=self.title_label.texture,
                size=self.title_label.texture.size,
                pos=(0, 0)
            )

        self.bind(size=self._update_all, pos=self._update_all)
        self._update_all()

    def add_button(self, func, text=None, img=None):
        if img:
            #size_hint=(1,None), height=100
            self.add_widget(ImageButton(str(img), func))
        elif text:
            self.add_widget(TextButton(str(text), func, 
                size_hint=(1, None), height=40,
                font_name="UI", font_size=dp(28)))
        else:
            self.add_widget(Widget())  # Spacer
