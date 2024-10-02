from jupyter_utility_widgets.chat.message import ContentType
from typing import Any, Protocol, Callable
from ipywidgets import Widget

class ContentInputProtocol(Protocol):
    content: Any
    widget: Widget
    type: ContentType
    
    def attach(self, func: Callable) -> None:
        pass

    def clear(self,) -> None:
        pass
