from IPython.display import display
import ipywidgets


class Message(ipywidgets.HTML):
    def __init__(self, message, style, msg_type, **kwargs):
        self.message = message
        self.inline_style = style
        self.sender = msg_type
        value = self.parse()
        super().__init__(value, **kwargs)
    
    def parse(self,):
        return f'<div style="{self.inline_style}"><b>{self.sender}:</b> {self.message}</div>'


class MessageInput(ipywidgets.HBox):
    def __init__(self, **kwargs):
        self.message_input = ipywidgets.Text(
            value="",
            placeholder="Type your message here",
            description="Message:",
            layout=ipywidgets.Layout(widget="80%")
        )
         
        self.send_button = ipywidgets.Button(
            description='Send',
            button_style='primary',
            layout=ipywidgets.Layout(width='20%')
        )
        children = [
            self.message_input,
            self.send_button
        ]
        self.observers = []
        super().__init__(children, **kwargs)
        self.send_button.on_click(self.notify)
        self.message_input.on_submit(self.notify)
    
    def listen(self, func):
        self.observers.append(func)
    
    def notify(self, b):
        for func in self.observers:
            func(self.message_input.value)
        self.message_input.value = ""

class ChatWidget(ipywidgets.VBox):
    USER_KEY = "USER"
    ASSITANT_KEY = "ASSISTANT"
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
            self.ASSITANT_KEY: (
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

        self.message_input.listen(self.add_user_message)
        self.observers = []
        

    def add_message(self, key, content):
        style = self.styles[key]
        msg = Message(content, style, key)
        self.chat_history.append(msg)

        with self.output:
            display(msg)

    def register_style(self, key, format):
        self.styles[key] = format

    def add_user_message(self, content):
        self.add_message("USER", content)
        self.notify(content)
    
    def listen(self, func):
        self.observers.append(func)
    
    def notify(self, content):
        for func in self.observers:
            func(content)
    