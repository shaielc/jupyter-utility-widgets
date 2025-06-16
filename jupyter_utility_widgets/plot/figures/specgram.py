from matplotlib import pyplot as plt
from jupyter_utility_widgets.plot.figures.base import BasePlot
from functools import wraps


class SpecgramPlot(BasePlot):
    def __init__(self, nrows=1, ncols=1, **kwargs):
        self.spec_args = tuple()
        self.spec_kwargs = {}
        self.sample_rate = 1
        self._image = None
        super().__init__(nrows, ncols, **kwargs)

    @wraps(plt.specgram)
    def set_params(self, *args, **kwargs):
        self.spec_args = args
        self.spec_kwargs = kwargs

    def update(self, data):
        if data is None:
            return
        if self._image is not None:
            self._image.remove()

        _, freqs, time, self._image = self.ax.specgram(data, *self.spec_args, **self.spec_kwargs)
        self.sample_rate = (freqs[1] - freqs[0])*len(freqs)
        self.ax.set_xlim([time[0] - (time[1] - time[0]), time[-1] + (time[1] - time[0])])
        super().update()