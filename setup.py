#!/usr/bin/python

from distutils.core import setup

setup(name         = 'gnuplotlib',
      version      = '0.12',
      author       = 'Dima Kogan',
      author_email = 'dima@secretsauce.net',
      url          = 'http://github.com/dkogan/gnuplotlib',
      description  = 'Gnuplot-based plotting for numpy',
      license      = 'LGPL-3+',
      py_modules   = ['gnuplotlib'],
      cmdclass     = {})
