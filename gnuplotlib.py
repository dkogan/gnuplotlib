#!/usr/bin/python

r'''* NAME

gnuplotlib: a gnuplot-based plotting backend for numpy

* SYNOPSIS

#+BEGIN_SRC python
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
#+END_SRC


* DESCRIPTION

This module allows numpy data to be plotted using Gnuplot as a backend. As much
as was possible, this module acts as a passive pass-through to Gnuplot, thus
making available the full power and flexibility of the Gnuplot backend. Gnuplot
is described in great detail at its upstream website: http://www.gnuplot.info

gnuplotlib has an object-oriented interface (via class gnuplotlib) and a few
helper class-less functions (plot(), plot3d(), plotimage()). Each instance of
class gnuplotlib has a gnuplot process associated with it, which has (usually) a
plot window to go with it. If multiple simultaneous plot windows are desired,
create a separate class gnuplotlib object for each.

The helper functions reuse a single global gnuplotlib instance, so each such
invocation rewrites over the previous gnuplot window.

When making a plot with the object-oriented interface, the gnuplotlib object is
created with a set of plot options, then the plot is made by passing it curves,
possibly with some curve options per curve. Something like this:

#+BEGIN_SRC python
 import gnuplotlib as gp
 g = gp.gnuplotlib(plot_options)
 g.plot( curve, curve, .... )
#+END_SRC

A call to plot(...) is simpler:

#+BEGIN_SRC python
 import gnuplotlib as gp
 gp.plot( curve, curve, ...., plot_and_default_curve_options )
#+END_SRC

plot3d(...) simply calls plot(...) with an extra plot option _3d=True.
plotimage(...) simply calls plot(...) with extra plot options _with='image',
tuplesize=3.

If just a single curve is plotted, 'curve' can simply be a sequence of numpy
arrays representing coordinates of each point. For instance:

#+BEGIN_SRC python
 plot( x, y )
#+END_SRC

If multiple curves are to be drawn on the same plot, then each 'curve' must live
in a separate tuple. The last element of any such tuple can be a dict of curve
options, if desired. For instance:

#+BEGIN_SRC python
 plot( (x1,y1),
       (x2,y2, {'legend'='Second curve'}) )
#+END_SRC

The plot_and_default_curve_options passed to plot(...) are kwargs. The curve
options present here are used as defaults for each curve; these defaults can be
overriden as desired. For instance:

#+BEGIN_SRC python
 plot( (x1,y1),
       (x2,y2, {'with':'points'}),
       _with='lines')
#+END_SRC

would plot the first curve with lines, but the second with points.

** Options arguments

Plot generation is controlled by two sets of options:

- Plot options: parameters that affect the whole plot, like the title of the
  plot, the axis labels, the extents, 2d/3d selection, etc. All the plot options
  are described below in "Plot options".

- Curve options: parameters that affect only a single curve. Each is described
  below in "Curve options".

** Data arguments

The 'curve' arguments in the plot(...) argument list represent the actual data
being plotted. Each output data point is a tuple (set of values, not a python
"tuple") whose size varies depending on what is being plotted. For example if
we're making a simple 2D x-y plot, each tuple has 2 values; if we're making a 3d
plot with each point having variable size and color, each tuple has 5 values
(x,y,z,size,color). In the plot(...) argument list each tuple element must be
passed separately. If we're making anything fancier than a simple 2D or 3D plot
(2- and 3- tuples respectively) then the 'tuplesize' curve option MUST be passed
in.

Furthermore, broadcasting is fully supported, so multiple curves can be plotted
by stacking data inside the passed-in arrays. Broadcasting works across curve
options also, so things like curve labels and styles can also be stacked inside
arrays. An example:

#+BEGIN_SRC python
  th    = np.linspace(0, 6*np.pi, 200)
  z     = np.linspace(0, 5,       200)
  size  = 0.5 + np.abs(np.cos(th))
  color = np.sin(2*th)


  # without broadcasting:
  plot3d( (  np.cos(th),  np.sin(th)
            z, size, color,
            { 'legend': 'spiral 1'}),

          ( -np.cos(th), -np.sin(th)
            z, size, color,
            { 'legend': 'spiral 2'})

          title     = 'double helix', tuplesize = 5,
          _with = 'points pointsize variable pointtype 7 palette' )


  # identical plot using broadcasting:
  plot3d( ( np.cos(th) * np.array([[1,-1]]).T,
            np.sin(th) * np.array([[1,-1]]).T,
            z, size, color, { 'legend': np.array(('spiral 1', 'spiral 2'))})

          title     = 'double helix', tuplesize = 5,
          _with = 'points pointsize variable pointtype 7 palette' )
#+END_SRC

This is a 3d plot with variable size and color. There are 5 values in the tuple,
which we specify. The first 2 arrays have dimensions (2,N); all the other arrays
have a single dimension. Thus the broadcasting rules generate 2 distinct curves,
with varying values for x,y and identical values for z, size and color. We label
the curves differently by passing an array for the 'legend' curve option. This
array contains strings, and is broadcast like everything else.

*** Implicit domains

When a particular tuplesize is specified, gnuplotlib will attempt to read that
many arrays. If there aren't enough arrays available, gnuplotlib will throw an
error, unless an implicit domain can be used. This happens if we are EXACTLY 1
or 2 arrays short (usually when making 2D and 3D plots respectively).

When making a simple 2D plot, if exactly 1 dimension is missing, gnuplotlib will
use numpy.arange(N) as the domain. This is why code like

#+BEGIN_SRC python
 plot(numpy.array([1,5,3,4,4]))
#+END_SRC

works. Only one array is given here, but the default tuplesize is 2, and we are
thus exactly 1 array short. This is thus equivalent to

#+BEGIN_SRC python
 plot(numpy.arange(5), numpy.array([1,5,3,4,4]) )
#+END_SRC

If plotting in 3D, an implicit domain will be used if we are exactly 2 arrayss
short. In this case, gnuplotlib will use a 2D grid as a domain. Example:

#+BEGIN_SRC python
 xy = numpy.arange(21*21).reshape(21*21)
 plot( xy, _with = 'points', _3d=True)
#+END_SRC

Here the only given array has dimensions (21,21). This is a 3D plot, so we are
exactly 2 arrays short. Thus, gnuplotlib generates an implicit domain,
corresponding to a 21-by-21 grid.

Note that while the DEFAULT tuplesize depends on whether we're making a 3d plot,
once we have a tuplesize, the logic doesn't care if a 3d plot is being made. It
can make sense to have a 2D implicit domain when making 2D plots. For example,
one can be plotting a color map:

#+BEGIN_SRC python
 x,y = np.ogrid[-10:11,-10:11]
 gp.plot( x**2 + y**2,
          title     = 'Heat map',
          set       = 'view map',
          _with     = 'image',
          tuplesize = 3)
#+END_SRC

Also note that the 'tuplesize' curve option is independent of implicit domains.
This option specifies not how many data arrays we have, but how many values
represent each data point. For example, if we want a 2D line plot with varying
colors plotted with an implicit domain, set tuplesize=3 as before (x,y,color),
but pass in only 2 arrays (y, color).

** Symbolic equations

Gnuplot can plot both data and equations. This module exists largely for the
data-plotting case, but sometimes it can be useful to plot equations together
with some data. This is supported by the 'equation' plot option. This plot
option is either a string (for a single equation) or a list/tuple containing
multiple strings for multiple equations. Note that plotting only equations
without data is not supported (and generally is better done with gnuplot
directly). An example:

#+BEGIN_SRC python
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
#+END_SRC

Here I generated some data, performed a curve fit to it, and plotted the data
points together with the best-fitting curve. Here the best-fitting curve was
plotted by gnuplot as an equation, so gnuplot was free to choose the proper
sampling frequency. And as we zoom around the plot, the sampling frequency is
adjusted to keep things looking nice.

Note that the various styles and options set by the other options do NOT apply
to these equation plots. Instead, the string is passed to gnuplot directly, and
any styling can be applied there. For instance, to plot a parabola with thick
lines, you can issue

#+BEGIN_SRC python
 gp.plot( ....., equation = 'x**2 with lines linewidth 2')
#+END_SRC

As before, see the gnuplot documentation for details. You can also do fancy
things:

#+BEGIN_SRC python
 x   = np.arange(100, dtype=float) / 100 * np.pi * 2;
 c,s = np.cos(x), np.sin(x)

 gp.plot( c,s,
          square=1, _with='points',
          set = ('parametric', 'trange [0:2*3.14]'),
          equation = "sin(t),cos(t)" )
#+END_SRC

Here the data are points evently spaced around a unit circle. Along with these
points we plot a unit circle as a parametric equation.

** Interactivity

The graphical backends of Gnuplot are interactive, allowing the user to pan,
zoom, rotate and measure the data in the plot window. See the Gnuplot
documentation for details about how to do this. Some terminals (such as wxt) are
persistently interactive, and the rest of this section does not apply to them.
Other terminals (such as x11) have the downside described here.

When using an affected terminal, interactivity is only possible if the gnuplot
process is running. As long as the python program calling gnuplotlib is running,
the plots are interactive, but once it exits, the child gnuplot process will
exit also. This will keep the plot windows up, but the interactivity will be
lost. So if the python program makes a plot and exits, the plot will NOT be
interactive.


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

#+BEGIN_SRC python
 plot(..., set='grid', unset=['xtics', 'ytics])
 [ turns on the grid, turns off the x and y axis tics ]
#+END_SRC

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

The y2 axis is the secondary y-axis that is enabled by the 'y2' curve option.
The 'cb' axis represents the color axis, used when color-coded plots are being
generated

- xlabel, ylabel, zlabel, y2label

These specify axis labels

- equation

This option allows equations represented as formula strings to be plotted along
with data passed in as numpy arrays. This can be a string (for a single
equation) or an array/tuple of strings (for multiple equations). See the
"Symbolic equations" section above.

- hardcopy

Instead of drawing a plot on screen, plot into a file instead. The output
filename is the value associated with this key. The output format is inferred
from the filename. Currently only eps, ps, pdf, png, svg are supported with some
default sets of options. This option is simply a shorthand for the 'terminal'
and 'output' options. If the defaults provided by the 'hardcopy' option are
insufficient, use 'terminal' and 'output' manually. Example:

#+BEGIN_SRC python
 plot(..., hardcopy="plot.pdf")
 [ Plots into that file ]
#+END_SRC

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

#+BEGIN_SRC python
  gp.plot( np.linspace(-5,5,30)**2,
            unset='grid', terminal='dumb 80 40' )
#+END_SRC

#+BEGIN_EXAMPLE
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
#+END_EXAMPLE

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
if desired.

- log

Used for debugging. If true, writes out the gnuplot commands and various
progress logs to STDERR in addition to writing to a gnuplot process. This is NOT
a dry run: data is sent to gnuplot AND to the log. Useful for debugging I/O
issues. Note that this log will contain binary data unless ascii-only plotting
is enabled (see below)

- ascii

If set, ASCII data is passed to gnuplot instead of binary data. Binary is the
default because it is much more efficient (and thus faster). Binary input works
for most plots, but not for all of them. An example where binary plotting
doesn't work is 'with labels', and this option exists to force ASCII
communication


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

Specifies how many values represent each data point. For 2D plots this defaults
to 2; for 3D plots this defaults to 3. These defaults are correct for simple
plots


* INTERFACE

** class gnuplotlib

A gnuplotlib object abstracts a gnuplot process and a plot window. Invocation:

#+BEGIN_SRC python
 import gnuplotlib as gp
 g = gp.gnuplotlib(plot_options)
 g.plot( curve, curve, .... )
#+END_SRC

The plot options are passed into the constructor; the curve options and the data
are passed into the plot() method. One advantage of making plots this way is
that there's a gnuplot process associated with each gnuplotlib instance, so as
long as the object exists, the plot will be interactive. Calling 'g.plot()'
multiple times reuses the plot window instead of creating a new one.

** global plot(...)

The convenience plotting routine in gnuplotlib. Invocation:

#+BEGIN_SRC python
 import gnuplotlib as gp
 gp.plot( curve, curve, ...., plot_and_default_curve_options )
#+END_SRC

Each 'plot()' call reuses the same window.

** global plot3d(...)

Generates 3D plots. Shorthand for 'plot(..., _3d=True)'

** global plotimage(...)

Generates an image plot. Shorthand for 'plot(..., _with='image', tuplesize=3)'


* RECIPES

Some different plots appear here. A longer set of demos is given in demos.py.

** 2D plotting

If we're plotting y-values sequentially (implicit domain), all you need is

#+BEGIN_SRC python
  plot(y)
#+END_SRC

If we also have a corresponding x domain, we can plot y vs. x with

#+BEGIN_SRC python
  plot(x, y)
#+END_SRC

*** Simple style control

To change line thickness:

#+BEGIN_SRC python
  plot(x,y, _with='lines linewidth 3')
#+END_SRC

To change point size and point type:

#+BEGIN_SRC python
  gp.plot(x,y, _with='points pointtype 4 pointsize 8')
#+END_SRC

Everything (like _with) feeds directly into Gnuplot, so look at the Gnuplot docs
to know how to change thicknesses, styles and such.

*** Errorbars

To plot errorbars that show y +- 1, plotted with an implicit domain

#+BEGIN_SRC python
  plot( y, np.ones(y.shape), _with = 'yerrorbars', tuplesize = 3 )
#+END_SRC

Same with an explicit x domain:

#+BEGIN_SRC python
  plot( x, y, np.ones(y.shape), _with = 'yerrorbars', tuplesize = 3 )
#+END_SRC

Symmetric errorbars on both x and y. x +- 1, y +- 2:

#+BEGIN_SRC python
  plot( x, y, np.ones(x.shape), 2*np.ones(y.shape), _with = 'xyerrorbars', tuplesize = 4 )
#+END_SRC

To plot asymmetric errorbars that show the range y-1 to y+2 (note that here you
must specify the actual errorbar-end positions, NOT just their deviations from
the center; this is how Gnuplot does it)

#+BEGIN_SRC python
  plot( y, y - np.ones(y.shape), y + 2*np.ones(y.shape),
       _with = 'yerrorbars', tuplesize = 4 )
#+END_SRC

*** More multi-value styles

Plotting with variable-size circles (size given in plot units, requires Gnuplot >= 4.4)

#+BEGIN_SRC python
  plot(x, y, radii,
       _with = 'circles', tuplesize = 3)
#+END_SRC

Plotting with an variably-sized arbitrary point type (size given in multiples of
the "default" point size)

#+BEGIN_SRC python
  plot(x, y, sizes,
       _with = 'points pointtype 7 pointsize variable', tuplesize = 3 )
#+END_SRC

Color-coded points

#+BEGIN_SRC python
  plot(x, y, colors,
       _with = 'points palette', tuplesize = 3 )
#+END_SRC

Variable-size AND color-coded circles. A Gnuplot (4.4.0) quirk makes it
necessary to specify the color range here

#+BEGIN_SRC python
  plot(x, y, radii, colors,
       cbmin = mincolor, cbmax = maxcolor,
       _with = 'circles palette', tuplesize = 4 )
#+END_SRC


Broadcasting example: the Conchoids of de Sluze. The whole family of curves is
generated all at once, and plotted all at once with broadcasting. Broadcasting
is also used to generate the labels. Generally these would be strings, but here
just printing the numerical value of the parameter is sufficient.

#+BEGIN_SRC python
 theta = np.linspace(0, 2*np.pi, 1000)  # dim=(  1000,)
 a     = np.arange(-4,3)[:, np.newaxis] # dim=(7,1)

 gp.plot( theta,
          1./np.cos(theta) + a*np.cos(theta), # broadcasted. dim=(7,1000)

          _with  = 'lines',
          set    = 'polar',
          square = True,
          yrange = [-5,5],
          legend = a.ravel() )
#+END_SRC

** 3D plotting

General style control works identically for 3D plots as in 2D plots.

To plot a set of 3d points, with a square aspect ratio (squareness requires
Gnuplot >= 4.4):

#+BEGIN_SRC python
  plot3d(x, y, z, square = 1)
#+END_SRC

If xy is a 2D array, we can plot it as a height map on an implicit domain

#+BEGIN_SRC python
  plot3d(xy)
#+END_SRC

Ellipse and sphere plotted together, using broadcasting:

#+BEGIN_SRC python
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
#+END_SRC

Image arrays plots can be plotted as a heat map:

#+BEGIN_SRC python
   x,y = np.ogrid[-10:11,-10:11]
   gp.plot( x**2 + y**2,
            title     = 'Heat map',
            set       = 'view map',
            _with     = 'image',
            tuplesize = 3)
#+END_SRC

** Hardcopies

To send any plot to a file, instead of to the screen, one can simply do

#+BEGIN_SRC python
  plot(x, y,
       hardcopy = 'output.pdf')
#+END_SRC

The 'hardcopy' option is a shorthand for the 'terminal' and 'output'
options. If more control is desired, the latter can be used. For example to
generate a PDF of a particular size with a particular font size for the text,
one can do

#+BEGIN_SRC python
  plot(x, y,
       terminal = 'pdfcairo solid color font ",10" size 11in,8.5in',
       output   = 'output.pdf')
#+END_SRC

This command is equivalent to the 'hardcopy' shorthand used previously, but the
fonts and sizes can be changed.


* COMPATIBILITY

Only python 2 is supported. I have no plans to support python 3 (it forces me to
care about unicode, which is an unreasonable burden), but patches are welcome.

Everything should work on all platforms that support Gnuplot and Python. That
said, only Debian GNU/Linux has been tested at this point. Comments and/or
patches are welcome.

* REPOSITORY

https://github.com/dkogan/gnuplotlib

* AUTHOR

Dima Kogan <dima@secretsauce.net>

* LICENSE AND COPYRIGHT

Copyright 2015-2016 Dima Kogan.

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License (version 3 or higher) as
published by the Free Software Foundation

See https://www.gnu.org/licenses/lgpl.html

'''



from __future__ import print_function

import subprocess
import time
import sys
import os
import re
import select
import numpy as np


# note that 'with' is both a known plot and curve option
knownPlotOptions = frozenset(('3d', 'dump', 'ascii', 'log',
                              'cmds', 'set', 'unset', 'square', 'square_xy', 'title',
                              'hardcopy', 'terminal', 'output',
                              'with', 'equation',
                              'xmax',  'xmin',  'xrange',  'xinv',  'xlabel',
                              'y2max', 'y2min', 'y2range', 'y2inv', 'y2label',
                              'ymax',  'ymin',  'yrange',  'yinv',  'ylabel',
                              'zmax',  'zmin',  'zrange',  'zinv',  'zlabel',
                              'cbmin', 'cbmax', 'cbrange'))

knownCurveOptions = frozenset(('legend', 'y2', 'with', 'tuplesize'))

knownInteractiveTerminals = frozenset(('x11', 'wxt', 'qt', 'aquaterm'))

# when testing plots with ASCII i/o, this is the unit of test data
testdataunit_ascii = 10




def _runSubprocess(cmd, input):
    """Runs a given command feeding the given input to stdin. Waits for the command
to terminate, and returns the stdout,stderr tuple we get back"""

    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(input=input)
    retcode = process.poll()
    if retcode:
        raise subprocess.CalledProcessError(retcode, cmd[0], output=out + err)
    return out,err


def _getGnuplotFeatures():

    # Be careful talking to gnuplot here. If you use a tty then gnuplot
    # messes with the tty settings where it should NOT. For example it turns
    # on the local echo. So make sure to not use a tty

    # first, I run 'gnuplot --help' to extract all the cmdline options as features
    helpstring = subprocess.check_output(['gnuplot', '--help'], stderr=subprocess.STDOUT)
    features = set( re.findall(r'--([a-zA-Z0-9_]+)', helpstring) )


    # then I try to set a square aspect ratio for 3D to see if it works
    out,err = _runSubprocess(['gnuplot'],
                             """set view equal
exit
""")

    # no output if works; some output if error
    if( not ( out or err ) ):
        features.add('equal_3d')

    return frozenset(features)


features = _getGnuplotFeatures()





def _dictDeUnderscore(d):
    """Takes a dict, and renames all keys that start with an '_' to not contain that
anymore. This is done because some keys are illegal as kwargs (notably 'with'
and '3d'), so the user passes in '_with' and '_3d', which ARE legal
    """
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





class gnuplotlib:

    def __init__(self, **plotOptions):

        # some defaults
        self.plotOptions      = _dictDeUnderscore(plotOptions)
        self.t0               = time.time()
        self.checkpoint_stuck = False
        self.sync_count       = 1

        plotOptionsCmds = self._getPlotOptionsCmds()

        # if we already have a gnuplot process, reset it. Otherwise make a new
        # one
        if hasattr(self, 'gnuplotProcess') and self.gnuplotProcess:
            self._printGnuplotPipe( "reset\nset output\n" )
            self._checkpoint()
        else:
            self.gnuplotProcess = None
            self._startgnuplot()
            self._logEvent("_startgnuplot() finished")

        self._safelyWriteToPipe(plotOptionsCmds)


    def _startgnuplot(self):

        self._logEvent("_startgnuplot()")

        if not self.plotOptions.get('dump'):

            cmd = ['gnuplot']
            if 'persist' in features:
                cmd += ['--persist']

            self.fdDupSTDOUT = os.dup(sys.stdout.fileno())
            self.gnuplotProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
                del self.plotOptions['square_xy']
                del self.plotOptions['square']
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

            # if we have min AND max AND inv, I make sure that min>max, and
            # suppress the inv. This is because in gnuplot 'plot [min:max]
            # reverse' ingores the 'reverse' if both min and max are given
            if axis + 'min' in self.plotOptions and \
               axis + 'max' in self.plotOptions and \
               self.plotOptions.get(axis + 'inv'):
                minval = min(self.plotOptions[axis + 'min'], self.plotOptions[axis + 'max'])
                maxval = max(self.plotOptions[axis + 'min'], self.plotOptions[axis + 'max'])
                self.plotOptions[axis + 'min'] = maxval
                self.plotOptions[axis + 'max'] = minval
                self.plotOptions[axis + 'inv'] = False

            # If a bound isn't given I want to set it to the empty string, so I can communicate it simply
            # to gnuplot
            rangeopt_name = axis + 'range'
            for minmax in ('min', 'max'):
                opt = axis + minmax
                if not opt in self.plotOptions:
                    self.plotOptions[opt] = ''
                else:
                    if rangeopt_name in self.plotOptions:
                        raise GnuplotlibError("Both {} and {} not allowed at the same time".format(opt,rangeopt_name))
                    self.plotOptions[opt] = str(self.plotOptions[opt])

            # if any of the ranges are given, set the range
            if len(self.plotOptions[axis + 'min'] + self.plotOptions[axis + 'max']):
                rangeopt_val = ':'.join((self.plotOptions[axis + 'min'], self.plotOptions[axis + 'max']))
            elif rangeopt_name in self.plotOptions:
                # A range was given. If it's a string, just take it. It can also
                # be a two-value list for the min/max
                rangeopt_val = self.plotOptions[rangeopt_name]
                if isinstance(rangeopt_val, (list, tuple)):
                    rangeopt_val = ':'.join(str(x) for x in rangeopt_val)
            else:
                rangeopt_val = ''

            cmds.append( "set {} [{}] {}".format(rangeopt_name,
                                                 rangeopt_val,
                                                 'reverse' if self.plotOptions.get(axis + 'inv') else ''))

            # set the curve labels
            if not axis == 'cb':
                if axis + 'label' in self.plotOptions:
                    cmds.append('set {axis}label "{label}"'.format(axis = axis,
                                                                   label = self.plotOptions[axis + 'label']))



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
            m = re.search(r'\.(eps|ps|pdf|png|svg)$', outputfile)
            if not m:
                raise GnuplotlibError("Only .eps, .ps, .pdf, .png and .svg hardcopy output supported")

            outputfileType = m.group(1)

            terminalOpts = { 'eps': 'postscript solid color enhanced eps',
                             'ps':  'postscript solid color landscape 10',
                             'pdf': 'pdf solid color font ",10" size 11in,8.5in',
                             'png': 'png size 1280,1024',
                             'svg': 'svg enhanced solid'}

            self.plotOptions['terminal'] = terminalOpts[outputfileType]
            self.plotOptions['output']   = outputfile


        if 'terminal' in self.plotOptions:
            if self.plotOptions['terminal'] in knownInteractiveTerminals:
                # known interactive terminal
                if 'output' in self.plotOptions and self.plotOptions['output'] != '':
                    sys.stderr.write("Warning: requested a known-interactive gnuplot terminal AND an output file. Is this REALLY what you want?\n")

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

        if self.gnuplotProcess:
            if self.checkpoint_stuck:
                self.gnuplotProcess.terminate()
            else:
                self._printGnuplotPipe( "exit\n" )

            self.gnuplotProcess.wait()
            self.gnuplotProcess = None
            os.close(self.fdDupSTDOUT)






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
        return sys.stdout

    def _printGnuplotPipe(self, string):
        self._gnuplotStdin().write( string )
        self._logEvent("Sent to child process {} bytes ==========\n{}=========================".
                       format(len(string), string))


    # I test the plot command by making a dummy plot with the test command.
    def _testPlotcmd(self, cmd, data):

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


    # syncronizes the child and parent processes. After _checkpoint() returns, I
    # know that I've read all the data from the child. Extra data that represents
    # errors is returned. Warnings are explicitly stripped out
    def _checkpoint(self, flags=''):

        # I have no way of knowing if the child process has sent its error data
        # yet. It may be that an error has already occurred, but the message hasn't
        # yet arrived. I thus print out a checkpoint message and keep reading the
        # child's STDERR pipe until I get that message back. Any errors would have
        # been printed before this
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

            rlist,wlist,xlist = select.select([self.gnuplotProcess.stderr],[], [], 5)

            if rlist:
                # read a byte. I'd like to read "as many bytes as are
                # available", but I don't know how to this in a very portable
                # way (I just know there will be windows users complaining if I
                # simply do a non-blocking read). Very little data will be
                # coming in anyway, so doing this a byte at a time is an
                # irrelevant inefficiency
                byte = self.gnuplotProcess.stderr.read(1)
                fromerr += byte
                self._logEvent("Read byte '{}' ({}) from gnuplot child process".format(byte, hex(ord(byte))))
            else:
                self._logEvent("Gnuplot read timed out")
                self.checkpoint_stuck = True

                raise GnuplotlibError(
                    r'''Gnuplot process no longer responding. This is likely a bug in gnuplotlib
and/or gnuplot itself. Please report this as a gnuplotlib bug''')

        fromerr = re.search(r'\s*(.*?)\s*{}$'.format(checkpoint), fromerr, re.M + re.S).group(1)

        warningre = re.compile(r'^.*(?:warning:\s*(.*?)\s*$)\n?', re.M + re.I)
        warnings  = warningre.findall(fromerr)

        if flags == 'printwarnings':
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
        # 2. "invalid range" errors caused by requested plot bounds (xmin, xmax,
        #    etc) tossing out any test-plot data. The point of the plot-command
        #    testing is to make sure the command is valid, so any out-of-boundedness
        #    of the test data is irrelevant
        #
        # 3. image grid complaints
        if flags == 'ignore_known_test_failures':
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
                           re.X + re.M)
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


    def _sendCurve(self, curve):

        pipe = self._gnuplotStdin()
        if self.plotOptions.get('ascii'):
            if curve.get('matrix'):
                np.savetxt( pipe,
                            np.vstack(curve['_data']).astype(np.float64,copy=False),
                            '%s' )
                pipe.write("\ne\n")
            else:
                np.savetxt( pipe,
                            np.vstack(curve['_data']).transpose().astype(np.float64,copy=False),
                            '%s' )
                pipe.write("e\n")

        else:
            np.dstack(curve['_data']).astype(np.float64,copy=False).tofile(pipe)


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

            fmt += ' using ' + ':'.join( str(x+1) for x in range(using_Ncolumns) )

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

        if self.plotOptions.get('3d'): basecmd += 'splot '
        else:                          basecmd += 'plot '

        # send all equations
        if 'equation' in self.plotOptions:
            if isinstance(self.plotOptions['equation'], (list, tuple)):
                basecmd += ''.join( eq + ', ' for eq in self.plotOptions['equation'])
            else:
                basecmd += self.plotOptions['equation'] + ', '

        plotCurveCmds        = []
        plotCurveCmdsMinimal = [] # same as above, but with a single data point per plot only
        testData             = '' # data to make a minimal plot

        for curve in curves:
            optioncmds = optioncmd(curve)

            if not self.plotOptions.get('ascii'):
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
                using = ' using ' + ':'.join(str(x+1) for x in range(curve['tuplesize']))

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

        # the command to make the plot and to test the plot
        cmd        =  basecmd + ','.join(plotCurveCmds)
        cmdMinimal = (basecmd + ','.join(plotCurveCmdsMinimal)) if plotCurveCmdsMinimal else cmd

        return (cmd, cmdMinimal, testData)


    def _massageAndValidateArgs(self, curves, curveOptions_base):

        # Collect all the passed data into a tuple of lists, one curve per list
        if all(type(curve) is np.ndarray for curve in curves):
            curves = (list(curves),)
        elif all(type(curve) is tuple for curve in curves):
            curves = [ list(curve) for curve in curves ]
        else:
            raise GnuplotlibError("all data arguments should be of type ndarray (one curve) or tuples")

        # add an options dict if there isn't one, apply the base curve
        # options to each curve
        for curve in curves:
            if not type(curve[-1]) is dict:
                curve.append({})
            curve[-1].update(curveOptions_base)

        # I convert the curve definition from a list of
        #    (data, data, data, ..., {options})
        # to a dict
        #    {options, '_data': (data, data, data, ....)}
        #
        # The former is nicer as a user interface, but the latter is easier for
        # the programmer (me!) to deal with
        def reformat(curve):
            d          = _dictDeUnderscore(curve[-1])
            d['_data'] = list(curve[0:-1])
            return d
        curves = [ reformat(curve) for curve in curves ]



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



        # I now manually broadcast the dimensions. PDL does this for me
        # automatically, but numpy absolutely does not. This is a MAJOR
        # advantage PDL has over numpy. Oh well
        def broadcast_split(curve):

            # I line up all the dimensions, and split off any that are being
            # broadcasted

            # With line plots I don't broadcast the last dimension; with
            # matrices, I don't broadcast the last 2
            ndims_keep = 2 if curve.get('matrix') else 1

            # object needed for fancy slices. m[:] is exactly the same as
            # m[colon], but 'colon' can be manipulated in ways that ':' can't
            colon = slice(None, None, None)

            # make a copy of the plot options
            curve_options = dict(curve)
            del curve_options['_data']

            # grab all option keys that have numpy arrays as values. I broadcast
            # these
            numpy_options_keys   = [ k for k in curve_options.keys()
                                     if type(curve_options[k]) == np.ndarray ]

            # The numpy option values have no domain dimension, so I add dummy
            # dimensions to make things line up
            idx_new_axes = (colon,) + (np.newaxis,)*ndims_keep
            for k in numpy_options_keys:
                curve_options[k] = curve_options[k][idx_new_axes]

            shapes = [ v.shape for v in curve['_data'] + [curve_options[k] for k in numpy_options_keys] ]
            max_ndim = max( len(s) for s in shapes )

            # Broadcasting does 2 things:
            # 1. out-of-bounds dimensions are added at the front
            # 2. too-high indices are truncated to 1
            #
            # I handle the first case before I do anything else: I add dummy
            # length-1 dimensions at the front as needed. After this is done,
            # ndims for all the matrices will be the same
            data = []
            for v in curve['_data']:
                N_new_axes = max_ndim - len(v.shape)
                idx_new_axes = (np.newaxis,)*N_new_axes + (colon,)
                data.append(v[idx_new_axes])

            for k in numpy_options_keys:
                o = curve_options[k]
                N_new_axes = max_ndim - len(o.shape)
                idx_new_axes = (np.newaxis,)*N_new_axes + (colon,)
                curve_options[k] = o[idx_new_axes]

            shapes = [ v.shape for v in data + [curve_options[k] for k in numpy_options_keys] ]



            dims = []
            for i in range(max_ndim):

                # looking at a particular dimension. I'm broadcasting, so this dimension
                # may not exist. The dimensions are lined up at the end. dim_idxs is the
                # indices of dimension i for each vector. If <0, this dimension does not
                # exist in that vector
                dim_idxs = [ len(s) - max_ndim + i for s in shapes ]

                # I grab all the dimensions that aren't 1. All the counts that aren't 1
                # must match, or else we can't broadcast this
                dims_not_1 = [ s[dim_idx] for s,dim_idx in zip(shapes,dim_idxs)
                               if dim_idx >= 0 and s[dim_idx] != 1 ]

                if len(dims_not_1) and not all( d == dims_not_1[0] for d in dims_not_1):
                    raise GnuplotlibError("Mismatched dimensions, cannot broadcast. Shapes: {}".format(shapes))

                # grab this dimension
                dims.append( dims_not_1[0] if len(dims_not_1) else 1 )


            split_curves = []
            def accum_dim( dimlist ):
                if len(dimlist) == max_ndim - ndims_keep:
                    # I have a full list of dimensions. I sample the curves and
                    # accumulate. Need to pay attention to 2 things:
                    #
                    # 1. out-of-bounds dimensions are added at the front (the
                    # 'data' and 'curve_options' already has this taken care of)
                    #
                    # 2. too-high indices are truncated to 1

                    # expand the dimensionality to cover out-of-bounds dimensions
                    split_curve = dict(curve_options)

                    def lookup_broadcasted_slice(array):
                        return tuple(d if array.shape[i] != 1 else 0 for i,d in enumerate(dimlist))

                    split_curve['_data'] = [ v[ lookup_broadcasted_slice(v) ] for v in data ]

                    for k in numpy_options_keys:
                        split_curve[k] = split_curve[k][ lookup_broadcasted_slice(split_curve[k]) +
                                                         (0,)*ndims_keep ]

                    split_curves.append(split_curve)
                    return

                for inext in range( dims[ len(dimlist)] ):
                    accum_dim( dimlist + (inext,) )

            accum_dim( () )
            return split_curves

        curves_flattened = []
        for curve in curves:
            curves_flattened.extend( broadcast_split( curve ))
        curves = curves_flattened


        return curves

    def plot(self, *curves, **curveOptions_base):
        r"""Main gnuplotlib API entry point"""

        curves = self._massageAndValidateArgs(curves, curveOptions_base)

        # I'm now ready to send the plot command. If the plot command fails,
        # I'll get an error message; if it succeeds, gnuplot will sit there
        # waiting for data. I don't want to have a timeout waiting for the error
        # message, so I try to run the plot command to see if it works. I make a
        # dummy plot into the 'dumb' terminal, and then _checkpoint() for
        # errors. To make this quick, the test plot command contains the minimum
        # number of data points
        plotcmd, testcmd, testdata = self._getPlotCmd( curves )

        self._testPlotcmd(testcmd, testdata)

        # tests ok. Now set the terminal and actually make the plot!

        # select the default terminal in case that's what we want
        self._safelyWriteToPipe("set terminal pop; set terminal push", 'terminal')

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
                self.plotOptions['output'] = '/dev/fd/' + str(self.fdDupSTDOUT)
                self._safelyWriteToPipe('set output "' + self.plotOptions['output'] + '"',
                                        'output')

        # all done. make the plot
        self._printGnuplotPipe( plotcmd + "\n")

        for curve in curves:
            self._sendCurve(curve)

        # read and report any warnings that happened during the plot
        self._checkpoint('printwarnings')

        # Reset the output. This is required for some terminals such as svg,
        # that need to write out a closing stanza
        self._safelyWriteToPipe('set output', 'output')







globalplot = None

def plot(*curves, **jointOptions):

    r'''A simple wrapper around class gnuplotlib

SYNOPSIS

 import numpy as np
 import gnuplotlib as gp

 x = np.linspace(-5,5,100)

 gp.plot( x, np.sin(x) )
 [ graphical plot pops up showing a simple sinusoid ]


 gp.plot( (x, np.sin(x), {'with': 'boxes'}),
          (x, np.cos(x), {'legend': 'cosine'}),

          _with    = 'lines',
          terminal = 'dumb 80,40',
          unset    = 'grid')

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
    if not globalplot or plotOptions.get('dump'):
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
