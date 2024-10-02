from typing import Callable
from ipywidgets import VBox, HBox
import numpy as np
from jupyter_utility_widgets.audio import Audio
from jupyter_utility_widgets.chat.content_input_protocol import ContentInputProtocol
from jupyter_utility_widgets.chat.message import ContentType

class AudioMessageInput(ContentInputProtocol):
    type = ContentType.AUDIO

    @property
    def content(self,) -> np.ndarray:
        return self.audio_widget.audio
    
    @content.setter
    def content(self, value):
        self.audio_widget.audio = value

    def __init__(self, **kwargs):
        self.audio_widget = Audio()
        self.controls = self.audio_widget.get_audio_controls(record=True, play=True)
        children=[HBox([self.audio_widget, *self.controls])]
        self.widget = VBox(children)
    
    def attach(self, func: Callable) -> None:
        pass

    def clear(self,):
        self.audio_widget.audio = np.empty((0,))
        self.audio_widget.recording = False
        self.audio_widget.playing = False