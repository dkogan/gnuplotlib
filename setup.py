#!/usr/bin/python

from setuptools import setup

setup(name         = 'gnuplotlib',
      version      = '0.13',
      author       = 'Dima Kogan',
      author_email = 'dima@secretsauce.net',
      url          = 'http://github.com/dkogan/gnuplotlib',
      description  = 'Gnuplot-based plotting for numpy',
      license      = 'LGPL-3+',
      py_modules   = ['gnuplotlib'],
      install_requires = ('numpy', 'numpysane >= 0.3'))
