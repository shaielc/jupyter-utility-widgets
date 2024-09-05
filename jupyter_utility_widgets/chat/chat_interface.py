from IPython.display import display
import ipywidgets
import traitlets
import anywidget
import pathlib


class Message(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "message.js"
    message = traitlets.Unicode("").tag(sync=True)
    inline_style = traitlets.Unicode("").tag(sync=True)
    sender = traitlets.Unicode("").tag(sync=True)

    def __init__(self, message, inline_style, sender, **kwargs):
        self.message = message
        self.inline_style = inline_style
        self.sender = sender
        self.edit_observers = []
        super().__init__(**kwargs)
        self.on_msg(self._handle_current_msg)
    
    def _handle_current_msg(self, widget, content, buffers):
        if content == "edit_request":
            self.edit_message()
    
    def on_edit(self, func):
        self.edit_observers.append(func)
    
    def edit_message(self,):
        for func in self.edit_observers:
            func(self)

    def update_message(self, new_message):
        self.message = new_message

class MessageInput(ipywidgets.HBox):
    def __init__(self, **kwargs):
        self.message_input = ipywidgets.Text(
            value="",
            placeholder="Type your message here",
            description="Message:",
            layout=ipywidgets.Layout(width="80%")
        )

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
        children = [
            self.message_input,
            self.cancel_button,
            self.send_button,
        ]
        self.send_observers = []
        self.cancel_observers = []
        super().__init__(children, **kwargs)
        self.send_button.on_click(self.send_notify)
        self.message_input.on_submit(self.send_notify)
        self.cancel_button.on_click(self.cancel_notify)
    
    def on_send(self, func):
        self.send_observers.append(func)

    def on_cancel(self, func):
        self.cancel_observers.append(func)
    
    def send_notify(self, b):
        for func in self.send_observers:
            func(self.message_input.value)
        self.message_input.value = ""
    
    def cancel_notify(self, b):
        for func in self.cancel_observers:
            func()
        self.message_input.value = ""


class ChatWidget(ipywidgets.VBox):
    USER_KEY = "USER"
    ASSISTANT_KEY = "ASSISTANT"

    def __init__(self, formats=None, message_input=None, **kwargs):
        self.output = ipywidgets.Output(
            layout=ipywidgets.Layout(width='100%', height='300px', border='1px solid black', overflow='auto')
        )
        self.message_input = MessageInput(**(message_input if message_input is not None else {}))

        self.chat_history = []
        self.styles = formats if formats is not None else {
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
       
        children = [
            self.output,
            self.message_input
        ]
        super().__init__(children, **kwargs)

        self.message_input.on_send(self.apply_user_message)
        self.message_input.on_cancel(self.cancel_user_message)
        self.observers = []
        self.current_editing_message = None  # Track the message being edited
    
    def reload(self,):
        self.output.clear_output()
        with self.output:
            for msg in self.chat_history:
                display(msg)

    def add_message(self, key, content):
        style = self.styles[key]
        msg = Message(content, style, key,)
        msg.on_edit(self.edit_message_callback)
        self.chat_history.append(msg)

        with self.output:
            display(msg)
        return msg

    def register_style(self, key, format):
        self.styles[key] = format

    def update_editing_message(self, content):
        self.current_editing_message.update_message(content)
        updated_message = self.current_editing_message
        self.current_editing_message = None
        return updated_message

    def apply_user_message(self, content):
        if self.current_editing_message:
            notify_msg = self.update_editing_message(content)
        else:
            notify_msg = self.add_message(self.USER_KEY, content)
        self.notify(notify_msg)
    
    def cancel_user_message(self,):
        if self.current_editing_message:
            self.current_editing_message = None
    
    def listen(self, func):
        self.observers.append(func)
    
    def notify(self, content):
        for func in self.observers:
            func(content)
    
    def edit_message_callback(self, message: Message):
        # Put the message content back into the input for editing
        self.message_input.message_input.value = message.message
        self.current_editing_message = message
