"""An experimental matplotlib backend whose ``Figure`` *is* an ipywidget.

With this backend active, ``plt.figure()`` / ``plt.subplots()`` return a
:class:`FigureWidget`, which is simultaneously a ``matplotlib.figure.Figure``
and an ``ipywidgets.Box``.  That means the object matplotlib hands back can be
dropped straight into widget layouts::

    %matplotlib juw

    fig, ax = plt.subplots()
    ax.plot(x, y)
    VBox([FloatSlider(), fig])      # <- the figure itself, no wrapper

Activate it either through the entry point registered in ``pyproject.toml``::

    %matplotlib juw

or, without relying on the entry point::

    %matplotlib module://jupyter_utility_widgets.plot.backend

It is built on top of ipympl: the canvas, toolbar and event plumbing are
ipympl's, unmodified.  The only thing this backend adds is the figure-level
widget wrapper.  See ``docs/matplotlib-widget-backend.md`` for the design
notes and the known rough edges.
"""
from IPython import get_ipython
from IPython.display import display
from ipympl.backend_nbagg import Canvas, FigureManager, _Backend_ipympl
from ipywidgets import Box
from matplotlib import is_interactive
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import _Backend
from matplotlib.figure import Figure


class FigureWidget(Figure, Box):
    """A ``Figure`` that is also a ``Box`` holding its own ipympl canvas.

    ``Figure`` and ``Box`` share no public attribute names, so the two APIs
    coexist without shadowing each other.  Only the dunders need care, and
    they are handled below.
    """

    def __init__(self, *args, **kwargs):
        # traitlets/comm setup has to happen before Figure.__init__, so that
        # trait assignment works while the figure is being built.
        Box.__init__(self)
        Figure.__init__(self, *args, **kwargs)

    # Figure._repr_html_ would compete with the widget mimebundle.
    _repr_html_ = None

    def _repr_mimebundle_(self, **kwargs):
        # Displayed explicitly, so the post_execute hook must not show it again.
        if self in _BackendWidgetFigure._to_show:
            _BackendWidgetFigure._to_show.remove(self)
        return Box._repr_mimebundle_(self, **kwargs)

    # The comm and the traitlets bookkeeping cannot be pickled; drop them on
    # the way out and rebuild them on the way in, so figures stay picklable.
    _WIDGET_STATE_KEYS = (
        "_trait_values",
        "_trait_notifiers",
        "_trait_validators",
        "_cross_validation_lock",
        "comm",
    )

    def __getstate__(self):
        state = Figure.__getstate__(self)
        for key in self._WIDGET_STATE_KEYS:
            state.pop(key, None)
        return state

    def __setstate__(self, state):
        # traitlets normally does setup_instance() from __new__, which pickle
        # bypasses; and Figure.__setstate__ assigns self.__dict__ wholesale,
        # which would drop the trait bookkeeping again -> merge it back in.
        self.setup_instance()
        Box.__init__(self)
        Figure.__setstate__(self, {**state, **vars(self)})


_widget_figure_classes = {}


def as_widget_figure(figure_class):
    """Return ``figure_class`` mixed with the widget behaviour.

    Keeps ``plt.figure(FigureClass=...)`` working for third-party Figure
    subclasses instead of silently ignoring the argument.
    """
    if issubclass(figure_class, Box):
        return figure_class
    if figure_class is Figure:
        return FigureWidget
    if figure_class not in _widget_figure_classes:
        _widget_figure_classes[figure_class] = type(
            f"Widget{figure_class.__name__}", (figure_class, FigureWidget), {}
        )
    return _widget_figure_classes[figure_class]


class WidgetFigureManager(FigureManager):
    def show(self):
        if self.canvas._closed:
            self.canvas._closed = False
            display(self.canvas.figure)
        else:
            self.canvas.draw_idle()

    def destroy(self):
        figure = self.canvas.figure
        super().destroy()
        if isinstance(figure, Box):
            # plt.close() only closes the canvas widget; close ours as well,
            # otherwise the figure lingers in the widget registry.
            figure.close()


@_Backend.export
class _BackendWidgetFigure(_Backend_ipympl):
    FigureCanvas = Canvas
    FigureManager = WidgetFigureManager

    _to_show = []
    _draw_called = False

    @staticmethod
    def new_figure_manager(num, *args, FigureClass=Figure, **kwargs):
        figure = as_widget_figure(FigureClass)(*args, **kwargs)
        return _BackendWidgetFigure.new_figure_manager_given_figure(num, figure)

    @staticmethod
    def new_figure_manager_given_figure(num, figure):
        canvas = Canvas(figure)
        manager = WidgetFigureManager(canvas, num)
        if isinstance(figure, Box):
            figure.children = (canvas,)

        def _destroy(event):
            canvas.mpl_disconnect(cid)
            Gcf.destroy(manager)

        cid = canvas.mpl_connect("close_event", _destroy)

        if is_interactive():
            _BackendWidgetFigure._to_show.append(figure)
            _BackendWidgetFigure._draw_called = True
            canvas.draw_idle()
        return manager

    @staticmethod
    def show(block=None):
        manager = Gcf.get_active()
        if manager is None:
            return
        figure = manager.canvas.figure
        display(figure if isinstance(figure, Box) else manager.canvas)
        if figure in _BackendWidgetFigure._to_show:
            _BackendWidgetFigure._to_show.remove(figure)


def flush_figures():
    """``post_execute`` hook that auto-displays new figures, as ipympl does.

    ipympl's own hook bails out unless ``matplotlib.get_backend()`` is one of
    its own names, so this backend needs its own.
    """
    if not _BackendWidgetFigure._draw_called:
        return
    try:
        active = {manager.canvas.figure for manager in Gcf.get_all_fig_managers()}
        for figure in [f for f in _BackendWidgetFigure._to_show if f in active]:
            display(figure if isinstance(figure, Box) else figure.canvas)
    finally:
        _BackendWidgetFigure._to_show = []
        _BackendWidgetFigure._draw_called = False


_ipython = get_ipython()
if _ipython is not None:
    _ipython.events.register("post_execute", flush_figures)
