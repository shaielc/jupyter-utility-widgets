from jupyter_utility_widgets.chat.audio_message import AudioMessageInput
from jupyter_utility_widgets.chat.content_input_protocol import ContentInputProtocol
from jupyter_utility_widgets.chat.message import ContentType
from typing import Any, Dict
import ipywidgets

from jupyter_utility_widgets.chat.text_message import TextContentInput


class ContentInput(ipywidgets.HBox):
    _input_type: ContentType
    @property
    def input_method(self,):
        return self.input_methods[self._input_type]

    @property
    def input_type(self,):
        return self._input_type
    
    @input_type.setter
    def input_type(self, value: ContentType):
        widget = self.input_methods[value].widget
        self.children = [
            widget,
            self.select_input_types,
            self.cancel_button,
            self.send_button
        ]
        self._input_type = value
        self.select_input_types.value = value
    

    def __init__(self, input_method=ContentType.TEXT, **kwargs):
        self.input_methods: Dict[ContentType, ContentInputProtocol] = {
            ContentType.TEXT: TextContentInput(),
            ContentType.RAW_AUDIO: AudioMessageInput()
        }
        self.send_observers = []
        self.cancel_observers = []
        super().__init__([], **kwargs)
        self.select_input_types = ipywidgets.Dropdown(options=self.input_methods.keys())
        self.send_button = ipywidgets.Button(
            description='Send',
            button_style='primary',
            layout=ipywidgets.Layout(width='10%')
        ) 
        self.cancel_button = ipywidgets.Button(
            description='Cancel',
            button_style='danger',
            layout=ipywidgets.Layout(width='10%')
        )
        self.input_type = input_method
        self.send_button.on_click(self.send_notify)
        self.input_method.attach(self.send_notify)
        self.cancel_button.on_click(self.cancel_notify)
        self.select_input_types.observe(self._set_input_type)
    
    def _set_input_type(self, evt):
        self.input_type = self.select_input_types.value
    
    def on_send(self, func):
        self.send_observers.append(func)

    def on_cancel(self, func):
        self.cancel_observers.append(func)
    
    def send_notify(self, b):
        for func in self.send_observers:
            func(self.input_method.content)
        self.input_method.clear()
    
    def cancel_notify(self, b):
        for func in self.cancel_observers:
            func()
        self.input_method.clear()

    def load_content(self, content: Any):
        self.input_method.content = content