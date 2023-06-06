from jupyter_utility_widgets.plot.figures.lines import Lines
from ipywidgets import Box
try:
    from scipy.signal import freqz
except ImportError:
    freqz = None

if freqz is None:
    raise ImportError("Missing scipy, it is required to use in with the filter module")

class Filter(Box):
    FREQ_RESPONSE = "H"
    def __init__(self, **kwargs):
        self.plot = Lines({self.FREQ_RESPONSE})
        children = [self.plot]
        super().__init__(children, **kwargs)
        
        self.plot.ax.set_title("H(z)")
    
    def update(self, data):
        f,h =freqz(data, 1)
        self.plot.update({self.FREQ_RESPONSE: (f,abs(h))})