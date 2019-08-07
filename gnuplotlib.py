#!/usr/bin/python

r'''a gnuplot-based plotting backend for numpy

* SYNOPSIS

    import numpy      as np
    import gnuplotlib as gp

    x = np.arange(101) - 50
    gp.plot(x**2)
    [ basic parabola plot pops up ]


    g1 = gp.gnuplotlib(title = 'Parabola with error bars',
                       _with = 'xyerrorbars')
    g1.plot( x**2 * 10, np.abs(x)/10, np.abs(x)*5,
             legend    = 'Parabola',
             tuplesize = 4 )
    [ parabola with x,y errobars pops up in a new window ]


    x,y = np.ogrid[-10:11,-10:11]
    gp.plot( x**2 + y**2,
             title     = 'Heat map',
             unset     = 'grid',
             cmds      = 'set view map',
             _with     = 'image',
             tuplesize = 3)
    [ Heat map pops up where first parabola used to be ]


    theta = np.linspace(0, 6*np.pi, 200)
    z     = np.linspace(0, 5,       200)
    g2 = gp.gnuplotlib(_3d = True)
    g2.plot( np.cos(theta),
             np.vstack((np.sin(theta), -np.sin(theta))),
             z )
    [ Two 3D spirals together in a new window ]


    x = np.arange(1000)
    gp.plot( (x*x, dict(histogram=1,            binwidth=10000)),
             (x*x, dict(histogram='cumulative', y2=1)))
    [ A density and cumulative histogram of x^2 are plotted together ]



* DESCRIPTION

This module allows numpy data to be plotted using Gnuplot as a backend. As much
as was possible, this module acts as a passive pass-through to Gnuplot, thus
making available the full power and flexibility of the Gnuplot backend. Gnuplot
is described in great detail at its upstream website: http://www.gnuplot.info

gnuplotlib has an object-oriented interface (via class gnuplotlib) and a few
global class-less functions (plot(), plot3d(), plotimage()). Each instance of
class gnuplotlib has a separate gnuplot process and a plot window. If multiple
simultaneous plot windows are desired, create a separate class gnuplotlib object
for each.

The global functions reuse a single global gnuplotlib instance, so each such
invocation rewrites over the previous gnuplot window.

The object-oriented interface is used like this:

    import gnuplotlib as gp
    g = gp.gnuplotlib(plot_options)
    g.plot( curve, curve, .... )

The global functions consolidate this into a single call:

    import gnuplotlib as gp
    gp.plot( curve, curve, ...., plot_options_and_default_curve_options )

Each plot contains multiple curves (different datasets to be plotted). Plot
generation is controlled by two sets of options:

- Plot options: parameters that affect the whole plot, like the title of the
  plot, the axis labels, the extents, 2D/3D selection, etc. These are passed
  into the gnuplotlib constructor or appear as keyword arguments in a global
  plot() call. All the plot options are described below in "Plot options".

- Curve options: parameters that affect only a single curve. These are given as
  a python dict after all the numpy arrays in a curve. Each is described below
  in "Curve options".

Each curve is passed in as a python tuple (data, data, data, ..., curve_options)
where each "data" is a numpy array, and "curve_options" is a dict. If we're
plotting a single curve, the tuple can be inlined. Thus the following are all
equivalent ways of making the same plot:

    import gnuplotlib as gp
    import numpy      as np
    x = np.arange(10)
    y = x*x

    # Global function. Non-inlined curves
    gp.plot( (x,y, dict(_with = 'lines')), title = 'parabola')

    # Global function. Inlined curves (possible because we have only one curve)
    gp.plot( x,y, _with = 'lines', title = 'parabola' )

    # Object-oriented function. Non-inlined curves.
    p1 = gp.gnuplotlib(title = 'parabola')
    p1.plot((x,y, dict(_with = 'lines')),)

    # Object-oriented function. Inlined curves.
    p2 = gp.gnuplotlib(title = 'parabola')
    p2.plot(x,y, _with = 'lines')

If multiple curves are to be drawn on the same plot, then each 'curve' must live
in a separate tuple:

    import gnuplotlib as gp
    import numpy      as np
    x = np.arange(10)
    y = x*x
    z = x*x*x

    # Global function
    gp.plot( (x,y, dict(_with = 'lines', legend = 'parabola')),
             (x,z, dict(_with = 'lines', legend = 'cubic')),
             title = 'parabola and cubic')

    # Object-oriented function
    p = gp.gnuplotlib(title = 'parabola and cubic')
    p.plot((x,y, dict(_with = 'lines', legend = 'parabola')),
           (x,z, dict(_with = 'lines', legend = 'cubic')),)

Another way to plot multiple curves is to use broadcasting; described below.

The plot_and_default_curve_options passed to the global plot(...) calls are
keyword arguments. The curve options present here are used as defaults for each
curve; these defaults can be overriden in each curve, as desired. For instance:

    gp.plot( (x1,y1),
             (x2,y2, dict(_with = 'points')),
             _with = 'lines')

would plot the first curve with lines, but the second with points.

plot3d(...) is equivalent to plot(..., _3d=True)

plotimage(...) is equivalent to plot(..., _with='image', tuplesize=3)

** Data arguments

The 'curve' arguments in the plot(...) argument list represent the actual data
being plotted. Each output data point is a tuple (set of values, not a python
"tuple") whose size varies depending on what is being plotted. For example if
we're making a simple 2D x-y plot, each tuple has 2 values. If we're making a 3D
plot with each point having variable size and color, each tuple has 5 values:
(x,y,z,size,color). When passing data to plot(), each tuple element is passed
separately. So if we want to plot N 2D points we pass the two numpy arrays of
shape (N,):

    gp.plot( x,y )

By default, gnuplotlib assumes tuplesize==2 when plotting in 2D and tuplesize==3
when plotting in 3D. If we're doing anything else, then the 'tuplesize' curve
option MUST be passed in:

    gp.plot( x,y,z,size,color,
             tuplesize = 5,
             _3d = True,
             _with = 'points ps variable palette' )

This is required because you may be using implicit domains (see below) and/or
broadcasting.

Broadcasting (https://docs.scipy.org/doc/numpy/user/basics.broadcasting.html) is
fully supported, so multiple curves can be plotted by stacking data inside the
passed-in arrays. Broadcasting works across curve options also, so things like
curve labels and styles can also be stacked inside arrays:

    th    = np.linspace(0, 6*np.pi, 200)
    z     = np.linspace(0, 5,       200)
    size  = 0.5 + np.abs(np.cos(th))
    color = np.sin(2*th)


    # without broadcasting:
    gp.plot3d( (  np.cos(th),  np.sin(th),
                 z, size, color,
                 dict(legend = 'spiral 1') ),

               ( -np.cos(th), -np.sin(th),
                 z, size, color,
                 dict(legend = 'spiral 2') ),

               tuplesize = 5,
               title = 'double helix',
               _with = 'points pointsize variable pointtype 7 palette' )


    # identical plot using broadcasting:
    gp.plot3d( ( np.cos(th) * np.array([[1,-1]]).T,
                 np.sin(th) * np.array([[1,-1]]).T,
                 z, size, color,
                 dict( legend = np.array(('spiral 1', 'spiral 2')))),

               tuplesize = 5,
               title = 'double helix',
               _with = 'points pointsize variable pointtype 7 palette' )

This is a 3D plot with variable size and color. There are 5 values in the tuple,
which we specify. The first 2 arrays have shape (2,N); all the other arrays have
shape (N,). Thus the broadcasting rules generate 2 distinct curves, with varying
values for x,y and identical values for z, size and color. We label the curves
differently by passing an array for the 'legend' curve option. This array
contains strings, and is broadcast like everything else.

*** Negative tuplesize

If we have all the data elements in a single array, plotting them is a bit
awkward. Here're two ways:

    xy = .... # Array of shape (N,2). Each slice is (x,y)

    gp.plot(xy[:,0], xy[:,1])

    gp.plot(*xy.T)

The *xy.T version is concise, but is only possible if we're plotting one curve:
python syntax doesn't allow any arguments after and *-expanded tuple. With more
than one curve you're left with the first version, which is really verbose,
especially with a large tuplesize. gnuplotlib handles this case with a
shorthand: negative tuplesize. The above can be represented nicely like this:

    gp.plot(xy, tuplesize = -2)

This means that each point has 2 values, but that instead of reading each one in
a separate array, we have ONE array, with the values in the last dimension.

*** Implicit domains

gnuplotlib looks for tuplesize different arrays for each curve. It is common for
the first few arrays to be predictable by gnuplotlib, and in those cases it's a
chore to require for the user to pass those in. Thus, if there are fewer than
tuplesize arrays available, gnuplotlib will try to use an implicit domain. This
happens if we are EXACTLY 1 or 2 arrays short (usually when making 2D and 3D
plots respectively).

If exactly 1 dimension is missing, gnuplotlib will use np.arange(N) as the
domain: we plot the given values in a row, one after another. Thus

    gp.plot(np.array([1,5,3,4,4]))

is equivalent to

    gp.plot(np.arange(5), np.array([1,5,3,4,4]) )

Only 1 array was given, but the default tuplesize is 2, so we are 1 array short.

If we are exactly 2 arrays short, gnuplotlib will use a 2D grid as a domain.
Example:

    xy = np.arange(21*21).reshape(21*21)
    gp.plot( xy, _with = 'points', _3d=True)

Here the only given array has dimensions (21,21). This is a 3D plot, so we are
exactly 2 arrays short. Thus, gnuplotlib generates an implicit domain,
corresponding to a 21-by-21 grid. Note that in all other cases, each curve takes
in tuplesize 1-dimensional arrays, while here it takes tuplesize-2 2-dimensional
arrays.

Also, note that while the DEFAULT tuplesize depends on whether we're making a 3D
plot, once a tuplesize is given, the logic doesn't care if a 3D plot is being
made. It can make sense to have a 2D implicit domain when making 2D plots. For
example, one can be plotting a color map:

    x,y = np.ogrid[-10:11,-10:11]
    gp.plot( x**2 + y**2,
             title     = 'Heat map',
             set       = 'view map',
             _with     = 'image',
             tuplesize = 3)

Also note that the 'tuplesize' curve option is independent of implicit domains.
This option specifies not how many data arrays we have, but how many values
represent each data point. For example, if we want a 2D line plot with varying
colors plotted with an implicit domain, set tuplesize=3 as before (x,y,color),
but pass in only 2 arrays (y, color).

** Symbolic equations

Gnuplot can plot both data and equations. This module exists largely for the
data-plotting case, but sometimes it can be useful to plot equations together
with some data. This is supported by the 'equation...' plot options. These plot
options are either a string (for a single equation) or a list/tuple containing
multiple strings for multiple equations. An example:

    import numpy as np
    import numpy.random as nr
    import numpy.linalg
    import gnuplotlib as gp

    # generate data
    x     = np.arange(100)
    c     = np.array([1, 1800, -100, 0.8])   # coefficients
    m     = x[:, np.newaxis] ** np.arange(4) # 1, x, x**2, ...
    noise = 1e4 * nr.random(x.shape)
    y     = np.dot( m, c) + noise            # polynomial corrupted by noise

    c_fit = np.dot(numpy.linalg.pinv(m), y)  # coefficients obtained by a curve fit

    # generate a string that describes the curve-fitted equation
    fit_equation = '+'.join( '{} * {}'.format(c,m) for c,m in zip( c_fit.tolist(), ('x**0','x**1','x**2','x**3')))

    # plot the data points and the fitted curve
    gp.plot(x, y, _with='points', equation = fit_equation)

Here I generated some data, performed a curve fit to it, and plotted the data
points together with the best-fitting curve. Here the best-fitting curve was
plotted by gnuplot as an equation, so gnuplot was free to choose the proper
sampling frequency. And as we zoom around the plot, the sampling frequency is
adjusted to keep things looking nice.

Note that the various styles and options set by the other options do NOT apply
to these equation plots. Instead, the string is passed to gnuplot directly, and
any styling can be applied there. For instance, to plot a parabola with thick
lines, you can issue

    gp.plot( ....., equation = 'x**2 with lines linewidth 2')

As before, see the gnuplot documentation for details. You can do fancy things:

    x   = np.arange(100, dtype=float) / 100 * np.pi * 2;
    c,s = np.cos(x), np.sin(x)

    gp.plot( c,s,
             square=1, _with='points',
             set = ('parametric', 'trange [0:2*3.14]'),
             equation = "sin(t),cos(t)" )

Here the data are points evently spaced around a unit circle. Along with these
points we plot a unit circle as a parametric equation.

** Histograms

It is possible to use gnuplot's internal histogram support, which uses gnuplot
to handle all the binning. A simple example:

    x = np.arange(1000)
    gp.plot( (x*x, dict(histogram = 'freq',       binwidth=10000)),
             (x*x, dict(histogram = 'cumulative', y2=1))

To use this, pass 'histogram = HISTOGRAM_TYPE' as a curve option. If the type is
any non-string that evaluates to True, we use the 'freq' type: a basic frequency
histogram. Otherwise, the types are whatever gnuplot supports. See the output of
'help smooth' in gnuplot. The most common types are

- freq:       frequency
- cumulative: integral of freq. Runs from 0 to N, where N is the number of samples
- cnormal:    like 'cumulative', but rescaled to run from 0 to 1

The 'binwidth' curve option specifies the size of the bins. This must match for
ALL histogram curves in a plot. If omitted, this is assumed to be 1. As usual,
the user can specify whatever styles they want using the 'with' curve option. If
omitted, you get reasonable defaults: boxes for 'freq' histograms and lines for
cumulative ones.

This only makes sense with 2D plots with tuplesize=1

** Plot persistence and blocking

As currently written, gnuplotlib does NOT block and the plot windows do NOT
persist. I.e.

- the 'plot()' functions return immediately, and the user interacts with the
  plot WHILE THE REST OF THE PYTHON PROGRAM IS RUNNING

- when the python program exits, the gnuplot process and any visible plots go
  away

If you want to write a program that just shows a plot, and exits when the user
closes the plot window, you should do any of

- add 'wait':1 to the plot options dict
- call wait() on your gnuplotlib object
- call the global gnuplotlib.wait(), if you have a global plot

Please note that it's not at all trivial to detect if a current plot window
exists. If not, this function will end up waiting forever, and the user will
need to Ctrl-C.

* OPTIONS

** Plot options

The plot options are a dictionary, passed as the keyword arguments to the global
plot() function or as the only arguments to the gnuplotlib contructor. The
supported keys of this dict are as follows:

- title

Specifies the title of the plot

- 3d

If true, a 3D plot is constructed. This changes the default tuple size from 2 to
3

- _3d

Identical to '3d'. In python, keyword argument keys cannot start with a number,
so '_3d' is accepted for that purpose. Same issue exists with with/_with

- set/unset

These take either a string of a list. If given a string, a set or unset gnuplot
command is executed with that argument. If given a list, elements of that list
are set/unset separately. Example:

    plot(..., set='grid', unset=['xtics', 'ytics])
    [ turns on the grid, turns off the x and y axis tics ]

- with

If no 'with' curve option is given, use this as a default. See the description
of the 'with' curve option for more detail

- _with

Identical to 'with'. In python 'with' is a reserved word so it is illegal to use
it as a keyword arg key, so '_with' exists as an alias. Same issue exists with
3d/_3d

- square, square_xy

If true, these request a square aspect ratio. For 3D plots, square_xy plots with
a square aspect ratio in x and y, but scales z. Using either of these in 3D
requires Gnuplot >= 4.4

- {x,y,y2,z,cb}{min,max,range,inv}

If given, these set the extents of the plot window for the requested axes.
Either min/max or range can be given but not both. min/max are numerical values.
'*range' is a string 'min:max' with either one allowed to be omitted; it can
also be a [min,max] tuple or list. '*inv' is a boolean that reverses this axis.
If the bounds are known, this can also be accomplished by setting max < min.
Passing in both max < min AND inv also results in a reversed axis.

If no information about a range is given, it is not touched: the previous zoom
settings are preserved.

The y2 axis is the secondary y-axis that is enabled by the 'y2' curve option.
The 'cb' axis represents the color axis, used when color-coded plots are being
generated

- xlabel, ylabel, zlabel, y2label

These specify axis labels

- rgbimage

This should be set to a path containing an image file on disk. The data is then
plotted on top of this image, which is very useful for annotations, computer
vision, etc. Note that when plotting data, the y axis usually points up, but
when looking at images, the y axis of the pixel coordinates points down instead.
Thus, if the y axis extents aren't given and an rgbimage IS specified,
gnuplotlib will flip the y axis to make things look reasonable. If any y-axis
ranges are given, however (with any of the ymin,ymax,yrange,yinv plot options),
then it is up to the user to flip the axis, if that's what they want.

- equation, equation_above, equation_below

These options allows equations represented as formula strings to be plotted
along with data passed in as numpy arrays. These can be a string (for a single
equation) or an array/tuple of strings (for multiple equations). See the
"Symbolic equations" section above.

By default, the equations are plotted BEFORE other data, so the data plotted
later may obscure some of the equation. Depending on what we're doing, this may
or may not be what we want. To plot the equations AFTER other data, use
'equation_above' instead of 'equation'. The 'equation_below' option is a synonym
for 'equation'

- hardcopy

Instead of drawing a plot on screen, plot into a file instead. The output
filename is the value associated with this key. The output format is inferred
from the filename. Currently only eps, ps, pdf, png, svg, gp are supported with
some default sets of options. This option is simply a shorthand for the
'terminal' and 'output' options. If the defaults provided by the 'hardcopy'
option are insufficient, use 'terminal' and 'output' manually. Example:

    plot(..., hardcopy="plot.pdf")
    [ Plots into that file ]

Note that the ".gp" format is special. Instead of asking gnuplot to make a plot
using a specific terminal, writing to "xxx.gp" will create a self-plotting data
file that is visualized with gnuplot.

- terminal

Selects the gnuplot terminal (backend). This determines how Gnuplot generates
its output. Common terminals are 'x11', 'qt', 'pdf', 'dumb' and so on. See the
Gnuplot docs for all the details.

- output

Sets the plot output file. You generally only need to set this if you're
generating a hardcopy, such as a PDF.

There are several gnuplot terminals that are known (at this time) to be
interactive: "x11", "qt" and so on. For these no "output" setting is desired.
For noninteractive terminals ("pdf", "dumb" and so on) the output will go to the
file defined here. If this plot option isn't defined or set to the empty string,
the output will be redirected to the standard output of the python process
calling gnuplotlib.

    >>> gp.plot( np.linspace(-5,5,30)**2,
    ...          unset='grid', terminal='dumb 80 40' )

    25 A-+---------+-----------+-----------+----------+-----------+---------A-+
       *           +           +           +          +           +        *  +
       |*                                                                  *  |
       |*                                                                 *   |
       | *                                                                *   |
       | A                                                               A    |
       |  *                                                              *    |
    20 +-+ *                                                            *   +-+
       |   *                                                            *     |
       |    A                                                          A      |
       |     *                                                         *      |
       |     *                                                        *       |
       |      *                                                       *       |
       |      A                                                      A        |
    15 +-+     *                                                    *       +-+
       |       *                                                    *         |
       |        *                                                  *          |
       |        A                                                 A           |
       |         *                                               *            |
       |          *                                              *            |
       |           A                                            A             |
    10 +-+          *                                          *            +-+
       |            *                                         *               |
       |             A                                       A                |
       |              *                                     *                 |
       |               *                                    *                 |
       |                A                                  A                  |
       |                 *                                *                   |
     5 +-+                A                              A                  +-+
       |                   *                           **                     |
       |                    A**                       A                       |
       |                                             *                        |
       |                       A*                  *A                         |
       |                         A*              *A                           |
       +           +           +   A**     +  *A*     +           +           +
     0 +-+---------+-----------+------A*A**A*A--------+-----------+---------+-+
       0           5           10          15         20          25          30

- cmds

Arbitrary extra commands to pass to gnuplot before the plots are created. These
are passed directly to gnuplot, without any validation. The value is either a
string of a list of strings, one per command

- dump

Used for debugging. If true, writes out the gnuplot commands to STDOUT instead
of writing to a gnuplot process. Useful to see what commands would be sent to
gnuplot. This is a dry run. Note that this dump will contain binary data unless
ascii-only plotting is enabled (see below). This is also useful to generate
gnuplot scripts since the dumped output can be sent to gnuplot later, manually
if desired. Look at the 'notest' option for a less verbose dump.

- log

Used for debugging. If true, writes out the gnuplot commands and various
progress logs to STDERR in addition to writing to a gnuplot process. This is NOT
a dry run: data is sent to gnuplot AND to the log. Useful for debugging I/O
issues. Note that this log will contain binary data unless ascii-only plotting
is enabled (see below)

- ascii

If set, ASCII data is passed to gnuplot instead of binary data. Binary is the
default because it is much more efficient (and thus faster). Usually there's no
reason to touch this option. Binary input works for most plots, but not for all
of them. An example where binary plotting doesn't work is 'with labels', and
gnuplotlib will use ascii there regardless of this setting

- notest

Don't check for failure after each gnuplot command. And don't test all the plot
options before creating the plot. This is generally only useful for debugging or
for more sparse 'dump' functionality.

- wait

When we're done asking gnuplot to make a plot, we ask gnuplot to tell us when
the user closes the interactive plot window that popped up. The python process
will block until the user is done looking at the data. This can also be achieved
by calling the wait() gnuplotlib method or the global gnuplotlib.wait()
function.

** Curve options

The curve options describe details of specific curves. They are in a dict, whose
keys are as follows:

- legend

Specifies the legend label for this curve

- with

Specifies the style for this curve. The value is passed to gnuplot using its
'with' keyword, so valid values are whatever gnuplot supports. Read the gnuplot
documentation for the 'with' keyword for more information

- _with

Identical to 'with'. In python 'with' is a reserved word so it is illegal to use
it as a keyword arg key, so '_with' exists as an alias

- y2

If true, requests that this curve be plotted on the y2 axis instead of the main y axis

- tuplesize

Described in the "Data arguments" section above. Specifies how many values
represent each data point. For 2D plots this defaults to 2; for 3D plots this
defaults to 3. These defaults are correct for simple plots. For each curve we
expect to get tuplesize separate arrays of data unless any of these are true

  - If tuplesize < 0, we expect to get a single numpy array, with each data
    tuple in the last dimension. See the "Negative tuplesize" section above for
    detail.

  - If we receive fewer than tuplesize arrays, we may be using "Implicit
    domains". See the "Implicit domains" section above for detail.

- using

Overrides the 'using' directive we pass to gnuplot. No error checking is
performed, and the string is passed to gnuplot verbatim. This option is very
rarely needed. The most common usage is to apply a function to an implicit
domain. For instance, this basic command plots a line (linearly increasing
values) against a linearly-increasing line number::

    gp.plot(np.arange(100))

We can plot the same values against the square-root of the line number to get a
parabola:

    gp.plot(np.arange(100), using='(sqrt($1)):2')

- histogram

If given and if it evaluates to True, gnuplot will plot the histogram of this
data instead of the data itself. See the "Histograms" section above for more
details. If this curve option is a string, it's expected to be one of the
smoothing style gnuplot understands (see 'help smooth'). Otherwise we assume the
most common style: a frequency histogram. This only makes sense with 2D plots
and tuplesize=1

- binwidth

Used for the histogram support. See the "Histograms" section above for more
details. This sets the width of the histogram bins. If omitted, the width is set
to 1.

* INTERFACE

** class gnuplotlib

A gnuplotlib object abstracts a gnuplot process and a plot window. Invocation:

    import gnuplotlib as gp
    g = gp.gnuplotlib(plot_options)
    g.plot( curve, curve, .... )

The plot options are passed into the constructor; the curve options and the data
are passed into the plot() method. One advantage of making plots this way is
that there's a gnuplot process associated with each gnuplotlib instance, so as
long as the object exists, the plot will be interactive. Calling 'g.plot()'
multiple times reuses the plot window instead of creating a new one.

** global plot(...)

The convenience plotting routine in gnuplotlib. Invocation:

    import gnuplotlib as gp
    gp.plot( curve, curve, ...., plot_and_default_curve_options )

Each 'plot()' call reuses the same window.

** global plot3d(...)

Generates 3D plots. Shorthand for 'plot(..., _3d=True)'

** global plotimage(...)

Generates an image plot. Shorthand for 'plot(..., _with='image', tuplesize=3)'

** global wait(...)

Blocks until the user closes the interactive plot window. Useful for python
applications that want blocking plotting behavior. This can also be achieved by
calling the wait() gnuplotlib method or by adding'wait':1 to the plot options
dict

* RECIPES

Some different plots appear here. A longer set of demos is given in demos.py.

** 2D plotting

If we're plotting y-values sequentially (implicit domain), all you need is

    plot(y)

If we also have a corresponding x domain, we can plot y vs. x with

    plot(x, y)

*** Simple style control

To change line thickness:

    plot(x,y, _with='lines linewidth 3')

To change point size and point type:

    gp.plot(x,y, _with='points pointtype 4 pointsize 8')

Everything (like _with) feeds directly into Gnuplot, so look at the Gnuplot docs
to know how to change thicknesses, styles and such.

*** Errorbars

To plot errorbars that show y +- 1, plotted with an implicit domain

    plot( y, np.ones(y.shape), _with = 'yerrorbars', tuplesize = 3 )

Same with an explicit x domain:

    plot( x, y, np.ones(y.shape), _with = 'yerrorbars', tuplesize = 3 )

Symmetric errorbars on both x and y. x +- 1, y +- 2:

    plot( x, y, np.ones(x.shape), 2*np.ones(y.shape), _with = 'xyerrorbars', tuplesize = 4 )

To plot asymmetric errorbars that show the range y-1 to y+2 (note that here you
must specify the actual errorbar-end positions, NOT just their deviations from
the center; this is how Gnuplot does it)

    plot( y, y - np.ones(y.shape), y + 2*np.ones(y.shape),
         _with = 'yerrorbars', tuplesize = 4 )

*** More multi-value styles

Plotting with variable-size circles (size given in plot units, requires Gnuplot >= 4.4)

    plot(x, y, radii,
         _with = 'circles', tuplesize = 3)

Plotting with an variably-sized arbitrary point type (size given in multiples of
the "default" point size)

    plot(x, y, sizes,
         _with = 'points pointtype 7 pointsize variable', tuplesize = 3 )

Color-coded points

    plot(x, y, colors,
         _with = 'points palette', tuplesize = 3 )

Variable-size AND color-coded circles. A Gnuplot (4.4.0) quirk makes it
necessary to specify the color range here

    plot(x, y, radii, colors,
         cbmin = mincolor, cbmax = maxcolor,
         _with = 'circles palette', tuplesize = 4 )


Broadcasting example: the Conchoids of de Sluze. The whole family of curves is
generated all at once, and plotted all at once with broadcasting. Broadcasting
is also used to generate the labels. Generally these would be strings, but here
just printing the numerical value of the parameter is sufficient.

    theta = np.linspace(0, 2*np.pi, 1000)  # dim=(  1000,)
    a     = np.arange(-4,3)[:, np.newaxis] # dim=(7,1)

    gp.plot( theta,
             1./np.cos(theta) + a*np.cos(theta), # broadcasted. dim=(7,1000)

             _with  = 'lines',
             set    = 'polar',
             square = True,
             yrange = [-5,5],
             legend = a.ravel() )

** 3D plotting

General style control works identically for 3D plots as in 2D plots.

To plot a set of 3D points, with a square aspect ratio (squareness requires
Gnuplot >= 4.4):

    plot3d(x, y, z, square = 1)

If xy is a 2D array, we can plot it as a height map on an implicit domain

    plot3d(xy)

Ellipse and sphere plotted together, using broadcasting:

    th   = np.linspace(0,        np.pi*2, 30)
    ph   = np.linspace(-np.pi/2, np.pi*2, 30)[:,np.newaxis]

    x_3d = (np.cos(ph) * np.cos(th))          .ravel()
    y_3d = (np.cos(ph) * np.sin(th))          .ravel()
    z_3d = (np.sin(ph) * np.ones( th.shape )) .ravel()

    gp.plot3d( (x_3d * np.array([[1,2]]).T,
                y_3d * np.array([[1,2]]).T,
                z_3d,
                { 'legend': np.array(('sphere', 'ellipse'))}),

               title  = 'sphere, ellipse',
               square = True,
               _with  = 'points')

Image arrays plots can be plotted as a heat map:

    x,y = np.ogrid[-10:11,-10:11]
    gp.plot( x**2 + y**2,
             title     = 'Heat map',
             set       = 'view map',
             _with     = 'image',
             tuplesize = 3)

Data plotted on top of an existing image. Useful for image annotations.

    gp.plot( x, y,
             title    = 'Points on top of an image',
             _with    = 'points',
             square   = 1,
             rgbimage = 'image.png')

** Hardcopies

To send any plot to a file, instead of to the screen, one can simply do

    plot(x, y,
         hardcopy = 'output.pdf')

The 'hardcopy' option is a shorthand for the 'terminal' and 'output' options (in
all cases except when writing a .gp file; see below). If more control is
desired, the latter can be used. For example to generate a PDF of a particular
size with a particular font size for the text, one can do

    plot(x, y,
         terminal = 'pdfcairo solid color font ",10" size 11in,8.5in',
         output   = 'output.pdf')

This command is equivalent to the 'hardcopy' shorthand used previously, but the
fonts and sizes can be changed.

If we write to a ".gp" file:

    plot(x, y,
         hardcopy = 'data.gp')

then instead of running gnuplot, we create a self-plotting file. gnuplot is
invoked when we execute that file.

'''



from __future__ import print_function

import subprocess
import time
import sys
import os
import re
import select
import numbers
import numpy as np
import numpysane as nps

# setup.py assumes the version is a simple string in '' quotes
__version__ = '0.30'

# note that 'with' is both a known plot and curve option
knownPlotOptions = frozenset(('dump', 'ascii', 'log', 'notest', 'wait',

                              '3d',
                              'cmds', 'set', 'unset', 'square', 'square_xy', 'title',
                              'hardcopy', 'terminal', 'output',
                              'with', 'rgbimage',
                              'equation', 'equation_above', 'equation_below',
                              'xmax',  'xmin',  'xrange',  'xinv',  'xlabel',
                              'y2max', 'y2min', 'y2range', 'y2inv', 'y2label',
                              'ymax',  'ymin',  'yrange',  'yinv',  'ylabel',
                              'zmax',  'zmin',  'zrange',  'zinv',  'zlabel',
                              'cbmin', 'cbmax', 'cbrange'))

knownCurveOptions = frozenset(('legend', 'y2', 'with', 'tuplesize', 'using',
                               'histogram', 'binwidth'))

knownInteractiveTerminals = frozenset(('x11', 'wxt', 'qt', 'aquaterm'))

# when testing plots with ASCII i/o, this is the unit of test data
testdataunit_ascii = 10



def _getGnuplotFeatures():

    # Be careful talking to gnuplot here. If you use a tty then gnuplot messes
    # with the tty settings where it should NOT. For example it turns on the
    # local echo. So make sure to not use a tty. Furthermore, I turn off the
    # DISPLAY. I'm not actually plotting anything, so a DISPLAY can try to
    # X-forward and be really slow pointlessly

    # I pass in the current environment, but with DISPLAY turned off
    env = os.environ.copy()
    env['DISPLAY'] = ''

    # first, I run 'gnuplot --help' to extract all the cmdline options as features
    try:
        helpstring = subprocess.check_output(['gnuplot', '--help'],
                                             stderr=subprocess.STDOUT,
                                             env=env).decode()
    except FileNotFoundError:
        print("Couldn't run gnuplot. Is it installed? Is it findable in the PATH?",
              file=sys.stderr)
        raise

    features = set( re.findall(r'--([a-zA-Z0-9_]+)', helpstring) )


    # then I try to set a square aspect ratio for 3D to see if it works
    equal_3d_works = True
    try:
        out = subprocess.check_output(('gnuplot', '-e', "set view equal"),
                                      stderr=subprocess.STDOUT,
                                      env=env).decode()
        if re.search("(undefined variable)|(unrecognized option)", out, re.I):
            equal_3d_works = False
    except:
        equal_3d_works = False

    if equal_3d_works:
        features.add('equal_3d')

    return frozenset(features)


features = _getGnuplotFeatures()





def _dictDeUnderscore(d):
    r'''Takes a dict, and renames all keys that start with an '_' to not contain that
    anymore. This is done because some keys are illegal as kwargs (notably
    'with' and '3d'), so the user passes in '_with' and '_3d', which ARE legal

    '''

    d2 = {}
    for key in d:
        if isinstance(key, (str, bytes)) and key[0] == '_':
            d2[key[1:]] = d[key]
        else:
            d2[key] = d[key]

    return d2

class GnuplotlibError(Exception):
    def __init__(self, err): self.err = err
    def __str__(self):       return self.err



def _data_dump_only(plotOptions):
    '''Returns True if we're dumping a script, NOT actually running gnuplot'''
    return \
        plotOptions.get('dump') or \
        plotOptions.get('terminal') == 'gp' or \
        re.match(".*\.gp$",plotOptions.get('hardcopy',''))


class gnuplotlib:

    def __init__(self, **plotOptions):

        # some defaults
        self.plotOptions      = _dictDeUnderscore(plotOptions)
        self._dumpPipe        = None
        self.t0               = time.time()
        self.checkpoint_stuck = False
        self.sync_count       = 1

        self._plotOptionsCmds = self._getPlotOptionsCmds()

        if _data_dump_only(self.plotOptions):
            self.gnuplotProcess = None
        else:
            # if we already have a gnuplot process, reset it. Otherwise make a new
            # one
            if hasattr(self, 'gnuplotProcess') and self.gnuplotProcess:
                self._printGnuplotPipe( "reset\nset output\n" )
                self._checkpoint()
            else:
                self.gnuplotProcess = None
                self._startgnuplot()
                self._logEvent("_startgnuplot() finished")

        if self.plotOptions.get('terminal') != 'gp':
            self._safelyWriteToPipe(self._plotOptionsCmds)


    def _startgnuplot(self):

        self._logEvent("_startgnuplot()")

        cmd = ['gnuplot']

        try:
            self.fdDupSTDOUT = os.dup(sys.stdout.fileno())
        except:
            self.fdDupSTDOUT = None


        # I need this to make fdDupSTDOUT available to the child gnuplot. This
        # would happen by default, but in python3 I need to do this extra thing
        # for some reason. And it's a new thing that didn't exist in python2, so
        # I need to explicitly allow this to fail in python2
        try:
            os.set_inheritable(self.fdDupSTDOUT, True)
        except AttributeError:
            pass

        self.gnuplotProcess = \
            subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,

                             # required to "autoflush" writes
                             bufsize=0,

                             # I need this to make fdDupSTDOUT available to the
                             # child gnuplot. close_fds=False was default in
                             # python2, but was changed in python3
                             close_fds = False,

                             # This was helpful in python3 to implicitly
                             # encode() strings, but it broke the
                             # select()/read() mechanism: select() would
                             # look at the OS file descriptor, but read()
                             # would look at some buffer, so you'd get into
                             # a situation where
                             #
                             # - data was read from the OS into a buffer, and is available to be read()
                             # - select() blocks waiting for MORE data
                             #
                             # I guess I leave this off and manully
                             # encode/decode everything

                             #encoding = 'utf-8',
            )

        # save the default terminal
        self._safelyWriteToPipe("set terminal push", 'terminal')


    def _getPlotOptionsCmds(self):

        for option in self.plotOptions:
            if not option in knownPlotOptions:
                raise GnuplotlibError(option + ' is not a valid plot option')


        # set some defaults
        # plot with lines and points by default
        if not 'with' in self.plotOptions:
            self.plotOptions['with'] = 'linespoints'

        # make sure I'm not passed invalid combinations of options
        if self.plotOptions.get('3d'):
            if 'y2min' in self.plotOptions or 'y2max' in self.plotOptions:
                raise GnuplotlibError("'3d' does not make sense with 'y2'...")

            if not 'equal_3d' in features and \
               ( self.plotOptions.get('square_xy') or self.plotOptions.get('square') ):

                sys.stderr.write("Your gnuplot doesn't support square aspect ratios for 3D plots, so I'm ignoring that\n")
                if 'square_xy' in self.plotOptions: del self.plotOptions['square_xy']
                if 'square'    in self.plotOptions: del self.plotOptions['square'   ]
        else:
            if self.plotOptions.get('square_xy'):
                raise GnuplotlibError("'square_xy' only makes sense with '3d'")



        # grid on by default
        cmds = ['set grid']

        # send all set/unset as is
        for setunset in ('set', 'unset'):
            if setunset in self.plotOptions:
                if isinstance(self.plotOptions[setunset], (list, tuple)):
                    cmds += [ setunset + ' ' + setting for setting in self.plotOptions[setunset] ]
                else:
                    cmds.append(setunset + ' ' + self.plotOptions[setunset])

        # set the plot bounds
        for axis in ('x', 'y', 'y2', 'z', 'cb'):

            # set the curve labels
            if not axis == 'cb':
                if axis + 'label' in self.plotOptions:
                    cmds.append('set {axis}label "{label}"'.format(axis = axis,
                                                                   label = self.plotOptions[axis + 'label']))

            # I deal with range bounds here. These can be given for the various
            # axes by variables (W-axis here; replace W with x, y, z, etc):
            #
            #   Wmin, Wmax, Winv, Wrange
            #
            # Wrange is mutually exclusive with Wmin and Wmax. Winv turns
            # reverses the direction of the axis. This can also be achieved by
            # passing in Wmin>Wmax or Wrange[0]>Wrange[1]. If this is done then
            # Winv has no effect, i.e. setting Wmin>Wmax AND Winv results in a
            # flipped axis.

            # This axis was set up with the 'set' plot option, so I don't touch
            # it
            if any ( re.match(" *set +{}range[\s=]".format(axis), s) for s in cmds ):
                continue

            # images generally have the origin at the top-left instead of the
            # bottom-left, so given nothing else, I flip the y axis
            if 'rgbimage' in self.plotOptions and \
               axis == 'y' and \
               not any ( ('y'+what) in self.plotOptions \
                         for what in ('min','max','range','inv')):
                cmds.append("set yrange [:] reverse")
                continue

            opt_min   = self.plotOptions.get( axis + 'min'   )
            opt_max   = self.plotOptions.get( axis + 'max'   )
            opt_range = self.plotOptions.get( axis + 'range' )
            opt_inv   = self.plotOptions.get( axis + 'inv'   )

            if (opt_min is not None or opt_max is not None) and opt_range is not None:
                raise GnuplotlibError("{0}min/{0}max and {0}range are mutually exclusive".format(axis))

            # if we have a range, copy it to min/max and just work with those
            if opt_range is not None:
                if not isinstance(opt_range, (list, tuple)):
                    opt_range = [ None if x == '*' else float(x) for x in opt_range.split(':')]
                if len(opt_range) != 2:
                    raise GnuplotlibError('{}range should have exactly 2 elements'.format(axis))
                opt_min,opt_max = opt_range
                opt_range = None

            # apply the axis inversion. It's only needed if we're given both
            # bounds and they aren't flipped
            if opt_inv:
                if opt_min is not None and opt_max is not None and opt_min < opt_max:
                    opt_min,opt_max = opt_max,opt_min

            cmds.append( "set {}range [{}:{}] {}reverse".
                         format(axis,
                                '*' if opt_min is None else opt_min,
                                '*' if opt_max is None else opt_max,
                                '' if opt_inv else 'no'))



        # set the title
        if 'title' in self.plotOptions:
            cmds.append('set title "' + self.plotOptions['title'] + '"')


        # handle a requested square aspect ratio
        # set a square aspect ratio. Gnuplot does this differently for 2D and 3D plots
        if self.plotOptions.get('3d'):
            if self.plotOptions.get('square'):
                cmds.append("set view equal xyz")
            elif self.plotOptions.get('square_xy'):
                cmds.append("set view equal xy")
        else:
            if self.plotOptions.get('square'):
                cmds.append("set size ratio -1")

        # handle 'hardcopy'. This simply ties in to 'output' and 'terminal', handled
        # later
        if 'hardcopy' in self.plotOptions:
            # 'hardcopy' is simply a shorthand for 'terminal' and 'output', so they
            # can't exist together
            if 'terminal' in self.plotOptions or 'output' in self.plotOptions:
                raise GnuplotlibError(
                    """The 'hardcopy' option can't coexist with either 'terminal' or 'output'.  If the
defaults are acceptable, use 'hardcopy' only, otherwise use 'terminal' and
'output' to get more control""")

            outputfile = self.plotOptions['hardcopy']
            m = re.search(r'\.(eps|ps|pdf|png|svg|gp)$', outputfile)
            if not m:
                raise GnuplotlibError("Only .eps, .ps, .pdf, .png, .svg and .gp hardcopy output supported")

            outputfileType = m.group(1)

            terminalOpts = { 'eps': 'postscript noenhanced solid color eps',
                             'ps':  'postscript noenhanced solid color landscape 10',
                             'pdf': 'pdf noenhanced solid color font ",10" size 11in,8.5in',
                             'png': 'png noenhanced size 1280,1024',
                             'svg': 'svg noenhanced solid',
                             'gp':  'gp'}

            self.plotOptions['terminal'] = terminalOpts[outputfileType]
            self.plotOptions['output']   = outputfile

        if 'terminal' in self.plotOptions:
            if self.plotOptions['terminal'] in knownInteractiveTerminals:
                # known interactive terminal
                if 'output' in self.plotOptions and self.plotOptions['output'] != '':
                    sys.stderr.write("Warning: requested a known-interactive gnuplot terminal AND an output file. Is this REALLY what you want?\n")

            if self.plotOptions['terminal'] == 'gp':
                self.plotOptions['dump'  ] = 1
                self.plotOptions['notest'] = 1

        # add the extra global options
        if 'cmds' in self.plotOptions:
            # if there's a single cmds option, put it into a 1-element list to
            # make the processing work
            if isinstance(self.plotOptions['cmds'], (list, tuple)):
                cmds += self.plotOptions['cmds']
            else:
                cmds.append(self.plotOptions['cmds'])

        return cmds



    def __del__(self):
        if hasattr(self, 'gnuplotProcess') and self.gnuplotProcess:

            try:
                self.gnuplotProcess.terminate()
            except:
                pass

            try:
                self.gnuplotProcess.wait()
            except:
                pass
            self.gnuplotProcess = None

            if self.fdDupSTDOUT is not None:
                os.close(self.fdDupSTDOUT)
                self.fdDupSTDOUT = None






    def _safelyWriteToPipe(self, input, flags=''):

        def barfOnDisallowedCommands(line):
            # I use STDERR as the backchannel, so I don't allow any "set print"
            # commands, since those can disable that
            if re.match(r'''(?: .*;)?       # optionally wait for a semicolon
                            \s*
                            set\s+print\b''',
                        line, re.X):
                raise GnuplotlibError("Please don't 'set print' since I use gnuplot's STDERR for error detection")

            if re.match(r'''(?: .*;)?       # optionally wait for a semicolon
                            \s*
                             print\b''',
                        line, re.X):
                 raise GnuplotlibError("Please don't ask gnuplot to 'print' anything since this can confuse my error detection")


            if re.match(r'''(?: .*;)?       # optionally wait for a semicolon
                            \s*
                            set\s+terminal\b''',
                        line, re.X) and flags != 'terminal':
                raise GnuplotlibError("Please do not 'set terminal' manually. Use the 'terminal' plot option instead")

            if re.match(r'''(?: .*;)?       # optionally wait for a semicolon
                            \s*
                            set\s+output\b''',
                        line, re.X) and not re.match('output', flags):
                raise GnuplotlibError("Please do not 'set output' manually. Use the 'output' plot option instead")




        if not isinstance(input, (list,tuple)):
            input = (input,)

        for cmd in input:
            barfOnDisallowedCommands(cmd)

            self._printGnuplotPipe( cmd + '\n' )

            errorMessage, warnings = self._checkpoint('printwarnings')
            if errorMessage:
                barfmsg = "Gnuplot error: '\n{}\n' while sending cmd '{}'\n".format(errorMessage, cmd)
                if warnings:
                    barfmsg += "Warnings:\n" + str(warnings)
                raise GnuplotlibError(barfmsg)




    def _gnuplotStdin(self):
        if self.gnuplotProcess:
            return self.gnuplotProcess.stdin

        # In python2 I just return stdout. But the python3 people have no idea
        # what they're doing. The normal pipe return by Popen is a FileIO, so I
        # can ONLY write bytes to it; if I write a string to it, it barfs. So I
        # normally need to do the encode/decode dance. But sys.stdout is a
        # TextIOWrapper, which means that I must write STRINGS and it'll barf if
        # I write bytes. I can apparently reach inside and grab the
        # corresponding FileIO object to make it work like the pipe, so I do
        # that
        # debug dump. I return stdout
        if self._dumpPipe:
            try:
                return self._dumpPipe.buffer.raw
            except:
                return self._dumpPipe

        try:
            return sys.stdout.buffer.raw
        except:
            return sys.stdout

    def _printGnuplotPipe(self, string):

        self._gnuplotStdin().write( string.encode() )
        self._logEvent("Sent to child process {} bytes ==========\n{}=========================".
                       format(len(string), string))


    # I test the plot command by making a dummy plot with the test command.
    def _testPlotcmd(self, cmd, data):

        if self.plotOptions.get('notest'):
            return

        # I don't actually want to see the plot, I just want to make sure that
        # no errors are thrown. I thus send the output to /dev/null. Note that I
        # never actually read stdout, so if this test plot goes to the default
        # stdout output, then eventually the buffer fills up and gnuplot blocks.
        # So keep it going to /dev/null, or make sure to read the test plot from
        # stdout
        self._printGnuplotPipe( "set output '/dev/null'\n" )
        self._printGnuplotPipe( "set terminal dumb\n" )

        # I send a test plot command. Gnuplot implicitly uses && if multiple
        # commands are present on the same line. Thus if I see the post-plot print
        # in the output, I know the plot command succeeded
        self._printGnuplotPipe( cmd + "\n" )
        self._printGnuplotPipe( data )

        checkpointMessage,warnings = self._checkpoint('ignore_known_test_failures')
        if checkpointMessage:
            # There's a checkpoint message. I explicitly ignored and threw away all
            # errors that are allowed to occur during a test. Anything leftover
            # implies a plot failure.
            barfmsg = "Gnuplot error: '\n{}\n' while sending plotcmd '{}'\n".format(checkpointMessage, cmd)
            if warnings:
                barfmsg += "Warnings:\n" + "\n".join(warnings)
            raise GnuplotlibError(barfmsg)

        # select the default terminal in case that's what we want
        self._safelyWriteToPipe("set terminal pop; set terminal push", 'terminal')


    # syncronizes the child and parent processes. After _checkpoint() returns, I
    # know that I've read all the data from the child. Extra data that represents
    # errors is returned. Warnings are explicitly stripped out
    def _checkpoint(self, flags=''):

        if _data_dump_only(self.plotOptions):
            # There is no child process. There's nothing to checkpoint
            return None, None

        # I have no way of knowing if the child process has sent its error data
        # yet. It may be that an error has already occurred, but the message hasn't
        # yet arrived. I thus print out a checkpoint message and keep reading the
        # child's STDERR pipe until I get that message back. Any errors would have
        # been printed before this
        waitforever                = re.search('waitforever',                flags)
        final                      = re.search('final',                      flags)
        printwarnings              = re.search('printwarnings',              flags)
        ignore_known_test_failures = re.search('ignore_known_test_failures', flags)

        # I always checkpoint() before exiting. Even if notest==1. Without this
        # 'set terminal dumb' plots don't end up rendering anything: we kill the
        # process before it has time to make the plot
        if self.plotOptions.get('notest') and not waitforever and not final and not printwarnings:
            return None, None

        checkpoint = "gpsync{}xxx".format(self.sync_count)
        self.sync_count += 1

        self._printGnuplotPipe( 'print "{}"\n'.format(checkpoint) )

        # if no error pipe exists, we can't check for errors, so we're done.
        # Usually happens if(we're dumping)
        if not self.gnuplotProcess or not self.gnuplotProcess.stderr:
            return '',[]

        fromerr       = ''
        while not fromerr.endswith(checkpoint):
            # if no data received in 5 seconds, the gnuplot process is stuck. This
            # usually happens if the gnuplot process is not in a command mode, but in
            # a data-receiving mode. I'm careful to avoid this situation, but bugs in
            # this module and/or in gnuplot itself can make this happen

            self._logEvent("Trying to read from gnuplot")

            rlist,wlist,xlist = select.select([self.gnuplotProcess.stderr],[], [],
                                              None if waitforever else 15)

            if rlist:
                # read a byte. I'd like to read "as many bytes as are
                # available", but I don't know how to this in a very portable
                # way (I just know there will be windows users complaining if I
                # simply do a non-blocking read). Very little data will be
                # coming in anyway, so doing this a byte at a time is an
                # irrelevant inefficiency
                byte = self.gnuplotProcess.stderr.read(1).decode()
                fromerr += byte
                if byte is not None and len(byte):
                    self._logEvent("Read byte '{}' ({}) from gnuplot child process".format(byte,
                                                                                           hex(ord(byte))))
                else:
                    self._logEvent("read() returned no data")
            else:
                self._logEvent("Gnuplot read timed out")
                self.checkpoint_stuck = True

                raise GnuplotlibError(
                    r'''Gnuplot process no longer responding. This is likely a bug in gnuplotlib
and/or gnuplot itself. Please report this as a gnuplotlib bug''')

        fromerr = re.search(r'\s*(.*?)\s*{}$'.format(checkpoint), fromerr, re.M + re.S).group(1)

        warningre = re.compile(r'^.*(?:warning:\s*(.*?)\s*$)\n?', re.M + re.I)
        warnings  = warningre.findall(fromerr)

        if printwarnings:
            for w in warnings:
                sys.stderr.write("Gnuplot warning: {}\n".format(w))


        # I've now read all the data up-to the checkpoint. Strip out all the warnings
        fromerr = warningre.sub('',fromerr)

        # if asked, ignore and get rid of all the errors known to happen during
        # plot-command testing. These include
        #
        # 1. "invalid command" errors caused by the test data being sent to gnuplot
        #    as a command. The plot command itself will never be invalid, so this
        #    doesn't actually mask out any errors
        #
        # 2. "invalid range" and "Terminal canvas area too small to hold plot"
        #    errors caused by the data or labels being out of bounds. The point
        #    of the plot-command testing is to make sure the command is valid,
        #    so any out-of-boundedness of the test data is irrelevant
        #
        # 3. image grid complaints
        if ignore_known_test_failures:

            r = re.compile(r'''^gnuplot>\s*(?:{}|e\b).*$                  # report of the actual invalid command
                               \n^\s+\^\s*$                               # ^ mark pointing to where the error happened
                               \n^.*invalid\s+command.*$'''               # actual 'invalid command' complaint
                           .format(testdataunit_ascii),
                           re.X + re.M)
            fromerr = r.sub('', fromerr)


            # ignore a simple 'invalid range' error observed when, say only the
            # xmin bound is set and all the data is below it
            r = re.compile(r'''^gnuplot>\s*plot.*$                        # the test plot command
                               \n^\s+\^\s*$                               # ^ mark pointing to where the error happened
                               \n^.*range\s*is\s*invalid.*$''',           # actual 'invalid range' complaint
                           re.X + re.M)
            fromerr = r.sub('', fromerr)

            # fancier plots show a different 'invalid range' error. Observed when xmin
            # > xmax (inverted x axis) and when there's out-of-bounds data
            r = re.compile(r'''^gnuplot>\s*plot.*$                        # the test plot command
                               \n^\s+\^\s*$                               # ^ mark pointing to where the error happened
                               \n^.*all\s*points.*undefined.*$''',        # actual 'invalid range' complaint
                           re.X + re.M)
            fromerr = r.sub('', fromerr)

            # Newer gnuplot sometimes says 'x_min should not equal x_max!' when
            # complaining about ranges. Ignore those here
            r = re.compile(r'^.*_min should not equal .*_max!.*$',        # actual 'invalid range' complaint
                           re.M)
            fromerr = r.sub('', fromerr)

            # Labels or titles that are too long can complain about stuff being
            # too small to hold plot
            r = re.compile(r'''^.*too small to hold plot.*$''',
                           re.M)
            fromerr = r.sub('', fromerr)
            r = re.compile(r'''^.*Check plot boundary.*$''',
                           re.M)
            fromerr = r.sub('', fromerr)

            # 'with image' plots can complain about an uninteresting domain. Exact error:
            # GNUPLOT (plot_image):  Image grid must be at least 4 points (2 x 2).
            r = re.compile(r'^.*Image grid must be at least.*$',
                           re.X + re.M)
            fromerr = r.sub('', fromerr)

        fromerr = fromerr.strip()

        return fromerr, warnings


    def _logEvent(self, event):

        # only log when asked
        if not self.plotOptions.get('log'):
            return

        t = time.time() - self.t0

        print( "==== PID {} at t={:.4f}: {}".format(self.gnuplotProcess.pid if self.gnuplotProcess else '(none)',
                                                   t, event),
               file=sys.stderr )


    def _plotCurveInASCII(self, curve):
        '''Should this curve be plotted in ascii?

        Mostly this just looks at the plot-level setting. But 'with labels' is
        an exception: such curves are ascii-only

        '''
        return \
            self.plotOptions.get('ascii') or \
            ( curve.get('with') and re.match(" *labels\\b", curve['with'], re.I) )


    def _sendCurve(self, curve):

        pipe = self._gnuplotStdin()

        if self._plotCurveInASCII(curve):

            if curve.get('matrix'):
                np.savetxt(pipe,
                           nps.glue(*curve['_data'], axis=-2).astype(np.float64,copy=False),
                           '%s')
                pipe.write(b"\ne\n")
            else:
                # Previously I was doing this:
                #     np.savetxt( pipe,
                #                 nps.glue(*curve['_data'], axis=-2).transpose().astype(np.float64,copy=False),
                #                 '%s' )
                #
                # That works in most cases, but sometimes we have disparate data
                # types in each column, so glueing the components together into
                # a single array is impossible (most notably when plotting 'with
                # labels' at some particular locations). Thus I loop myself
                # here. This is slow, but if we're plotting in ascii, we
                # probably aren't looking for maximal performance here. And
                # 'with labels' isn't super common
                Ncurves = len(curve['_data'])
                def write_element(e):
                    r'''Writes value to pipe. Encloses strings in "". This is required to support
labels with spaces in them

                    '''
                    if type(e) is np.string_ or type(e) is np.str_:
                        pipe.write(b'"')
                        pipe.write(str(e).encode())
                        pipe.write(b'"')
                    else:
                        pipe.write(str(e).encode())

                for i in range(curve['_data'][0].shape[-1]):
                    for j in range(Ncurves-1):
                        write_element(curve['_data'][j][i])
                        pipe.write(b' ')
                    write_element(curve['_data'][Ncurves-1][i])
                    pipe.write(b'\n')


                pipe.write(b"e\n")

        else:
            nps.mv(nps.cat(*curve['_data']), 0, -1).astype(np.float64,copy=False).tofile(pipe)

        self._logEvent("Sent the data to child process")


    def _getPlotCmd(self, curves):

        def optioncmd(curve):
            cmd = ''

            if 'legend' in curve: cmd += 'title "{}" '.format(curve['legend'])
            else:                 cmd += 'notitle '

            # use the given per-curve 'with' style if there is one. Otherwise fall
            # back on the global
            _with = curve['with'] if 'with' in curve else self.plotOptions['with']

            if _with:           cmd += "with {} ".format(_with)
            if curve.get('y2'): cmd += "axes x1y2 "

            return cmd


        def binaryFormatcmd(curve):
            # I make 2 formats: one real, and another to test the plot cmd, in case it
            # fails
            tuplesize = curve['tuplesize']

            fmt = ''
            if curve.get('matrix'):
                fmt += 'binary array=({},{})'.format(curve['_data'][0].shape[-1],
                                                     curve['_data'][0].shape[-2])
                fmt += ' format="' + ('%double' * (tuplesize-2)) + '"'
            else:
                fmt += 'binary record=' + str(curve['_data'][0].shape[-1])
                fmt += ' format="' + ('%double' * tuplesize) + '"'


            # when doing fancy things, gnuplot can get confused if I don't
            # explicitly tell it the tuplesize. It has its own implicit-tuples
            # logic that I don't want kicking in. For instance, 3d matrix plots
            # with image do not work in binary without 'using':
            using_Ncolumns = tuplesize
            if curve.get('matrix'):
                using_Ncolumns -= 2

            using = curve.get('using')
            if using is None:
                using = ':'.join(str(x+1) for x in range(using_Ncolumns))
            fmt += ' using ' + using

            # to test the plot I plot a single record
            fmtTest = fmt
            fmtTest = re.sub('record=\d+',        'record=1',     fmtTest)
            fmtTest = re.sub('array=\(\d+,\d+\)', 'array=(2, 2)', fmtTest)

            return fmt,fmtTest


        def getTestDataLen(curve):
            # assuming sizeof(double)==8
            if curve.get('matrix'):
                return 8 * 2*2*(curve['tuplesize']-2)
            return 8 * curve['tuplesize']






        basecmd = ''

        # if anything is to be plotted on the y2 axis, set it up
        if any( curve.get('y2') for curve in curves ):
            if self.plotOptions.get('3d'):
                raise GnuplotlibError("3d plots don't have a y2 axis")

            basecmd += "set ytics nomirror\n"
            basecmd += "set y2tics\n"

        binwidth = None
        for curve in curves:
            if curve.get('histogram'):
                binwidth = 1 # default. Used if nothing else is specified
                if curve.get('binwidth'):
                    binwidth = curve['binwidth']
                    break
        if binwidth is not None:
            basecmd += \
                "set boxwidth {w}\nhistbin(x) = {w} * floor(0.5 + x/{w})\n".format(w=binwidth)

        if self.plotOptions.get('3d'): basecmd += 'splot '
        else:                          basecmd += 'plot '

        plotCurveCmdsNonDataBefore = []
        plotCurveCmdsNonDataAfter  = []
        plotCurveCmds              = []
        plotCurveCmdsMinimal       = [] # same as above, but with a single data point per plot only

        # send all pre-data equations
        def set_equation(equation, cmds):
            if equation in self.plotOptions:
                if isinstance(self.plotOptions[equation], (list, tuple)):
                    cmds += self.plotOptions[equation]
                else:
                    cmds.append(self.plotOptions[equation])

        set_equation('equation',       plotCurveCmdsNonDataBefore)
        set_equation('equation_below', plotCurveCmdsNonDataBefore)

        if 'rgbimage' in self.plotOptions:
            if not os.access     (self.plotOptions['rgbimage'], os.R_OK) or \
               not os.path.isfile(self.plotOptions['rgbimage']):
                raise GnuplotlibError("Requested image '{}' is not a readable file".format(self.plotOptions['rgbimage']))

            plotCurveCmdsNonDataBefore.append('"{0}" binary filetype=auto flipy with rgbimage title "{0}"'.format(self.plotOptions['rgbimage']))

        testData             = '' # data to make a minimal plot

        for curve in curves:
            optioncmds = optioncmd(curve)

            if not self._plotCurveInASCII(curve):
                # I get 2 formats: one real, and another to test the plot cmd, in case it
                # fails. The test command is the same, but with a minimal point count. I
                # also get the number of bytes in a single data point here
                formatFull,formatMinimal = binaryFormatcmd(curve)
                Ntestbytes_here          = getTestDataLen(curve)

                plotCurveCmds       .append( "'-' " + formatFull    + ' ' + optioncmds )
                plotCurveCmdsMinimal.append( "'-' " + formatMinimal + ' ' + optioncmds )

                # If there was an error, these whitespace commands will simply do
                # nothing. If there was no error, these are data that will be plotted in
                # some manner. I'm not actually looking at this plot so I don't care
                # what it is. Note that I'm not making assumptions about how long a
                # newline is (perl docs say it could be 0 bytes). I'm printing as many
                # spaces as the number of bytes that I need, so I'm potentially doubling
                # or even tripling the amount of needed data. This is OK, since gnuplot
                # will simply ignore the tail.
                testData += " \n" * Ntestbytes_here

            else:
                # for some things gnuplot has its own implicit-tuples logic; I want to
                # suppress this, so I explicitly tell gnuplot to use all the columns we
                # have
                using = curve.get('using')
                if using is None:
                    using = ':'.join(str(x+1) for x in range(curve['tuplesize']))
                using = ' using ' + using

                # I'm using ascii to talk to gnuplot, so the minimal and "normal" plot
                # commands are the same (point count is not in the plot command)
                matrix = ''
                if curve.get('matrix'): matrix =  'matrix'
                plotCurveCmds.append( \
                    "'-' {matrix} {using} {optioncmds}".
                        format(matrix     = matrix,
                               using      = using,
                               optioncmds = optioncmds))

                testData_curve = ''
                if curve.get('matrix'):
                    testmatrix = "{0} {0}\n" + "{0} {0}\n" + "\ne\n"
                    testData_curve = testmatrix.format(testdataunit_ascii) * (curve['tuplesize'] - 2)
                else:
                    testData_curve = ' '.join( ['{}'.format(testdataunit_ascii)] * curve['tuplesize']) + \
                    "\n" + "e\n"

                testData += testData_curve

        set_equation('equation_above', plotCurveCmdsNonDataAfter)

        # the command to make the plot and to test the plot
        cmd        =  basecmd + ','.join(plotCurveCmdsNonDataBefore + plotCurveCmds        + plotCurveCmdsNonDataAfter)
        cmdMinimal = (basecmd + ','.join(plotCurveCmdsNonDataBefore + plotCurveCmdsMinimal + plotCurveCmdsNonDataAfter)) \
            if plotCurveCmdsMinimal else cmd

        return (cmd, cmdMinimal, testData)


    def _massageAndValidateArgs(self, curves, curveOptions_base):

        # Collect all the passed data into a tuple of lists, one curve per list.
        # The input is either a bunch of numerical arrays, in which we have one
        # curve (ignoring broadcasting) or a bunch of tuples containing
        # numerical arrays, where each tuple represents a curve.
        #
        # These numerical arrays can be numpy arrays or scalars. If we see
        # scalars, we convert them to a numpy array so that everything
        # downstream can assume we have arrays

        # convert any scalars in the data list
        if len(curves):
            curves = [ np.array((c,)) if isinstance(c, numbers.Real) else c for c in curves ]
            if all(type(curve) is np.ndarray for curve in curves):
                curves = (list(curves),)
            elif all(type(curve) is tuple for curve in curves):
                # we have a list of tuples. I convert this into a list of lists, and
                # each scalar in each list becomes a numpy array
                curves = [ [ np.array((c,)) if isinstance(c, numbers.Real) else c
                             for c in curve ]
                           for curve in curves ]
            else:
                raise GnuplotlibError("all data arguments should be of type ndarray (one curve) or tuples")

        # add an options dict if there isn't one, apply the base curve
        # options to each curve
        #
        # I convert the curve definition from a list of
        #    (data, data, data, ..., {options})
        # to a dict
        #    {options, '_data': (data, data, data, ....)}
        #
        # The former is nicer as a user interface, but the latter is easier for
        # the programmer (me!) to deal with.
        #
        # Also handle tuplesize<0 by splitting the innermost dimension
        def reformat(curve):

            if type(curve[-1]) is dict:
                d     = _dictDeUnderscore(curve[-1])
                curve = curve[:-1]
            else:
                d = {}
            for k in _dictDeUnderscore(curveOptions_base):
                if k not in d:
                    d[k] = curveOptions_base[k]

            for x in curve:
                if x.size <= 0:
                    raise GnuplotlibError("Can't plot a length-0 numpy array")

            if 'tuplesize' in d and d['tuplesize'] < 0:
                if len(curve) != 1:
                    raise GnuplotlibError("tuplesize<0 means that only a single numpy array of data should be given: all data is in this array")
                d['tuplesize'] = -d['tuplesize']
                d['_data']     = list(nps.mv(curve[0], -1, 0))
            else:
                d['_data'] = list(curve)
            return d
        curves = [ reformat(curve) for curve in curves ]


        binwidth = None
        for curve in curves:

            # make sure all the curve options are valid
            for opt in curve:
                if opt == '_data':
                    continue
                if not opt in knownCurveOptions:
                    raise GnuplotlibError("'{}' not a known curve option".format(opt))

            # tuplesize is either given explicitly, or taken from the '3d' plot
            # option. 2d plots default to tuplesize=2 and 3d plots to
            # tuplesize=3. This means that the tuplesize can be omitted for
            # basic plots but MUST be given for anything fancy
            Ndata = len(curve['_data'])

            if curve.get('histogram'):

                if self.plotOptions.get('3d'):
                    raise GnuplotlibError("histograms don't make sense in 3d")
                if 'tuplesize' in curve and curve['tuplesize'] != 1:
                    raise GnuplotlibError("histograms only make sense with tuplesize=1. I'll assume this if you don't specify a tuplesize")
                curve['tuplesize'] = 1

                if 'using' in curve:
                    raise GnuplotlibError("'using' cannot be given with 'histogram'. I'll make up my own 'using' in this case")

                if type(curve['histogram']) is not str:
                    curve['histogram'] = 'freq'
                histogram_type = curve['histogram']

                curve['using'] = '(histbin($1)):(1.0) smooth ' + histogram_type

                if 'with' not in curve:
                    if re.match('freq|fnorm', histogram_type) and 'with' not in curve:
                        curve['with'] = 'boxes fill solid border lt -1'
                    else:
                        curve['with'] = 'lines'

                if 'binwidth' in curve:
                    if binwidth is not None and binwidth != curve['binwidth']:
                        raise GnuplotlibError("Histogram binwidths must all match. This is a gnuplot limitation mostly. Got: {} and {}". \
                                              format(binwidth,curve['binwidth']))
                    binwidth = curve['binwidth']

            else:
                if 'binwidth' in curve:
                    raise GnuplotlibError("'binwidth' only makes sense with 'histogram'")

            if not 'tuplesize' in curve:
                curve['tuplesize'] = 3 if self.plotOptions.get('3d') else 2

            if Ndata > curve['tuplesize']:
                raise GnuplotlibError("Got {} tuples, but the tuplesize is {}. Giving up". \
                    format(Ndata, curve['tuplesize']))

            if Ndata < curve['tuplesize']:
                # I got fewer data elements than I expected. Set up the implicit
                # domain if that makes sense

                if Ndata+1 == curve['tuplesize']:

                    # A plot is one data element short. Fill in a sequential
                    # domain 0,1,2,...
                    curve['_data'].insert(0, np.arange(curve['_data'][0].shape[-1]))

                elif Ndata+2 == curve['tuplesize']:
                    # a plot is 2 elements short. Use a grid as a domain. I simply set the
                    # 'matrix' flag and have gnuplot deal with it later
                    if self.plotOptions.get('ascii') and curve['tuplesize'] > 3:
                        raise GnuplotlibError( \
                            "Can't make more than 3-dimensional plots on a implicit 2D domain\n" + \
                            "when sending ASCII data. I don't think gnuplot supports this. Use binary data\n" + \
                            "or explicitly specify the domain\n" )

                    curve['matrix'] = True

                else:
                    raise GnuplotlibError( \
                        "plot() needed {} data arrays, but only got {}".format(curve['tuplesize'],Ndata))



            # The curve is now set up. I look at the input matrices to make sure
            # the dimensions line up

            # Make sure the domain and ranges describe the same number of data points
            dim01 = [None, None]
            for datum in curve['_data']:

                if curve.get('matrix') and datum.ndim < 2:
                    raise GnuplotlibError("Tried to plot against an implicit 2D domain, but was given less than 2D data")

                def checkdim(idim):
                    dim_here = datum.shape[-1 - idim]
                    if dim01[idim]:
                        if dim_here != dim01[idim]:
                            raise GnuplotlibError("plot() was given mismatched tuples to plot. {} vs {}". \
                                                  format(dim01[idim], dim_here))
                    else:
                        dim01[idim] = dim_here

                checkdim(0)

                if curve.get('matrix'):
                    checkdim(1)


        # broadcast through the arguments AND all the options that are arrays
        curves_flattened = []
        for curve in curves:
            ndims_input = 2 if curve.get('matrix') else 1
            prototype_onearg = tuple('n{}'.format(i) for i in range(ndims_input))
            prototype = (prototype_onearg,) * len(curve['_data'])

            # grab all option keys that have numpy arrays as values. I broadcast
            # these as well
            np_options_keys = [ k for k in curve.keys()
                                if isinstance(curve[k], np.ndarray) ]
            N_options_keys = len(np_options_keys)
            prototype_np_options = ((),) * N_options_keys

            for args in nps.broadcast_generate( prototype + prototype_np_options,
                                                curve['_data'] + list(curve[k] for k in np_options_keys)):

                # make a copy of the options
                curve_slice = dict(curve)

                # replace the data with the slice
                curve_slice['_data'] = args[:-N_options_keys] if N_options_keys else args

                for ikey in range(N_options_keys):
                    curve_slice[np_options_keys[ikey]] = args[-N_options_keys + ikey]

                curves_flattened.append( curve_slice )

        curves = curves_flattened

        return curves


    def wait(self):
        r'''Waits until the open interactive plot window is closed

        Note: it's not at all trivial to detect if a current plot window exists.
        If not, this function will end up waiting forever, and the user will
        need to Ctrl-C

        '''

        self._printGnuplotPipe('pause mouse close\n')
        self._logEvent("Waiting for data from gnuplot")
        self._checkpoint('waitforever')


    def plot(self, *curves, **curveOptions_base):
        r'''Main gnuplotlib API entry point'''

        curves = self._massageAndValidateArgs(curves, curveOptions_base)

        # I'm now ready to send the plot command. If the plot command fails,
        # I'll get an error message; if it succeeds, gnuplot will sit there
        # waiting for data. I don't want to have a timeout waiting for the error
        # message, so I try to run the plot command to see if it works. I make a
        # dummy plot into the 'dumb' terminal, and then _checkpoint() for
        # errors. To make this quick, the test plot command contains the minimum
        # number of data points
        plotcmd, testcmd, testdata = self._getPlotCmd( curves )

        if self.plotOptions.get('terminal') == 'gp':
            self._dumpPipe = open(self.plotOptions['output'],'w')
            os.chmod(self.plotOptions['output'], 0o755)

            import distutils.spawn
            gnuplotpath = distutils.spawn.find_executable('gnuplot')

            self._safelyWriteToPipe('#!' + gnuplotpath)
            self._safelyWriteToPipe(self._plotOptionsCmds)

        else:
            self._testPlotcmd(testcmd, testdata)

            # tests ok. Now set the terminal and actually make the plot!
            if 'terminal' in self.plotOptions:
                self._safelyWriteToPipe("set terminal " + self.plotOptions['terminal'],
                                        'terminal')

            # I always set the output. If no plot option explicitly is given then I
            # either "set output" for a known interactive terminal, or redirect to
            # python's STDOUT otherwise
            if 'output' in self.plotOptions:
                if self.plotOptions['output'] != '':
                    # user requested an explicit output
                    self._safelyWriteToPipe('set output "' + self.plotOptions['output'] + '"',
                                            'output')
                else:
                    # user requested null output
                    self._safelyWriteToPipe('set output',
                                            'output')
            else:
                # user requested nothing. Is this a known interactive terminal or an
                # unspecified terminal (unspecified terminal assumed to be
                # interactive)? Then set the null output
                if 'terminal' not in self.plotOptions or self.plotOptions['terminal'] in knownInteractiveTerminals:
                    self._safelyWriteToPipe('set output',
                                            'output')
                else:
                    if self.fdDupSTDOUT is None:
                        raise Exception("I need to plot to STDOUT, but STDOUT wasn't available")

                    self.plotOptions['output'] = '/dev/fd/' + str(self.fdDupSTDOUT)
                    self._safelyWriteToPipe('set output "' + self.plotOptions['output'] + '"',
                                            'output')

        # all done. make the plot
        self._printGnuplotPipe( plotcmd + "\n")

        for curve in curves:
            self._sendCurve(curve)

        # There's some bug in gnuplot right now, where it sometimes reads too
        # many bytes after receiving inline data, which swallows the initial
        # bytes in a subsequent command, breaking things. I workaround by
        # stuffing newlines into the pipe. These don't do anything, and gnuplot
        # is allowed to steal some number of them without breaking anything. I
        # running gnuplot=5.2.6+dfsg1-1 on Debian. I can tickle the bug by doing
        # this:
        #   gp.plot(np.arange(5))
        # Error:
        # ...
        #   File "/home/dima/projects/gnuplotlib/gnuplotlib.py", line 1221, in _safelyWriteToPipe
        #     raise GnuplotlibError(barfmsg)
        # gnuplotlib.GnuplotlibError: Gnuplot error: '
        # "
        #          ^
        #          line 0: invalid command
        # ' while sending cmd 'set output'
        self._printGnuplotPipe('\n\n\n\n')

        if self.plotOptions.get('terminal') == 'gp':
            self._printGnuplotPipe('pause mouse close\n')
            self._dumpPipe.close()
            self._dumpPipe = None

        else:
            # read and report any warnings that happened during the plot
            self._checkpoint('printwarnings')

            # Reset the output. This is required for some terminals such as svg,
            # that need to write out a closing stanza
            self._safelyWriteToPipe('set output', 'output')

            if self.plotOptions.get('wait'):
                self.wait()

        # I force gnuplot to tell me it's done before exiting. Without this 'set
        # terminal dumb' plots don't end up rendering anything: we kill the
        # process before it has time to do anything
        self._checkpoint('final printwarnings')






globalplot = None

def plot(*curves, **jointOptions):

    r'''A simple wrapper around class gnuplotlib

    SYNOPSIS

        >>> import numpy as np
        >>> import gnuplotlib as gp

        >>> x = np.linspace(-5,5,100)

        >>> gp.plot( x, np.sin(x) )
        [ graphical plot pops up showing a simple sinusoid ]


        >>> gp.plot( (x, np.sin(x), {'with': 'boxes'}),
        ...          (x, np.cos(x), {'legend': 'cosine'}),

        ...          _with    = 'lines',
        ...          terminal = 'dumb 80,40',
        ...          unset    = 'grid')

        [ ascii plot printed on STDOUT]
           1 +-+---------+----------+-----------+-----------+----------+---------+-+
             +     +|||+ +          +         +++++   +++|||+          +           +
             |     |||||+                    +     +  +||||||       cosine +-----+ |
         0.8 +-+   ||||||                    +     + ++||||||+                   +-+
             |     ||||||+                  +       ++||||||||+                    |
             |     |||||||                  +       ++|||||||||                    |
             |     |||||||+                +        |||||||||||                    |
         0.6 +-+   ||||||||               +         +||||||||||+                 +-+
             |     ||||||||+              |        ++|||||||||||                   |
             |     |||||||||              +        |||||||||||||                   |
         0.4 +-+   |||||||||              |       ++||||||||||||+                +-+
             |     |||||||||             +        +||||||||||||||                  |
             |     |||||||||+            +        |||||||||||||||                  |
             |     ||||||||||+           |       ++||||||||||||||+           +     |
         0.2 +-+   |||||||||||          +        |||||||||||||||||           +   +-+
             |     |||||||||||          |        +||||||||||||||||+          |     |
             |     |||||||||||         +         ||||||||||||||||||         +      |
           0 +-+   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++   +-+
             |       +        ||||||||||||||||||+         |       ++||||||||||     |
             |       |        +|||||||||||||||||          +        |||||||||||     |
             |       +        ++||||||||||||||||          |        +||||||||||     |
        -0.2 +-+      +        |||||||||||||||||          +        |||||||||||   +-+
             |        |        ++||||||||||||||+           |       ++|||||||||     |
             |        +         |||||||||||||||            +        ++||||||||     |
             |         |        +||||||||||||||            +         |||||||||     |
        -0.4 +-+       +        ++||||||||||||+             |        +||||||||   +-+
             |          +        |||||||||||||              +        |||||||||     |
             |          |        +|||||||||||+               +       ++|||||||     |
        -0.6 +-+        +        ++||||||||||                |        +|||||||   +-+
             |           +        |||||||||||                +        ++||||||     |
             |           +        +|||||||||+                 +        |||||||     |
             |            +       ++||||||||                  +       +++|||||     |
        -0.8 +-+          +      + ++||||||+                   +      + +|||||   +-+
             |             +    +   +||||||                     +    +  ++||||     |
             +           +  +  ++   ++|||++     +           +   ++  +  + ++|||     +
          -1 +-+---------+----------+-----------+-----------+----------+---------+-+
            -6          -4         -2           0           2          4           6


    DESCRIPTION

    class gnuplotlib provides full power and flexibility, but for simple plots this
    wrapper is easier to use. plot() uses a global instance of class gnuplotlib, so
    only a single plot can be made by plot() at a time: the one plot window is
    reused.

    Data is passed to plot() in exactly the same way as when using class gnuplotlib.
    The kwargs passed to this function are a combination of curve options and plot
    options. The curve options passed here are defaults for all the curves. Any
    specific options specified in each curve override the defaults given in the
    kwargs.

    See the documentation for class gnuplotlib for full details.

    '''

    # pull out the options (joint curve and plot)
    jointOptions = _dictDeUnderscore(jointOptions)


    # separate the options into plot and curve ones
    plotOptions       = {}
    curveOptions_base = {}
    for opt in jointOptions:
        if opt in knownCurveOptions:
            curveOptions_base[opt] = jointOptions[opt]
        elif opt in knownPlotOptions:
            plotOptions[opt] = jointOptions[opt]
        else:
            raise GnuplotlibError("Option '{}' not a known curve or plot option".format(opt))

    # I make a brand new gnuplot process if necessary. If one already exists, I
    # re-initialize it. If we're doing a data dump then I also create a new
    # object. There's no gnuplot session to reuse in that case, and otherwise
    # the dumping won't get activated
    global globalplot
    if not globalplot or _data_dump_only(plotOptions):
        globalplot = gnuplotlib(**plotOptions)
    else:
        globalplot.__init__(**plotOptions)


    globalplot.plot(*curves, **curveOptions_base)


def plot3d(*curves, **jointOptions):

    r'''A simple wrapper around class gnuplotlib to make 3d plots

    SYNOPSIS

        import numpy as np
        import gnuplotlib as gp

        th = np.linspace(0,10,1000)
        x  = np.cos(np.linspace(0,10,1000))
        y  = np.sin(np.linspace(0,10,1000))

        gp.plot3d( x, y, th )
        [ an interactive, graphical plot of a spiral pops up]

    DESCRIPTION

    class gnuplotlib provides full power and flexibility, but for simple 3d plots
    this wrapper is easier to use. plot3d() simply calls plot(..., _3d=True). See
    the documentation for plot() and class gnuplotlib for full details.

    '''
    jointOptions['3d'] = True
    plot(*curves, **jointOptions)


def plotimage(*curves, **jointOptions):

    r'''A simple wrapper around class gnuplotlib to plot image maps

    SYNOPSIS

        import numpy as np
        import gnuplotlib as gp

        x,y = np.ogrid[-10:11,-10:11]
        gp.plotimage( x**2 + y**2,
                      title     = 'Heat map')

    DESCRIPTION

    class gnuplotlib provides full power and flexibility, but for simple image-map
    plots this wrapper is easier to use. plotimage() simply calls plot(...,
    _with='image', tuplesize=3). See the documentation for plot() and class
    gnuplotlib for full details.

    '''

    jointOptions['_with']     = 'image'
    jointOptions['tuplesize'] = 3
    plot(*curves, **jointOptions)


def wait():
    r'''Waits until the open interactive plot window is closed

    SYNOPSIS

        import numpy as np
        import gnuplotlib as gp

        gp.plot(np.arange(5))

        # interactive plot pops up

        gp.wait()

        # We get here when the user closes the plot window

    DESCRIPTION

    This applies to the global gnuplotlib object.

    It's not at all trivial to detect if a current plot window exists. If not,
    this function will end up waiting forever, and the user will need to Ctrl-C

    '''
    global globalplot
    if not globalplot:
        raise Exception("There isn't a plot to wait on")

    globalplot.wait()





if __name__ == '__main__':

    import numpy      as np
    import gnuplotlib as gp
    import time

    x = np.arange(101) - 50
    gp.plot(x**2, dump=0, ascii=0)
    time.sleep(1)


    g1 = gp.gnuplotlib(title = 'Parabola with error bars',
                       _with = 'xyerrorbars')
    g1.plot( x**2 * 10, np.abs(x)/10, np.abs(x)*5,
             legend    = 'Parabola',
             tuplesize = 4 )
    time.sleep(5)


    x,y = np.ogrid[-10:11,-10:11]
    gp.plot( x**2 + y**2,
             title     = 'Heat map',
             set       = 'view map',
             _with     = 'image',
             tuplesize = 3)
    time.sleep(5)


    theta = np.linspace(0, 6*np.pi, 200)
    z     = np.linspace(0, 5,       200)
    g2 = gp.gnuplotlib(_3d = True)
    g2.plot( (np.cos(theta),  np.sin(theta), z),
             (np.cos(theta), -np.sin(theta), z))
    time.sleep(60)
