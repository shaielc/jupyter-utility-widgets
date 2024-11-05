from __future__ import annotations
from jupyter_utility_widgets.chat.audio_message import AudioMessageWidget
from jupyter_utility_widgets.chat.message import Message
from jupyter_utility_widgets.chat.message import ContentType, Message
from jupyter_utility_widgets.chat.message_display import MessageDisplayWidget, MessageDisplayWrapper
from jupyter_utility_widgets.chat.text_message import TextMessageWidget
from ipywidgets import Output
from typing import Dict, List
import uuid

def message_display_factory(message: Message):
    if message.type == ContentType.TEXT:
        return TextMessageWidget(
            content=message.content
        )
    if message.type == ContentType.RAW_AUDIO:
        return AudioMessageWidget(content=message.content) #TODO: apply style
    else:
        raise NotImplementedError("Displaying message of type %s is not supported. yet." % message.type)

class ChatDisplay(Output):
    def __init__(self, formats, **kwargs):
        super().__init__(**kwargs)
        self.history: List[MessageDisplayWidget] = []
        self.index: Dict[uuid.UUID, MessageDisplayWidget] = {}
        self.styles: Dict[str, str] = formats
        self.edit_observers = []

    def on_edit(self, func):
        self.edit_observers.append(func)

    def notify_start_edit(self, message):
        print(self.edit_observers)
        for func in self.edit_observers:
            func(message)

    def update(self, message: Message):
        message_widget = self.index[message.uid]
        message_widget.update_message(message)

    def add_message(self, message: Message):
        message_widget = MessageDisplayWrapper(
            message_display_factory(message),
            inline_style=self.styles.get(message.source),
            sender=message.source
        )
        self.history.append(message_widget)
        self.index[message.uid] = message_widget
        message_widget.on_edit(lambda widget: self.notify_start_edit(message))
        self.append_display_data(message_widget)
    
    def remove_message(self, message):
        widget = self.index.pop(message.uid)
        i = self.history.index(widget)
        widget.close()
        del widget
        return i
    
    def clear(self,):
        self.clear_output()
        self.history = []
        self.index = {}