from jupyter_utility_widgets.plot.figures.specgram import SpecgramPlot
from matplotlib.widgets import SpanSelector
from ipywidgets import HBox
from matplotlib import pyplot as plt
from functools import wraps
from traitlets import Tuple, Int

class SpectrogramExaminer(HBox):
    current_span = Tuple(Int(), Int())
    def __init__(self, keep_selection=False, **kwargs):
        """Widget that displays a signal in a spectrogram with the ability to zoom

        Parameters
        ----------
        keep_selection : bool, optional
            If set to true keeps the previous selection after update, by default False
        """
        self.full_spec = SpecgramPlot()
        self.zoom_spec = SpecgramPlot()
        self.keep_selection = keep_selection
        self.last_time_span = None

        # FIX: https://github.com/matplotlib/matplotlib/issues/10009
        self.span_ax = self.full_spec.fig.add_subplot(1,1,1)
        self.span_ax.patch.set_visible(False)
        self.span_ax.axis("off")
        
        self.selector = SpanSelector(
            ax=self.span_ax,
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
        self.last_time_span = (tmin, tmax)
        xmin, xmax = int(tmin * self.full_spec.sample_rate), int(tmax * self.full_spec.sample_rate)
        self.current_span = xmin, xmax
        self.zoom_spec.update(self.data[max(0,xmin):min(len(self.data),xmax)])
    
    @wraps(plt.specgram)
    def set_params(self, *args, **kwargs):
        self.full_spec.set_params(*args, **kwargs)
        self.zoom_spec.set_params(*args, **kwargs)

    def update(self, data):
        self.data = data
        self.full_spec.update(data)
        self.zoom_spec.update(None)

        if not self.keep_selection:
            self.span_ax.patches[0].remove()
            self.selector.new_axes(self.span_ax)
        elif self.last_time_span != None:
            self.on_select(*self.last_time_span)
        
        self.span_ax.set_xlim(*self.full_spec.ax.get_xlim())
