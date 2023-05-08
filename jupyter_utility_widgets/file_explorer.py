from ipywidgets import Text, HBox, Valid, link, Dropdown
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

class DirectoryChooser(HBox):
    directory = Unicode()
    def __init__(self, *args, **kwargs) -> None:
        self.select = Dropdown()
        self.relative_mode = True
        super().__init__([self.select], *args, **kwargs)
        self.select.observe(self._update_path, names=["value"])
    
    @observe("directory")
    def _new_directory(self, change):
        path = change.new

        if os.path.isdir(path):
            self.relative_mode = path[0] != "/"
            self.select.options = list(filter(lambda path: os.path.isdir(os.path.join(self.directory,path)),[".."] +os.listdir(path)))
        
    def _update_path(self, change):
        if change.new is None:
            return
        self.select.value = None
        path_solver = os.path.relpath
        if not self.relative_mode:
            path_solver = os.path.realpath
        self.directory = path_solver(os.path.join(self.directory, change.new))

# class DirectoryChooser:
#     path_inp = Text()
#     select_subdir = Dropdown()
#     select_valid_subdir = Dropdown()
#     set_dir = Button(description="Set dir")
#     directory = directory
#     save_directory = save_directory
    
#     @classmethod
#     def set_directory(cls, directory=None):
#         if directory is None:
#             directory = cls.path_inp.value
#         if os.path.isdir(directory):
#             cls.directory = directory
#             cls.path_inp.value = directory
#             subdirs = sorted([e for e in os.listdir(cls.directory) if os.path.isdir(os.path.join(cls.directory, e) )])
#             cls.select_subdir.options = [""] + subdirs + [".."]
#             valid_subdirs = [e for e in subdirs if is_formatted_dir(os.path.join(cls.directory, e))] 
#             cls.open_log_tree.disabled = len(valid_subdirs) == 0
#             cls.select_valid_subdir.options = valid_subdirs
            
            
#     @classmethod
#     def open_burst_dir(cls, directory):
#         CurrentBurst.init(directory)
        
#     @classmethod
#     def display(cls):
#         display(HBox([cls.path_inp, cls.set_dir, cls.select_subdir,cls.open_burst_dir_btn,]),HBox([cls.select_valid_subdir ,cls.open_log_tree]) )
        
#     @classmethod
#     def update_subdir(cls, evt):
#         cls.select_subdir.unobserve(cls.update_subdir, names=["value"])
#         cls.set_directory(os.path.relpath(os.path.join(cls.directory, cls.select_subdir.value)))
#         cls.select_subdir.observe(cls.update_subdir, names=["value"])
        
#     @classmethod
#     def init(cls):
#         cls.path_inp.value = cls.directory
#         cls.set_directory()
#         cls.set_dir.on_click(lambda btn: cls.set_directory())
#         cls.select_subdir.observe(cls.update_subdir, names=["value"])
#         cls.open_burst_dir_btn.on_click(lambda btn: cls.open_burst_dir(cls.directory))
#         cls.open_log_tree.on_click(lambda btn: cls.open_burst_dir(os.path.join(cls.directory, cls.select_valid_subdir.value, "detection","raw")))
        