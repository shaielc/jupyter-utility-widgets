from ipywidgets import Text, HBox, Valid, link, Dropdown, SelectMultiple
from traitlets import Unicode, observe, Bool
import os

class PathInput(HBox):
    value = Unicode()
    display_value = Unicode()
    VALID_BORDER = "black"
    INVALID_BORDER = "red"
    def __init__(self, *args, **kwargs) -> None:
        self.input = Text()
        self.is_valid = Valid()
        link((self,"value"), (self.input, "value"), (self.path_to_display, self.display_to_path))
        super().__init__([self.input, self.is_valid], *args, **kwargs)
        self.value = "./"

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

class DirectoryChooser(Dropdown):
    directory = Unicode()
    relative_mode = Bool(default_value=True)
    
    @observe("directory")
    def _new_directory(self, change):
        path = change.new

        if os.path.isdir(path):
            self.relative_mode = path[0] != "/"
            self.options = list(filter(lambda path: os.path.isdir(os.path.join(self.directory,path)),[".."] +os.listdir(path)))
    
    @observe("value")
    def _update_path(self, change):
        if change.new is None:
            return
        self.value = None
        path_solver = os.path.relpath
        if not self.relative_mode:
            path_solver = os.path.realpath
        self.directory = path_solver(os.path.join(self.directory, change.new))

class FileChooser(SelectMultiple):
    directory = Unicode()

    @observe("directory")
    def _new_directory(self, change):
        path = change.new
        
        if os.path.isdir(path):
            self.options = list(filter(lambda path: os.path.isfile(os.path.join(self.directory,path)),[".."] +os.listdir(path)))
    