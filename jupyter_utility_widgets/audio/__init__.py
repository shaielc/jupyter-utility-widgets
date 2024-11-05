import traitlets
import anywidget
import pathlib
import numpy as np
from ipywidgets import Button
from scipy.signal import resample_poly


def _serialize_audio(value: np.ndarray, widget):
    return value.data


def _deserialize_audio(value, widget):
    return np.asarray(value, dtype=np.uint8).view(np.float32)


class Audio(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "audio.js"
    recording = traitlets.Bool(False).tag(sync=True)
    playing = traitlets.Bool(False).tag(sync=True)
    audio = traitlets.Instance(np.ndarray, allow_none=False, default_value=np.empty(0, dtype=np.float32))\
        .tag(sync=True, to_json=_serialize_audio, from_json=_deserialize_audio)
    sample_rate = traitlets.Int().tag(sync=True)
    
    def __init__(self, recording=False, **kwargs):
        self.recording = recording
        super().__init__(**kwargs)
        self.on_msg(self._handle_current_message)
    
    def _handle_current_message(self, widget, content, buffers):
        if content["type"] == "resample":
            down = content["current"]
            if down == 0:
                return
            up = content["out"]
            self.audio = resample_poly(self.audio, up, down)
    
    @traitlets.validate("playing")
    def _validate_playing(self, proposal):
        if proposal["value"] and self.recording:
            return False
        return proposal["value"]
    
    @traitlets.validate("audio")
    def _validate_audio(self, proposal):
        return np.asarray(proposal["value"]).astype(np.float32)
    
    def play_toggle(self,):
        self.recording = False
        self.playing = not self.playing
    
    def record_toggle(self,):
        self.playing = False
        self.recording = not self.recording


    def get_audio_controls(self, record=False, play=False):
        controls = []
        if record:
            btn = Button(icon="circle", layout={"width": "fit-content"})
            btn.on_click(lambda btn: self.record_toggle())
            controls.append(btn)
        if play:
            btn = Button(icon="play", layout={"width": "fit-content"})
            btn.on_click(lambda btn: self.play_toggle())
            controls.append(btn)
        return controls


