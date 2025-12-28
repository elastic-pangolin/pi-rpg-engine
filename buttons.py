from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior

# Create an image button
class ImageButton(ButtonBehavior, Image):
    def __init__(self, image_source, callback, **kwargs):
        super().__init__(**kwargs)
        self.on_press_callback = callback
        self.source = image_source
        self.allow_stretch = False
        self.keep_ratio = True

    def on_press(self):
        self.on_press_callback()

class TextButton(Button):
    def __init__(self, text, callback, **kwargs):
        super().__init__(**kwargs)
        self.on_press_callback = callback
        self.text = text
        self.allow_stretch = True
        self.keep_ratio = False

    def on_press(self):
        self.on_press_callback()
