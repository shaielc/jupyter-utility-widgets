from matplotlib import pyplot as plt
from jupyter_utility_widgets.plot.figures.base import BasePlot
from ipywidgets import HBox
from functools import wraps
from matplotlib.widgets import SpanSelector


class SpecgramPlot(BasePlot):
    def __init__(self, nrows=1, ncols=1, **kwargs):
        self.spec_args = tuple()
        self.spec_kwargs = {}
        self.sample_rate = 1
        super().__init__(nrows, ncols, **kwargs)

    @wraps(plt.specgram)
    def set_params(self, *args, **kwargs):
        self.spec_args = args
        self.spec_kwargs = kwargs

    @property
    def ax(self,):
        return self.axes[0]

    def update(self, data):
        self.ax.cla()

        if data is None:
            return

        _, freqs,_,_ = self.ax.specgram(data, *self.spec_args, **self.spec_kwargs)
        self.sample_rate = freqs[-1]*2


class SpectrogramExaminer(HBox):
    def __init__(self, **kwargs):
        self.full_spec = SpecgramPlot()
        self.zoom_spec = SpecgramPlot()
        
        self.selector = SpanSelector(
            ax=self.full_spec.ax,
            onselect=self.on_select,
            direction="horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:gray"),
            interactive=True,
            drag_from_anywhere=True,
        )

        super().__init__(children=[self.full_spec, self.zoom_spec], **kwargs)
        self.data = None

    def on_select(self, tmin, tmax):
        xmin, xmax = int(tmin * self.full_spec.sample_rate), int(tmax * self.full_spec.sample_rate)
        self.zoom_spec.update(self.data[max(0,xmin):min(len(self.data),xmax)])

    @wraps(plt.specgram)
    def set_params(self, *args, **kwargs):
        self.full_spec.set_params(*args, **kwargs)
        self.zoom_spec.set_params(*args, **kwargs)

    def update(self, data):
        self.data = data
        self.full_spec.update(data)
        self.selector.new_axes(self.full_spec.ax)
        self.zoom_spec.update(None)
