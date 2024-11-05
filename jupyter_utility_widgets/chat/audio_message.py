from dataclasses import dataclass
from typing import Callable, Optional
from ipywidgets import VBox, HBox
import numpy as np
from jupyter_utility_widgets.audio import Audio
from jupyter_utility_widgets.chat.content_input_protocol import ContentInputProtocol
from jupyter_utility_widgets.chat.message import ContentType, RawAudioContent
from scipy.signal import resample_poly



def set_audio(audio_widget: Audio, raw_audio: RawAudioContent):
    data = raw_audio.data
    if raw_audio.sample_rate != audio_widget.sample_rate:
        data = resample_poly(data, raw_audio.sample_rate, audio_widget.sample_rate)
    audio_widget.audio = data
    
class AudioMessageWidget(HBox):
    def __init__(self, content: Optional[RawAudioContent] = None, **kwargs) -> None:
        if content is not None:
            self.audio_widget = Audio(
                audio=content.data,
                sample_rate=content.sample_rate
            )
        else:
            self.audio_widget = Audio()
        self.controls = self.audio_widget.get_audio_controls(play=True)
        children = [self.audio_widget, *self.controls]
        super().__init__(children, **kwargs)
    
    def update_message(self, message):
        pass


class AudioMessageInput(ContentInputProtocol):
    type = ContentType.RAW_AUDIO

    @property
    def content(self,) -> RawAudioContent:
        return RawAudioContent(
            self.audio_widget.audio,
            self.audio_widget.sample_rate
        )
    
    @content.setter
    def content(self, value: RawAudioContent):
        set_audio(self.audio_widget, value)

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