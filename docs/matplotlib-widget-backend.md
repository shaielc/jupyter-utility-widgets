# Can "figures are widgets" be a matplotlib backend?

**Yes.** A backend fully controls the object `plt.figure()` hands back, and a
`Figure` subclass can also be an `ipywidgets.Box` without any name collisions.
A working reference implementation lives in
[`jupyter_utility_widgets/plot/backend.py`](../jupyter_utility_widgets/plot/backend.py);
it was verified in a real JupyterLab 4.6 session (matplotlib 3.11, ipympl 0.10,
ipywidgets 8.1).

```python
%matplotlib juw

fig, ax = plt.subplots()
ax.plot(x, np.sin(x))
VBox([FloatSlider(), fig])      # the figure itself is the child
```

## Why it works

`pyplot.figure()` ends with:

```python
manager = new_figure_manager(num, ..., FigureClass=FigureClass, **kwargs)
...
return manager.canvas.figure
```

`new_figure_manager` is supplied by the backend module. So whatever object the
backend puts at `manager.canvas.figure` is what the user gets — from
`plt.figure()`, from `plt.subplots()`, and from `plt.gcf()`. There is no
separate "what pyplot returns" hook to fight with; overriding
`new_figure_manager` is the whole mechanism.

The object still has to *be* a `Figure`, because `canvas.figure` is walked by
the draw machinery. That rules out a proxy or wrapper and points at multiple
inheritance: `class FigureWidget(Figure, Box)`.

That turns out to be unusually clean:

* **Zero public name collisions.** `set(dir(Figure)) & set(dir(Box))` minus
  dunders is empty. `Box.layout` (CSS) and matplotlib's layout engine do not
  collide — matplotlib keeps the engine in `_layout_engine` and never reads
  `.layout`.
* **Metaclass is fine.** `Figure`'s metaclass is `type`, `Box`'s is
  `MetaHasTraits`, and Python picks the more derived one.
* **`__new__` resolves to `HasDescriptors.__new__`**, which is what traitlets
  needs, because `Figure` does not define `__new__`.
* **`__repr__` resolves to `Figure.__repr__`**, which is the nicer one.

## What the backend has to do

1. Override `new_figure_manager` to instantiate the widget-figure class.
   Mix the requested `FigureClass` with the widget mixin rather than replacing
   it, so `plt.figure(FigureClass=MyFigure)` keeps working.
2. Set `figure.children = (canvas,)` after the ipympl canvas exists, so the
   Box renders the canvas.
3. Ship a `post_execute` hook. ipympl's `flush_figures` checks
   `matplotlib.get_backend()` against its own names and returns early for
   anyone else, so implicit display (a cell that just calls `plt.plot(...)`)
   needs a replacement hook.
4. Suppress the double display: a cell whose last expression is `fig` produces
   an `execute_result`, and the `post_execute` hook would then emit a second
   `display_data`. Dropping the figure from the pending list inside
   `_repr_mimebundle_` fixes it.
5. Override `FigureManager.destroy` to also `close()` the figure widget.
   `plt.close(fig)` otherwise only closes the canvas comm, leaving the figure
   in the widget registry.
6. Set `_repr_html_ = None`. `Figure._repr_html_` otherwise adds a competing
   `text/html` entry next to the widget view.

## The two real rough edges

**Pickling.** `Figure.__setstate__` does `self.__dict__ = state`, which wipes
traitlets' per-instance bookkeeping, and the comm is not picklable at all.
Both are fixable — strip the trait state in `__getstate__`, call
`setup_instance()` and merge the trait dict back in `__setstate__` — but it is
a real thing that breaks if you do the naive mixin. (Pleasant side effect once
fixed: `Figure.__setstate__` rebuilds the manager through the *current*
backend, so unpickling under this backend yields a widget figure.)

**Lifetime.** Every figure now owns a comm and sits in the widget registry
until explicitly closed. This is the same cost ipympl already pays for the
canvas, roughly doubled, and it means `plt.close()` genuinely matters.

Smaller ones: `SubFigure` is not a widget (`fig.subfigures()` returns plain
ones); the mixin is sensitive to ipywidgets' `Widget.__init__` internals across
major versions; and code that sniffs the backend name — including
`BasePlot.__init__` in this repo, which asserts `'ipympl' in
matplotlib.get_backend()` — needs updating, since the backend now reports
`juw`.

## Registration

matplotlib >= 3.9 reads the `matplotlib.backend` entry point group, so a named
backend needs only:

```toml
[project.entry-points."matplotlib.backend"]
juw = "jupyter_utility_widgets.plot.backend"
```

after which `%matplotlib juw` and `matplotlib.use("juw")` work. Without the
entry point, `%matplotlib module://jupyter_utility_widgets.plot.backend` is
equivalent.

## What this would mean for the existing widgets

`BasePlot` currently exists to bridge the gap: it is a `Box`, it creates a
figure with `plt.subplots()` under `plt.ioff()`, and it puts `fig.canvas` in
its children. Under this backend that bridging is what the backend does, so
`BasePlot` collapses to roughly

```python
class BasePlot:
    def __init__(self, nrows=1, ncols=1, **kwargs):
        self.fig, axes = plt.subplots(nrows, ncols, **kwargs)
        self.axes = np.atleast_1d(axes).ravel().tolist()
```

with `self.fig` being the widget. The subclasses (`Lines`, `SpecgramPlot`) are
unaffected — they only touch `self.ax`.

Worth weighing before committing to it: the backend is global, so it changes
the meaning of `plt.figure()` for every cell in the notebook, not just for this
library's widgets. Keeping `BasePlot` as an opt-in wrapper and offering the
backend as an alternative front door is the lower-risk shape.

## Verified

* `plt.figure()`, `plt.subplots()`, `plt.gcf()`, `plt.gca()`, `savefig`,
  `plt.close`, `plt.close('all')`
* `isinstance(fig, Figure)` and `isinstance(fig, Widget)` both true
* `plt.figure(layout='constrained')` and `plt.figure(FigureClass=MyFigure)`
* nesting in `VBox`, `interact`, pickle round-trip
* in-browser: canvas renders with toolbar, slider `observe` drives
  `line.set_ydata` + `draw_idle`, and two views of the same figure stay in sync
