import pathlib
from typing import Any, List, Callable, Protocol, TypeVar, runtime_checkable
from anywidget import AnyWidget
from ipywidgets import DOMWidget, DOMWidget, widget_serialization
import traitlets

from jupyter_utility_widgets.chat.message import Message

T= TypeVar('T', bound=DOMWidget, covariant=True)

@runtime_checkable
class MessageDisplayWidget(Protocol[T]):
    def __init__(self, content) -> None:
        pass
    
    def update_message(self, message: Message) -> None:
        pass

class MessageDisplayWidgetTrait(traitlets.TraitType[MessageDisplayWidget, MessageDisplayWidget]):
    info_text ="A Message Display Widget"

    def validate(self, obj: Any, value: Any):
        if isinstance(obj, MessageDisplayWidget):
            return value
        self.error(obj,value)

class MessageDisplayWrapper(AnyWidget):
    _esm = pathlib.Path(__file__).parent / "message_wrapper.js"
    child = MessageDisplayWidgetTrait().tag(sync=True, **widget_serialization)
    inline_style = traitlets.Unicode("").tag(sync=True)
    sender = traitlets.Unicode("").tag(sync=True)

    def __init__(self, child, **kwargs) -> None:
        self.edit_observers: List[Callable] = []
        super().__init__(child=child, **kwargs)
        self.on_msg(self._handle_current_msg)
    
    def _handle_current_msg(self, widget, content, buffers):
        if content == "edit_request":
            self._edit_message()

    def on_edit(self, func: Callable):
        self.edit_observers.append(func)
    
    def _edit_message(self,):
        for func in self.edit_observers:
            func(self.child)
    
    def update_message(self, message: Message):
        self.child.update_message(message)
    