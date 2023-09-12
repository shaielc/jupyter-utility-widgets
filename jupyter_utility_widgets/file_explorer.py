from ipywidgets import Text, HBox, Valid, link, Dropdown, SelectMultiple, Select, VBox, ValueWidget, Button
from traitlets import Unicode, dlink, observe, Bool
import os

def get_entries(directory, path, allow_files=True):
    check = os.path.exists
    if not allow_files:
        check = os.path.isdir

    return list(sorted(filter(lambda path: check(os.path.join(directory,path)),[".."] +os.listdir(path))))

def create_filter_ext(extensios, directory, allow_dir=True):
    def ext_filter(filename):
        path = os.path.join(directory, filename)
        if allow_dir and os.path.isdir(path):
            return True
        if not os.path.isfile(path):
            return False
        _, ext = os.path.splitext(path)
        return ext in extensios
    return ext_filter

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
            self.options = get_entries(self.directory, path, allow_files=False)
    
    @observe("value")
    def _update_path(self, change):
        if change.new is None:
            return
        self.value = None
        path_solver = os.path.relpath
        if not self.relative_mode:
            path_solver = os.path.realpath
        self.directory = path_solver(os.path.join(self.directory, change.new))

class FileChooser(Select):
    directory = Unicode()

    def __init__(self, *args, extensions=None, **kwargs):
        self.extensions = extensions

        super().__init__(*args, **kwargs)

    @observe("directory")
    def _new_directory(self, change):
        path = change.new
        
        if os.path.isdir(path):
            options = get_entries(self.directory, path)
            if self.extensions is not None:
                options = list(filter(create_filter_ext(self.extensions, self.directory), options))
            self.options = options

    @property
    def path(self,):
        return os.path.join(self.directory,self.value)


class FileExplorer(VBox, ValueWidget):
    value = Unicode()

    def __init__(self, directory="", extensions=None, **kwargs):
        self.directory_explorer = DirectoryChooser()
        self.file_explorer = FileChooser(extensions=extensions)
        self.input = PathInput()
        self.select_button = Button(description="Select")
        self.select_button.on_click(self.on_select)
        
        link((self.input, "value"), (self.directory_explorer, "directory"))
        dlink((self.input, "value"), (self.file_explorer, "directory"))
        
        children = [
            HBox([self.input, self.directory_explorer]),
            HBox([self.file_explorer, self.select_button])
        ]
        super().__init__(children, **kwargs)
        self.directory = directory

    def on_select(self, evt):
        self.value = self.file_explorer.path

    @property
    def directory(self,):
        return self.directory_explorer.directory
    
    @directory.setter
    def directory(self, value):
        self.directory_explorer.directory = value