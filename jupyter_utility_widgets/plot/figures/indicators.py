from traitlets import HasTraits, Float
from matplotlib.axes import Axes

# TODO: change lines to follow this pattern?
class VerticalIndicator(HasTraits):
    value = Float(default_value=None, allow_none=True)
    def __init__(self, ax: Axes = None):
        self.ax = ax
        self.indicator = None
    
    def clear(self, ):
        if self.indicator is None:
            return
        self.indicator.remove()
        self.indicator = None
    
    def attach(self, ax):
        self.ax = ax
        
        self.clear()
        if self.value is None:
            return
        self._create_line()
    
    def _create_line(self):
        if self.indicator is not None:
            self.clear()
        self.indicator = self.ax.axvline(self.value, c="k", ls="--")
    
    def update(self, x):
        self.value = x

        if self.indicator is None:
            self._create_line()
            return
        self.indicator.set_xdata([x,x])
        
        # TODO: make this better:
        self.ax.figure.canvas.draw_idle()
        self.ax.figure.canvas.flush_events()