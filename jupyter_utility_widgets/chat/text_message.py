from typing import Optional
from jupyter_utility_widgets.chat.message import ContentType, Message
import traitlets
import pathlib
import ipywidgets

class TextMessageWidget(ipywidgets.HTML):
    # _esm = pathlib.Path(__file__).parent / "text_message.js"
    # content = traitlets.Unicode("").tag(sync=True)
    # inline_style = traitlets.Unicode("").tag(sync=True)
    # sender = traitlets.Unicode("").tag(sync=True)

    # def __init__(self, content, inline_style, sender, **kwargs):
        # self.content = content
        # self.inline_style = inline_style
        # self.sender = sender
        # self.edit_observers = []
        # super().__init__(**kwargs)
        # self.on_msg(self._handle_current_msg)
    
    def _format(self, value):
        return f"<span>{value}</span>"
    
    def __init__(self, content: Optional[str]=None, **kwargs):
        if content is not None:
            content = self._format(content)
        super().__init__(value=content, **kwargs)
    
    # def _handle_current_msg(self, widget, content, buffers):
    #     if content == "edit_request":
    #         self._edit_message()
    
    # def on_edit(self, func):
    #     self.edit_observers.append(func)
    
    # def _edit_message(self,):
    #     for func in self.edit_observers:
    #         func(self)

    def update_message(self, new_message: Message):
        self.value = self._format(new_message.content)


class TextContentInput:
    type = ContentType.TEXT

    @property
    def content(self,) -> str:
        return self.widget.value
    
    @content.setter
    def content(self, value):
        self.widget.value = value

    def __init__(self) -> None:
        self.widget = ipywidgets.Text(
            value="",
            placeholder="Type your message here",
            description="Message:",
            layout=ipywidgets.Layout(width="80%"),
            continuous_update=False
        )

    def attach(self, func):
        self.widget.on_submit(
            lambda evt: func(self)
        )
    
    def clear(self, ):
        self.widget.value = ""