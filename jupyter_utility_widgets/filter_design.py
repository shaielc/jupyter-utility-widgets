from jupyter_utility_widgets.plot.filter import Filter
from ipywidgets import HBox, VBox, Dropdown, BoundedIntText, BoundedFloatText
from traitlets import Any
from scipy.signal import windows, firwin
available_windows = list(filter(lambda s: not (s.startswith("_") or s in ["get_window"]), dir(windows))) + ["manual"]
class WindowSelect(Dropdown):
    manual = Any()
    
    def __init__(self, **kwargs):
        super().__init__(options=available_windows, **kwargs)
    
    @property
    def window(self,):
        if self.value == "manual":
            return self.manual
        return getattr(windows, self.value)

class FilterDesignControls(VBox):
    value = Any()
    def __init__(self, **kwargs):
        self.window_selector = WindowSelect(description="Win")
        self.window_length = BoundedIntText(min=0, value=64, max=2**20, description="N")
        self.cutoff_input = BoundedFloatText(value=0.25, min=1e-12, max=0.5, description="w0")
        self.width_input = BoundedFloatText(value=0.001, min=1e-12, max=0.5, description="w1")
        
        children= [
            self.window_selector,
            self.window_length, 
            self.cutoff_input,
            self.width_input
        ]
        super().__init__(children, **kwargs)
        
        for child in children:
            child.observe(lambda evt: self.calc_filt(),names=["value"])
    
    def calc_filt(self, ):
        self.value = firwin(
            self.window_length.value,
            self.cutoff_input.value,
            self.width_input.value,
            self.window_selector.window
        )

class FilterDesign(HBox):
    def __init__(self, **kwargs):
        self.filter_plot = Filter()
        self.design_controls = FilterDesignControls()
        children = [self.filter_plot, self.design_controls]
        super().__init__(children, **kwargs)

        self.design_controls.observe(lambda evt: self.filter_plot.update(evt.new))
