from ipywidgets import HBox, Text, Label, Valid, ValueWidget
from traitlets import Float

def safe_float_convert(string):
    try:
        return float(string)
    except ValueError:
        return None

def safe_rational_convert(string):
    try:
        a_str,b_str = string.split("/")
        a = float(a_str)
        b = float(b_str)
        return a/b
    except ValueError:
        return None
    
def string_to_number(string):
    number = safe_float_convert(string)
    if number is not None:
        return number
    number = safe_rational_convert(string)
    return number

class NumericalInput(HBox, ValueWidget):
    value = Float()
    
    def __init__(self, **kwargs):
        self.text = Text()
        self.value_display = Label()
        self.valid_input = Valid(True)
        super().__init__([self.text, self.value_display, self.valid_input], **kwargs)
        self.text.observe(lambda evt: self.update_value(evt.new), names=["value"])
        self.update_value(self.text.value)
    
    def set_value(self,new_value):
        self.valid_input.value = new_value is not None
        if new_value is None:
            return
        self.value = new_value
        self.value_display.value = str(new_value)
        
    def update_value(self, string):
        if string == "":
            self.set_value(0.0)
            return
        new_value = string_to_number(string)
        self.set_value(new_value)