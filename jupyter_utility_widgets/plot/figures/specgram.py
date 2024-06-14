from matplotlib import pyplot as plt
from jupyter_utility_widgets.plot.figures.base import BasePlot
from functools import wraps


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

    def update(self, data):
        self.ax.cla()

        if data is None:
            return

        _, freqs, _, _ = self.ax.specgram(data, *self.spec_args, **self.spec_kwargs)
        self.sample_rate = freqs[-1]*2
        super().update()