from ipywidgets import HBox, Button, IntText
from traitlets import Int, TraitError, link, observe, validate

class IndexSelector(HBox):
    value = Int()

    def __init__(self, length=1,loop=False, **kwargs):
        self._length = length
        self.loop = loop

        self.left_button = Button(icon="arrow-left")
        self.text_input = IntText()
        self.right_button = Button(icon="arrow-right")
        super().__init__([self.left_button, self.text_input, self.right_button], **kwargs)

        link((self, "value"), (self.text_input, "value"))
        self.left_button.on_click(lambda button: self.step(-1))
        self.right_button.on_click(lambda button: self.step(1))

    def step(self, amount):
        if self.loop or (self.value >= -amount and self.value < self.length - amount):
            self.value = self.value + amount

    @property
    def length(self, ):
        return self._length
    
    @length.setter
    def length(self, value):
        self._length = value
        
        if self.loop:
            self.value = self.value % self._length

        elif self.value >= self._length:
            self.value = self._length

    @validate("value")
    def validate_value(self, proposal):
        if not self.loop and proposal["value"] >= self.length:
            raise TraitError("List index out of range")
        return proposal["value"] % self.length