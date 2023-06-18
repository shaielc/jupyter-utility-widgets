from jupyter_utility_widgets.plot.filter import Filter
from jupyter_utility_widgets.utility.numpy_parameter_converter import NumpyFunctionUIFactory, SKIP_PARAMETER
from ipywidgets import HBox, VBox, Dropdown, BoundedIntText, BoundedFloatText
from traitlets import Any, Unicode
from scipy.signal import windows, firwin
available_windows = list(filter(lambda s: not (s.startswith("_") or s in ["get_window"]), dir(windows))) + ["manual"]
class WindowSelect(VBox):
    manual = Any()
    value = Any()
    
    def __init__(self, **kwargs):
        self.window_func_selector = Dropdown(options=available_windows, **kwargs)
        self.extras = VBox([])

        super().__init__(children=[self.window_func_selector, self.extras])

        self.window_func_selector.observe(lambda evt: self._handle_window_change(evt.new), names=["value"])
        self._handle_window_change(self.window_func_selector.value)

    def _handle_window_change(self, window_name):
        self.set_extras(window_name)
        self.update_value()
    
    def set_extras(self, window_name):
        func = getattr(windows, window_name)
        parameters, parameters_types = NumpyFunctionUIFactory.get_parameter_types(func)
        parameters_types['M'] = SKIP_PARAMETER
        parameters_types["sym"] = SKIP_PARAMETER

        for child in self.extras.children:
            child.unobserve_all()

        self.extras.children = NumpyFunctionUIFactory.construct_widgets(parameters, parameters_types)
        
        for child in self.extras.children:
            child.observe(lambda evt: self.update_value(), names=["value"])

    def update_value(self,):
        self.value = self.window
    
    @property
    def window(self,):
        window_name = self.window_func_selector.value
        if  window_name == "manual":
            return self.manual
        return (window_name,) + tuple(child.value for child in self.extras.children)

class FilterDesignControls(VBox):
    value = Any()
    def __init__(self, **kwargs):
        self.window_selector = WindowSelect(description="Win")
        self.window_length = BoundedIntText(min=0, value=64, max=2**20, description="N")
        self.cutoff_input = BoundedFloatText(value=0.25, min=1e-12, max=1, description="w0")
        
        children= [
            self.window_length, 
            self.cutoff_input,
            self.window_selector,
        ]
        super().__init__(children, **kwargs)

        for child in children:
            child.observe(lambda evt: self.calc_filt(),names=["value"])
        
        self.calc_filt()
    
    def calc_filt(self, ):
        self.value = firwin(
            self.window_length.value,
            self.cutoff_input.value,
            window=self.window_selector.value
        )

class FilterDesign(HBox):
    def __init__(self, **kwargs):
        self.filter_plot = Filter()
        self.design_controls = FilterDesignControls()
        children = [self.filter_plot, self.design_controls]
        super().__init__(children, **kwargs)

        self.design_controls.observe(lambda evt: self.filter_plot.update(evt.new), names=["value"])
        self.filter_plot.update(self.design_controls.value)
