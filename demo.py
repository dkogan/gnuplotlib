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

sleep_interval = 1





#################################
# Now the demos!
#################################

# first, some very basic stuff. Testing implicit domains, multiple curves in
# arguments, packed broadcastable data, etc
gp.plot(x**2)
time.sleep(sleep_interval)
gp.plot(-x, x**3)
time.sleep(sleep_interval)
gp.plot((x**2))
time.sleep(sleep_interval)
gp.plot((-x, x**3, {'with': 'lines'}), (x**2,))
time.sleep(sleep_interval)
gp.plot( x, np.vstack((x**3, x**2)) )
time.sleep(sleep_interval)
gp.plot( np.vstack((-x**3, x**2)), _with='lines' )
time.sleep(sleep_interval)
gp.plot( (np.vstack((x**3, -x**2)), {'with': 'points'} ))
time.sleep(sleep_interval)

#################################
# some more varied plotting, using the object-oriented interface
plot1 = gp.gnuplotlib(_with = 'linespoints',
                      xmin  = -10,
                      title = 'Error bars and other things')

# broadcasting title fix here
plot1.plot( ( np.vstack((x, x*2, x*3)), x**2 - 300,
              {'with':   'lines lw 4',
               'y2':     True,
               'legend': 'a parabola'}),

            (x**2 * 10, x**2/40, x**2/2, # implicit domain
             {'with':      'xyerrorbars',
              'tuplesize': 4}),

            (x, np.vstack((x**3, x**3 - 100)),
             {"with": 'lines',
              'legend': 'shifted cubic',
              'tuplesize': 2}))
time.sleep(sleep_interval)

#################################





# a way to control the point size
gp.plot( x**2, np.abs(x)/2, x*50,
         cbrange = '-600:600',
         _with   = 'points pointtype 7 pointsize variable palette',
         tuplesize = 4 )
time.sleep(sleep_interval)


################################
# some 3d stuff
################################

# gp.plot a sphere
gp.plot3d( x_3d, y_3d, z_3d,
           _with = 'points',
           title  = 'sphere',
           square = True,
           legend = 'sphere')
time.sleep(sleep_interval)

# sphere, ellipse together
# broadcasting title fix here
gp.plot3d( (x_3d * np.array([[1,2]]).T,
            y_3d * np.array([[1,2]]).T,
            z_3d,
            { 'legend': 'sphere'}),

           title  = 'sphere, ellipse',
           square = True,
           _with  = 'points')
time.sleep(sleep_interval)


# similar, written to a png
# broadcasting title fix here
gp.plot3d( (x_3d * np.array([[1,2]]).T,
            y_3d * np.array([[1,2]]).T,
            z_3d,
            { 'legend': 'sphere'}),

           title    = 'sphere, ellipse',
           square   = True,
           _with    = 'points',
           hardcopy = 'spheres.png')
time.sleep(sleep_interval)




# some paraboloids plotted on an implicit 2D domain
x,y = np.ogrid[-10:11, -10:11]
z   = x*x + y*y
gp.plot3d( ( z,  {'legend': 'zplus'}),
           (-z,  {'legend': 'zminus'}),
           (z*2, {'legend': 'zplus2'}),

           _with = 'points', title  = 'gridded paraboloids', ascii=True)
time.sleep(sleep_interval)

# 3d, variable color, variable pointsize
th    = np.linspace(0, 6*np.pi, 200)
z     = np.linspace(0, 5,       200)
size  = 0.5 + np.abs(np.cos(th))
color = np.sin(2*th)

# broadcasting title fix here
gp.plot3d( ( np.cos(th) * np.array([[1,-1]]).T,
             np.sin(th) * np.array([[1,-1]]).T,
             z, size, color, {'legend': "spiral 1"}),

           title     = 'double helix',
           tuplesize = 5,
           _with = 'points pointsize variable pointtype 7 palette' )
time.sleep(sleep_interval)


# implicit domain heat map
x,y = np.ogrid[-10:11, -10:11]
z   = x*x + y*y
gp.plot3d(z,
          title = 'Paraboloid heat map',
          set   = 'view map',
          _with = 'image')
time.sleep(sleep_interval)

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
         ymax = 20 )
time.sleep(sleep_interval)



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
        ascii     = False)
time.sleep(sleep_interval)

# 4d matrix curve
gp.plot(z, x,
        title     = '4D matrix plot. Binary.',
        square    = 1,
        tuplesize = 4,
        _with     = 'points palette ps variable pt 7',
        ascii     = False)
time.sleep(sleep_interval)

# broadcasting fix here: this is broadcast, but with different 'with'. Do I even
# want to allow this?
# 2 3d matrix curves

# gp.plot((np.rollaxis( np.dstack((x,z)), 2,0),
#          {'tuplesize': 3,
#           'with':      'points palette pt 7'}),

#         title  = '2 3D matrix plots. Binary.',
#         square = 1,
#         ascii = False)


gp.plot((x, {'tuplesize': 3,
             'with':      'points palette pt 7'}),
        (z, {'tuplesize': 3,
             'with':      'points ps variable pt 6'}),

        title  = '2 3D matrix plots. Binary.',
        square = 1,
        ascii = False)
time.sleep(sleep_interval)

# # Gnuplot doesn't support this
# gp.plot(z, x,
#         title     = '4D matrix plot. Binary.',
#         square    = 1,
#         tuplesize = 4,
#         _with     = 'points palette ps variable pt 7',
#         ascii     = True)
# time.sleep(sleep_interval)

# 2 3d matrix curves
gp.plot((x, {'tuplesize': 3,
             'with':      'points palette pt 7'}),
        (z, {'tuplesize': 3,
             'with':      'points ps variable pt 6'}),

        title  = '2 3D matrix plots. Binary.',
        square = 1,
        ascii = True)
time.sleep(sleep_interval)

###################################
# fancy contours just because I can
###################################
y,x = np.mgrid[0:61,0:61]
x -= 30.0
y -= 30.0
z = np.sin(x / 4.0) * y

# single 3d matrix curve
gp.plot3d( (z, {'tuplesize': 3, 'with': 'image'}),
           (z, {'tuplesize': 3, 'with': 'lines'}),

           title             = 'matrix plot with contours',
           cmds         = [ 'set contours base',
                            'set cntrparam bspline',
                            'set cntrparam levels 15',
                            'unset grid',
                            'unset surface',
                            'set view 0,0'],
           square = 1 )
time.sleep(sleep_interval)


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
    gp.plot( np.arange(5), cmds = 'pause 10' )
except gp.GnuplotlibError as e:
    print("OK! Got err I was supposed to get:\n[[[[[[[\n{}\n]]]]]]]\n".format(e))
except:
    print("ERROR! Got some other error I was NOT supposed to get\n")
else:
    print("ERROR! An error was supposed to be reported but it was not\n")
