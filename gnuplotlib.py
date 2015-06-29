#!/usr/bin/python

from __future__ import print_function

import subprocess
import time
import sys
import re
import select
import numpy as np



knownPlotOptions = set(('3d', 'dump', 'binary', 'log',
                        'extracmds', 'nogrid', 'square', 'square_xy', 'title',
                        'hardcopy', 'terminal', 'output',
                        'globalwith',
                        'xlabel', 'xmax', 'xmin',
                        'y2label', 'y2max', 'y2min',
                        'ylabel', 'ymax', 'ymin',
                        'zlabel', 'zmax', 'zmin',
                        'cbmin', 'cbmax'))

knownCurveOptions = set(('legend', 'y2', 'with', 'tuplesize'))

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






def _have(opt, where):
    return opt in where

def _active(opt, where):
    return opt in where and where[opt]



class GnuplotlibError(Exception):
    def __init__(self, err): self.err = err
    def __str__(self):       return self.err





class gnuplotlib:

    # class members
    def __init__(self, **plotOptions):

        # some defaults
        self.gnuplotProcess   = None
        self.plotOptions      = plotOptions
        self.t0               = time.time()
        self.checkpoint_stuck = False

        plotOptionsCmd = self._getPlotOptionsCmd()

        self._startgnuplot()
        self._logEvent("_startgnuplot() finished")

        self._safelyWriteToPipe(plotOptionsCmd)


    def _startgnuplot(self):

        self._logEvent("_startgnuplot()")

        if 'dump' in self.plotOptions:
            return

        cmd = ['gnuplot']
        if 'persist' in features:
            cmd += ['--persist']

        self.gnuplotProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def _havePlotOption  (self, opt): return _have  (opt, self.plotOptions)
    def _activePlotOption(self, opt): return _active(opt, self.plotOptions)

    def _getPlotOptionsCmd(self):

        def have(opt):   return self._havePlotOption(opt)
        def active(opt): return self._activePlotOption(opt)


        for option in self.plotOptions:
            if not option in knownPlotOptions:
                raise GnuplotlibError(option + ' is not a valid plot option')


        # set some defaults
        # plot with lines and points by default
        if not have('globalwith'):
            self.plotOptions['globalwith'] = 'linespoints'

        # make sure I'm not passed invalid combinations of options
        if active('3d'):
            if have('y2min') or have('y2max'):
                raise GnuplotlibError("'3d' does not make sense with 'y2'...")

            if not 'equal_3d' in features and \
               ( active('square_xy') or active('square') ):

                sys.stderr.write("Your gnuplot doesn't support square aspect ratios for 3D plots, so I'm ignoring that\n")
                del self.plotOptions['square_xy']
                del self.plotOptions['square']
        else:
            if active('square_xy'):
                raise GnuplotlibError("'square_xy' only makes sense with '3d'")



        cmd = ''

        # grid on by default
        if not active('nogrid'):
            cmd += "set grid\n"


        # set the plot bounds

        for axis in ('x', 'y', 'y2', 'z', 'cb'):

            # If a bound isn't given I want to set it to the empty string, so I can communicate it simply
            # to gnuplot
            for minmax in ('min', 'max'):
                opt = axis + minmax
                if not have(opt): self.plotOptions[opt] = ''

            # if any of the ranges are given, set the range
            if len(self.plotOptions[axis + 'min'] + self.plotOptions[axis + 'max']):
                cmd += "set {axis}range [{axis}min:{axis}max]\n".format(axis = axis)

            # set the curve labels
            if not axis == 'cb':
                if have(axis + 'label'):
                    cmd += 'set {axis}label "{label}"\n'.format(axis = axis,
                                                                label = self.plotOptions[axis + 'label'])



        # set the title
        if have('title'):
            cmd += 'set title "{}"\n'.format(self.plotOptions['title'])


        # handle a requested square aspect ratio
        # set a square aspect ratio. Gnuplot does this differently for 2D and 3D plots
        if active('3d'):
            if active('square'):
                cmd += "set view equal xyz\n"
            elif active('square_xy'):
                cmd += "set view equal xy\n"
        else:
            if active('square'):
                cmd += "set size ratio -1\n"

        # handle 'hardcopy'. This simply ties in to 'output' and 'terminal', handled
        # later
        if have('hardcopy'):
            # 'hardcopy' is simply a shorthand for 'terminal' and 'output', so they
            # can't exist together
            if have('terminal') or have('output'):
                raise GnuplotlibError(
                    """The 'hardcopy' option can't coexist with either 'terminal' or 'output'.  If the
defaults are acceptable, use 'hardcopy' only, otherwise use 'terminal' and
'output' to get more control""")

            outputfile = self.plotOptions['hardcopy']
            m = re.search(r'\.(eps|ps|pdf|png)$', outputfile)
            if not m:
                raise GnuplotlibError("Only .eps, .ps, .pdf and .png hardcopy output supported")

            outputfileType = m.group(1)

            terminalOpts = { 'eps': 'postscript solid color enhanced eps',
                             'ps':  'postscript solid color landscape 10',
                             'pdf': 'pdf solid color font ",10" size 11in,8.5in',
                             'png': 'png size 1280,1024' }

            self.plotOptions['terminal'] = terminalOpts[outputfileType]
            self.plotOptions['output']   = outputfile


        if have('terminal') and not have('output'):
            sys.stderr.write('Warning: defined gnuplot terminal, but NOT an output file. Is this REALLY what you want?')

        # add the extra global options
        if have('extracmds'):
            # if there's a single extracmds option, put it into a 1-element list to
            # make the processing work
            if type(self.plotOptions['extracmds']) == 'str':
                self.plotOptions['extracmds'] = [self.plotOptions['extracmds']]

            for extracmd in self.plotOptions['extracmds']:
                cmd += "extracmd" + "\n"

        return cmd



    def __del__(self):

        if self.gnuplotProcess:
            self.gnuplotProcess.kill()
            self.gnuplotProcess.wait()
            self.gnuplotProcess = None





    def _safelyWriteToPipe(self, string, flags=''):

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
                        line, re.X) and not re.match('terminal', flags):
                raise GnuplotlibError("Please do not 'set terminal' manually. Use the 'terminal' plot option instead")

            if re.match(r'''(?: .*;)?       # optionally wait for a semicolon
                            \s*
                            set\s+output\b''',
                        line, re.X) and not re.match('output', flags):
                raise GnuplotlibError("Please do not 'set output' manually. Use the 'output' plot option instead")




        for line in string.splitlines():
            line = line.strip()
            if not line:
                continue

            barfOnDisallowedCommands(line)

            self._printGnuplotPipe( line + '\n' )

            errorMessage, warnings = self._checkpoint('printwarnings')
            if errorMessage:
                barfmsg = "Gnuplot error: '\n{}\n' while sending line '{}'\n".format(errorMessage, line)
                if warnings:
                    barfmsg += "Warnings:\n" + str(warnings)
                raise GnuplotlibError(barfmsg)





    def _printGnuplotPipe(self, string):
        if self.gnuplotProcess:
            pipe = self.gnuplotProcess.stdin
        else:
            pipe = sys.stdout
        pipe.write( string )
        self._logEvent("Sent to child process {} bytes ==========\n{}=========================".
                       format(len(string), string))


    # I test the plot command by making a dummy plot with the test command.
    def _testPlotcmd(self, cmd, data):

        self._printGnuplotPipe( "set terminal push\n" )
        self._printGnuplotPipe( "set output\n" )
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

        self._printGnuplotPipe( "set terminal pop\n" )


    # syncronizes the child and parent processes. After _checkpoint() returns, I
    # know that I've read all the data from the child. Extra data that represents
    # errors is returned. Warnings are explicitly stripped out
    def _checkpoint(self, flags=''):

        # I have no way of knowing if the child process has sent its error data
        # yet. It may be that an error has already occurred, but the message hasn't
        # yet arrived. I thus print out a checkpoint message and keep reading the
        # child's STDERR pipe until I get that message back. Any errors would have
        # been printed before this
        checkpoint = "xxxxxxx Syncronizing gnuplot i/o xxxxxxx"

        self._printGnuplotPipe( 'print "{}"\n'.format(checkpoint) )

        # if no error pipe exists, we can't check for errors, so we're done.
        # Usually happens if(we're dumping)
        if not self.gnuplotProcess or not self.gnuplotProcess.stderr:
            return '',[]

        fromerr       = ''
        err_re_result = None

        while True:
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
                    r'''Gnuplot process no longer responding. This is likely a bug in PDL::Graphics::Gnuplot
and/or gnuplot itself. Please report this as a PDL::Graphics::Gnuplot bug.''')


            err_re_result = re.search(r'\s*(.*?)\s*{}$'.format(checkpoint), fromerr, re.M + re.S)
            if err_re_result:
                break



        fromerr = err_re_result.group(1)

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
        if not 'log' in self.plotOptions:
            return

        t = time.time() - self.t0

        print( "==== PID {} at t={:.4f}: {}".format(self.gnuplotProcess.pid if self.gnuplotProcess else '(none)',
                                                   t, event),
               file=sys.stderr )


    def _massageAndValidateArgs(self, curves):

        # first off, I convert the curve definition from a list of
        #    (data, data, data, ..., {options})
        # to a dict
        #    {options, '_data': (data, data, data, ....)}
        #
        # The former is nicer as a user interface, but the latter is easier for
        # the programmer (me!) to deal with
        def reformat(curve):
            d          = curve[-1]
            d['_data'] = curve[0:-1]
            return d

        curves = [ reformat(curve) for curve in curves ]



        for curve in curves:

            # tuplesize is either given explicitly, or taken from the '3d' plot
            # option. 2d plots default to tuplesize=2 and 3d plots to
            # tuplesize=3. This means that the tuplesize can be omitted for
            # basic plots but MUST be given for anything fancy
            Ndata = len(curve['_data'])
            if not 'tuplesize' in curve:
                curve['tuplesize'] = 3 if self._activePlotOption('3d') else 2

            if Ndata > curve['tuplesize']:
                raise GnuplotlibError("Got {} tuples, but the tuplesize is {}. Giving up"). \
                    format(Ndata, curve['tuplesize'])

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
                    if not self._activePlotOption('binary') and curve['tuplesize'] > 3:
                        raise GnuplotlibError( \
                            "Can't make more than 3-dimensional plots on a implicit 2D domain\n" + \
                            "when sending ASCII data. I don't think gnuplot supports this. Use binary data\n" + \
                            "or explicitly specify the domain\n" )

                    curve['matrix'] = True

                else:
                    raise GnuplotlibError( \
                        "plot() needed {} data piddles, but only got {}".format(curve['tuplesize'],Ndata))



            # The curve is now set up. I look at the input matrices to make sure
            # the dimensions line up

            # Make sure the domain and ranges describe the same number of data points
            dim01 = [None, None]
            for datum in curve['_data']:

                if _active('matrix', curve) and datum.ndim < 2:
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

                if _active('matrix', curve):
                    checkdim(1)


        return curves



    def _sendCurve(self, curve):

        np.savetxt( self.gnuplotProcess.stdin,
                    np.vstack(curve['_data']).transpose(),
                    '%s' )
        self.gnuplotProcess.stdin.write( "e\n")


    def plot(self, *curves):
        """Main gnuplotlib API entry point"""

        curves = self._massageAndValidateArgs(curves)

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
        if self._havePlotOption('terminal'):
            self._safelyWriteToPipe("set terminal {}\n".format(self.plotOptions['terminal']),
                                    'terminal')

        if self._havePlotOption('output'):
            self._safelyWriteToPipe('set output "{}"\n'.format(self.plotOptions['output']),
                                    'output')

        # all done. make the plot
        self._printGnuplotPipe( plotcmd + "\n")

        for curve in curves:
            self._sendCurve(curve)

        # read and report any warnings that happened during the plot
        self._checkpoint('printwarnings')



    def _getPlotCmd(self, curves):

        def optioncmd(curve):
            cmd = ''

            if 'legend' in curve: cmd += 'title "{}" '.format(curve['legend'])
            else:                 cmd += 'notitle '

            # use the given per-curve 'with' style if there is one. Otherwise fall
            # back on the global
            _with = curve['with'] if 'with' in curve else self.plotOptions['globalwith']

            if _with:                cmd += "with {} ".format(_with)
            if _active('y2', curve): cmd += "axes x1y2 "

            return cmd


        # def binaryFormatcmd(curve):
        #     # I make 2 formats: one real, and another to test the plot cmd, in case it
        #     # fails

        #     tuplesize = curve['tuplesize']

        #     format = ''
        #     if curve['matrix']:
        #         format += 'binary array=(' . curve['data'][0]->dim(0) . ',' . curve['data'][0]->dim(1) . ')'
        #         format += ' transpose'
        #         format += ' format="' . ('%double' x (tuplesize-2)) . '"'
        #     }
        #     else
        #     {
        #       format = 'binary record=' . curve['data'][0]->dim(0)
        #       format += ' format="' . ('%double' x tuplesize) . '"'
        #     }

        #     # when doing fancy things, gnuplot can get confused if I don't explicitly
        #     # tell it the tuplesize. It has its own implicit-tuples logic that I don't
        #     # want kicking in. As an example, the following simple plot doesn't work
        #     # in binary without telling it 'using':
        #     #   plot3d(binary => 1, with => 'image', sequence(5,5))
        #     my using_Ncolumns = curve['matrix'] ? (tuplesize-2) : tuplesize
        #     my using = ' using ' . join(':', 1..using_Ncolumns)

        #     # When plotting in binary, gnuplot gets confused if I don't explicitly
        #     # tell it the tuplesize. It's got its own implicit-tuples logic that I
        #     # don't want kicking in. As an example, the following simple plot doesn't
        #     # work in binary without this extra line:
        #     # plot3d(binary => 1,
        #     #        with => 'image', sequence(5,5))
        #     format += " using"

        #     # to test the plot I plot a single record
        #     my formatTest = format
        #     formatTest =~ s/record=\d+/record=1/
        #     formatTest =~ s/array=\(\d+,\d+\)/array=(2,2)/

        #     return (format, formatTest)


        def getTestDataLen(curve):
            # assuming sizeof(double)==8
            if _active('matrix', curve):
                return 8 * 2*2*(curve['tuplesize']-2)
            return 8 * curve['tuplesize']






        basecmd = ''

        # if anything is to be plotted on the y2 axis, set it up
        if any( _active('y2', curve) for curve in curves ):
            if self._activePlotOption('3d'):
                raise GnuplotlibError("3d plots don't have a y2 axis")

            basecmd += "set ytics nomirror\n"
            basecmd += "set y2tics\n"

        if self._activePlotOption('3d'): basecmd += 'splot '
        else:                            basecmd += 'plot '

        plotCurveCmds        = []
        plotCurveCmdsMinimal = [] # same as above, but with a single data point per plot only
        testData             = '' # data to make a minimal plot

        for curve in curves:
            optioncmds = optioncmd(curve)

            if self._activePlotOption('binary'):
                # # I get 2 formats: one real, and another to test the plot cmd, in case it
                # # fails. The test command is the same, but with a minimal point count. I
                # # also get the number of bytes in a single data point here
                # my (format, formatMinimal) = binaryFormatcmd(curve)
                # my Ntestbytes_here          = getTestDataLen(curve)

                # push @plotCurveCmds,        map { "'-' format _"     }    @optioncmds
                # push @plotCurveCmdsMinimal, map { "'-' formatMinimal _" } @optioncmds

                # # If there was an error, these whitespace commands will simply do
                # # nothing. If there was no error, these are data that will be plotted in
                # # some manner. I'm not actually looking at this plot so I don't care
                # # what it is. Note that I'm not making assumptions about how long a
                # # newline is (perl docs say it could be 0 bytes). I'm printing as many
                # # spaces as the number of bytes that I need, so I'm potentially doubling
                # # or even tripling the amount of needed data. This is OK, since gnuplot
                # # will simply ignore the tail.
                # testData += " \n" x (Ntestbytes_here * scalar @optioncmds)
                5

            else:
                # for some things gnuplot has its own implicit-tuples logic; I want to
                # suppress this, so I explicitly tell gnuplot to use all the columns we
                # have
                using = ' using ' + ':'.join(str(x+1) for x in range(curve['tuplesize']))

                # I'm using ascii to talk to gnuplot, so the minimal and "normal" plot
                # commands are the same (point count is not in the plot command)
                matrix = ''
                if _active('matrix', curve): matrix =  'matrix'
                plotCurveCmds.append( \
                    "'-' {matrix} {using} {optioncmds}".
                        format(matrix     = matrix,
                               using      = using,
                               optioncmds = optioncmds))

                testData_curve = ''
                if _active('matrix', curve):
                    testmatrix = "{0} {0}\n" + "{0} {0}\n\n" + "e\n"
                    testData_curve = testmatrix.format(testdataunit_ascii) * (curve['tuplesize'] - 2)
                else:
                    testData_curve = ' '.join( ['{}'.format(testdataunit_ascii)] * curve['tuplesize']) + \
                    "\n" + "e\n"

                testData += testData_curve

        # the command to make the plot and to test the plot
        cmd        =  basecmd + ','.join(plotCurveCmds)
        cmdMinimal = (basecmd + ','.join(plotCurveCmdsMinimal)) if plotCurveCmdsMinimal else cmd

        return (cmd, cmdMinimal, testData)

















if __name__ == '__main__':

    x = np.arange(100)
    y = x ** 2

    g = gnuplotlib()
    g.plot( (x,y,{}))




# search for "pdl", PDL
# make sure to shut down the process properly
# use checkpoint_stuck (sub DESTROY in Gnuplot.pm)
# binary default
# can I feed the data in a SEPARATE pipe? '&5'

# makeCurve and friends: do I really need chunks? As it is, I process the
# options and the data in completely different places, so I can just keep them
# where they are

# make binary work
# new option parsing: omitted curve options
#   packed data
#   matrices
#   plot( x,y ) should work (note not a list of tuples)

# find && ||
