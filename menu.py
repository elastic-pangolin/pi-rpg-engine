from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.clock import Clock

from PIL import Image as GifImage

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

    @staticmethod
    def _layout_text(text: str, width: int):
        words = str(text).split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += (word if not current_line else " " + word)
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return "\n".join(lines).replace("[LB]", "\n") # [LB] are literal linebreaks

    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        
        if not image_source:
            image_source = "dark_grey.png"
        self.source = image_source
        #self.size = img_size
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [50, 100, 50, 100]  # [left, top, right, bottom]

        with self.canvas.before:
            self.bg = Rectangle(source=self.source, size=self.size, pos=self.pos)

        # Core text label (drawn, not widget)
        self.title_label = CoreLabel(
            text=self._layout_text(text, 50),
            halign='center',
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

    def _schedule_after_gif(self, func):
        gifimg = GifImage.open(self.gif.source)
        frame_count = gifimg.n_frames
        duration = frame_count * self.gif.anim_delay
        print(f"DEBUG: found {frame_count} frames for a total of {duration} seconds")
        # Kivy always passes dt, so wrap your function
        #Clock.schedule_once(lambda dt: func(), duration)
        Clock.schedule_once(lambda dt: func(), duration)

    def add_animation(self, func='UNDEFINED', gif=None):
        if not func and not gif:
            return # nothing to do
        self.gif = Image(
            source=gif,
            anim_delay=1/24
        )
        self.add_widget(self.gif)
        if not func == 'UNDEFINED':
            Clock.schedule_once(lambda dt: self._schedule_after_gif(func), 0)

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
