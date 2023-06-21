from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import List
import matplotlib
from ipywidgets import Box
from abc import abstractmethod

class BasePlot(Box):
    @property
    def ax(self,):
        return self.axes[0]
    
    def __init__(self, nrows=1,ncols=1, **kwargs):
        self.fig: Figure
        self.axes: List[Axes]
        if not 'ipympl' in matplotlib.get_backend():
            raise ValueError('Cannot use plot widgets without ipympl active.\n did you run %matplotlib widget?')
        
        plt.ioff()
        self.fig, axes = plt.subplots(nrows,ncols)
        plt.ion()
        
        if nrows*ncols == 1:
            self.axes = [axes]
        else:
            self.axes = list(axes.reshape(-1,))
        children = [self.fig.canvas]

        super().__init__(children, **kwargs)


    def update(self, data=None):
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
    
    @abstractmethod
    def select(self, x=None, y=None, z=None):
        raise NotImplementedError()


