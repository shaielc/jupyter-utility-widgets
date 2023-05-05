from ipywidgets import Text, HBox, Valid, link
from traitlets import Unicode, observe
import os

class PathInput(HBox):
    value = Unicode()
    display_value = Unicode()
    VALID_BORDER = "black"
    INVALID_BORDER = "red"
    def __init__(self, *args, **kwargs) -> None:
        self.input = Text()
        self.is_valid = Valid()
        link((self,"value"), (self.input, "value"), (self.display_to_path, self.path_to_display))
        super().__init__([self.input, self.is_valid], *args, **kwargs)

    def display_to_path(self, value):
        if len(value) == 0 or value[0] != "/":
            return os.path.join("./", value)
        return value
    
    def path_to_display(self, value: str):
        if value.startswith("./"):
            return value[2:]
        return value

    @observe('value')
    def _check_value(self, change):
        self.is_valid.value = os.path.exists(change.new)
        self.input.layout.border = "1px solid %s" % (self.VALID_BORDER if self.is_valid.value else self.INVALID_BORDER)
