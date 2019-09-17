#!/usr/bin/python

import numpy as np
import time
import sys

import gnuplotlib as gp

# data I use for 2D testing
x = np.arange(21) - 10

# data I use for 3D testing
th   = np.linspace(0,        np.pi*2, 30)
ph   = np.linspace(-np.pi/2, np.pi*2, 30)[:,np.newaxis]

x_3d = (np.cos(ph) * np.cos(th))          .ravel()
y_3d = (np.cos(ph) * np.sin(th))          .ravel()
z_3d = (np.sin(ph) * np.ones( th.shape )) .ravel()






#################################
# Now the demos!
#################################

# first, some very basic stuff. Testing implicit domains, multiple curves in
# arguments, packed broadcastable data, etc
gp.plot(x**2, wait=1)
gp.plot(-x, x**3, wait=1)
gp.plot((x**2), wait=1)
gp.plot((-x, x**3, {'with': 'lines'}), (x**2,), wait=1)
gp.plot( x, np.vstack((x**3, x**2)) , wait=1)
gp.plot( np.vstack((-x**3, x**2)), _with='lines' , wait=1)
gp.plot( (np.vstack((x**3, -x**2)), {'with': 'points'} ), wait=1)

#################################
# some more varied plotting, using the object-oriented interface
plot1 = gp.gnuplotlib(_with = 'linespoints',
                      xmin  = -10,
                      title = 'Error bars and other things',
                      wait = 1)

plot1.plot( ( np.vstack((x, x*2, x*3)), x**2 - 300,
              {'with':   'lines lw 4',
               'y2':     True,
               'legend': 'parabolas'}),

            (x**2 * 10, x**2/40, x**2/2, # implicit domain
             {'with':      'xyerrorbars',
              'tuplesize': 4}),

            (x, np.vstack((x**3, x**3 - 100)),
             {"with": 'lines',
              'legend': 'shifted cubics',
              'tuplesize': 2}))

#################################





# a way to control the point size
gp.plot( x**2, np.abs(x)/2, x*50,
         cbrange = '-600:600',
         _with   = 'points pointtype 7 pointsize variable palette',
         tuplesize = 4,
         wait = 1)

# labels
gp.plot(np.arange(5),np.arange(5)+1,
        np.array( ['{} {}'.format(x,x+1) for x in range(5)], dtype=str),
        _with='labels', tuplesize=3, ascii=1,
        wait = 1)

# Conchoids of de Sluze. Broadcasting example
theta = np.linspace(0, 2*np.pi, 1000)  # dim=(  1000,)
a     = np.arange(-4,3)[:, np.newaxis] # dim=(7,1)
gp.plot( theta,
         1./np.cos(theta) + a*np.cos(theta), # broadcasted. dim=(7,1000)

         _with  = 'lines',
         set    = 'polar',
         square = True,
         yrange = [-5,5],
         legend = a.ravel(),
         wait = 1)


################################
# some 3d stuff
################################

# gp.plot a sphere
gp.plot3d( x_3d, y_3d, z_3d,
           _with = 'points',
           title  = 'sphere',
           square = True,
           legend = 'sphere',
           wait = 1)

# sphere, ellipse together
gp.plot3d( (x_3d * np.array([[1,2]]).T,
            y_3d * np.array([[1,2]]).T,
            z_3d,
            { 'legend': np.array(('sphere', 'ellipse'))}),

           title  = 'sphere, ellipse',
           square = True,
           _with  = 'points',
           wait = 1)


# similar, written to a png
gp.plot3d( (x_3d * np.array([[1,2]]).T,
            y_3d * np.array([[1,2]]).T,
            z_3d,
            { 'legend': np.array(('sphere', 'ellipse'))}),

           title    = 'sphere, ellipse',
           square   = True,
           _with    = 'points',
           hardcopy = 'spheres.png',
           wait = 1)




# some paraboloids plotted on an implicit 2D domain
x,y = np.ogrid[-10:11, -10:11]
z   = x*x + y*y
gp.plot3d( ( z,  {'legend': 'zplus'}),
           (-z,  {'legend': 'zminus'}),
           (z*2, {'legend': 'zplus2'}),

           _with = 'points', title  = 'gridded paraboloids', ascii=True,
           wait = 1)

# 3d, variable color, variable pointsize
th    = np.linspace(0, 6*np.pi, 200)
z     = np.linspace(0, 5,       200)
size  = 0.5 + np.abs(np.cos(th))
color = np.sin(2*th)

gp.plot3d( ( np.cos(th) * np.array([[1,-1]]).T,
             np.sin(th) * np.array([[1,-1]]).T,
             z, size, color, { 'legend': np.array(('spiral 1', 'spiral 2'))}),

           title     = 'double helix',
           tuplesize = 5,
           _with = 'points pointsize variable pointtype 7 palette',
           wait = 1)


# implicit domain heat map
x,y = np.ogrid[-10:11, -10:11]
z   = x*x + y*y
gp.plot3d(z,
          title = 'Paraboloid heat map',
          set   = 'view map',
          _with = 'image',
          wait = 1)

# same, but as a 2d gp.plot, _with a curve drawn on top for good measure
x,y = np.ogrid[-10:11, -10:11]
z   = x*x + y*y
x   = np.linspace(0,20,100)
gp.plot( ( z, {'tuplesize': 3,
               'with':      'image'}),
         (x, 20*np.cos(x/20 * np.pi/2),

          {'tuplesize': 2,
           'with':      'lines'}),

         title  = 'Paraboloid heat map, 2D',
         xmin = 0,
         xmax = 20,
         ymin = 0,
         ymax = 20,
         wait = 1)



################################
# 2D implicit domain demos
################################
x,y = np.mgrid[-10:11, -10:11]
z   = np.sqrt(x*x + y*y)

x  = x[:, 2:12]
z  = z[:, 2:12]

# single 3d matrix curve
gp.plot(z,
        title     = 'Single 3D matrix plot. Binary.',
        square    = 1,
        tuplesize = 3,
        _with     = 'points palette pt 7',
        ascii     = False,
        wait      = 1)

# 4d matrix curve
gp.plot(z, x,
        title     = '4D matrix plot. Binary.',
        square    = 1,
        tuplesize = 4,
        _with     = 'points palette ps variable pt 7',
        ascii     = False,
        wait      = 1)

# Using broadcasting to plot each slice with a different style
gp.plot((np.rollaxis( np.dstack((x,z)), 2,0),
         {'tuplesize': 3,
          'with': np.array(('points palette pt 7','points ps variable pt 6'))}),

        title  = 'Two 3D matrix plots. Binary.',
        square = 1,
        ascii  = False,
        wait   = 1)

# # Gnuplot doesn't support this
# gp.plot(z, x,
#         title     = '4D matrix plot. Binary.',
#         square    = 1,
#         tuplesize = 4,
#         _with     = 'points palette ps variable pt 7',
#         ascii     = True,
#         wait      = 1)
#
# 2 3d matrix curves
gp.plot((np.rollaxis( np.dstack((x,z)), 2,0),
         {'tuplesize': 3,
          'with': np.array(('points palette pt 7','points ps variable pt 6'))}),

        title  = 'Two 3D matrix plots. Binary.',
        square = 1,
        ascii  = True,
        wait   = 1)

###################################
# fancy contours just because I can
###################################
y,x = np.mgrid[0:61,0:61]
x -= 30
y -= 30
z = np.sin(x / 4.0) * y

# single 3d matrix curve. Two plots: the image and the contours together.
# Broadcasting the styles
gp.plot3d( (z, {'tuplesize': 3, 'with': np.array(('image','lines'))}),

           title = 'matrix plot with contours',
           cmds  = [ 'set contours base',
                     'set cntrparam bspline',
                     'set cntrparam levels 15',
                     'unset grid',
                     'unset surface',
                     'set view 0,0'],
           square = 1,
           wait = 1)


################################
# testing some error detection
################################

sys.stderr.write("\n\n\n")
sys.stderr.write("==== Testing error detection ====\n")
sys.stderr.write('I should complain about an invalid "with":\n')
sys.stderr.write("=================================\n")
try:
    gp.plot(np.arange(5), _with = 'bogusstyle')
except gp.GnuplotlibError as e:
    print("OK! Got err I was supposed to get:\n[[[[[[[\n{}\n]]]]]]]\n".format(e))
except:
    print("ERROR! Got some other error I was NOT supposed to get\n")
else:
    print("ERROR! An error was supposed to be reported but it was not\n")

sys.stderr.write('gnuplotlib can detect I/O hangs. Here I ask for a delay, so I should detect this and quit after a few seconds:\n')
sys.stderr.write("=================================\n")
try:
    gp.plot( np.arange(5), cmds = 'pause 20' )
except gp.GnuplotlibError as e:
    print("OK! Got err I was supposed to get:\n[[[[[[[\n{}\n]]]]]]]\n".format(e))
except Exception as e:
    print("ERROR! Got some other error I was NOT supposed to get: {}\n".format(e))
else:
    print("ERROR! An error was supposed to be reported but it was not\n")
