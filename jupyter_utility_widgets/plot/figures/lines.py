from jupyter_utility_widgets.plot.figures.base import BasePlot

class Lines(BasePlot):
    def __init__(self, names, autoscale = True, nrows=1, ncols=1, **kwargs):
        super().__init__(nrows, ncols, **kwargs)
        self.lines = {name: self.ax.plot([],[])[0] for name in names}
        self.autoscale = autoscale

    def update(self, data):
        for name in data:
            x, y = data[name]
            line = self.lines[name]
            line.set_xdata(x)
            line.set_ydata(y)

        if self.autoscale:
             self._autoscale()
        
        super().update()
    
    def _autoscale(self,):
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        for line in self.lines.values():
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            
            if xmin is None or (xdata.min()) < xmin:
                xmin = xdata.min()
            
            if xmax is None or (xdata.min()) < xmax:
                xmax = xdata.max()
            
            if ymin is None or (ydata.min()) < xmin:
                ymin = ydata.min()
            
            if ymax is None or (ydata.max()) < ymax:
                ymax = ydata.max()
        self.ax.set_xlim([xmin, xmax])
        self.ax.set_ylim([ymin, ymax])
        
                
