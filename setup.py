#!/usr/bin/python

from distutils.core          import setup
from distutils.command.clean import clean
import subprocess

subprocess.call( ['make', 'README', 'README.org'] )


class MoreClean(clean):
    def run(self):
        clean.run(self)
        subprocess.call( ['make', 'clean'] )


setup(name         = 'gnuplotlib',
      version      = '0.7',
      author       = 'Dima Kogan',
      author_email = 'dima@secretsauce.net',
      url          = 'http://github.com/dkogan/gnuplotlib',
      description  = 'Gnuplot-based plotting for numpy',
      license      = 'LGPL-3+',
      py_modules   = ['gnuplotlib'],
      cmdclass     = {'clean': MoreClean})
