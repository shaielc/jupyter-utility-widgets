
from typing import Any, Optional
from IPython.display import display
import ipywidgets
from jupyter_utility_widgets.chat.chat_display import ChatDisplay
from jupyter_utility_widgets.chat.message import Message, TextMessage
from jupyter_utility_widgets.chat.content_input import ContentInput

class ChatWidget(ipywidgets.VBox):
    USER_KEY = "USER"
    ASSISTANT_KEY = "ASSISTANT"

    def __init__(self, formats=None, message_input=None, **kwargs):
        formats =formats if formats is not None else {
            self.USER_KEY: (
                'background-color: #DCF8C6; '
                'border-radius: 10px 10px 0px 10px; '
                'padding: 8px; margin: 5px 0; max-width: 60%; '
                'float: right; clear: both;'
            ),
            self.ASSISTANT_KEY: (
                'background-color: #E0E0E0; '
                'border-radius: 10px 10px 10px 0px; '
                'padding: 8px; margin: 5px 0; max-width: 60%; '
                'float: left; clear: both;'
            )
        }
        self.output = ChatDisplay(formats, layout=ipywidgets.Layout(width='100%', height='300px', border='1px solid black', overflow='auto'))
        self.message_input = ContentInput(**(message_input if message_input is not None else {}))
        self.chat_history = []

        children = [
            self.output,
            self.message_input
        ]
        super().__init__(children, **kwargs, layout=ipywidgets.Layout(width='100%', overflow='auto'))

        self.message_input.on_send(self._apply_user_input)
        self.message_input.on_cancel(self.cancel_user_message)
        self.output.on_edit(self._edit_message_callback)
        self.observers = []
        self.current_editing_message: Optional[Message] = None  # Track the message being edited
    
    def reload(self,):
        self.output.clear()
        for messgae in self.chat_history:
            self.output.add_message(messgae)

    def register_style(self, key, format):
        self.output.styles[key] = format

    def _update_editing_message(self, content):
        if self.current_editing_message is None:
            raise RuntimeError("No message set to edit.")
        self.current_editing_message.content = content
        updated_message = self.current_editing_message
        self.output.update(updated_message)
        self.current_editing_message = None
        return updated_message
    
    def _new_user_message(self, content):
        message = Message(content, self.USER_KEY, self.message_input.input_type)
        self.add_message(message)
        return message
    
    def add_message(self, message):
        self.output.add_message(message)
        self.chat_history.append(message)

    def _apply_user_input(self, content: Any):
        if self.current_editing_message:
            notify_msg = self._update_editing_message(content)
        else:
            notify_msg = self._new_user_message(content)
        self._notify_message_change(notify_msg)
    
    def cancel_user_message(self,):
        if self.current_editing_message:
            self.current_editing_message = None
    
    def listen(self, func):
        self.observers.append(func)
    
    def _notify_message_change(self, content):
        for func in self.observers:
            func(content)
    
    def _edit_message_callback(self, message: Message):
        # Put the message content back into the input for editing
        self.message_input.load_content(message.content)
        self.current_editing_message = message
