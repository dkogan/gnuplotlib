#!/usr/bin/python

from setuptools import setup

setup(name         = 'gnuplotlib',
      version      = '0.14',
      author       = 'Dima Kogan',
      author_email = 'dima@secretsauce.net',
      url          = 'http://github.com/dkogan/gnuplotlib',
      description  = 'Gnuplot-based plotting for numpy',

      long_description = """gnuplotlib allows numpy data to be plotted using Gnuplot as a backend. As
much as was possible, this module acts as a passive pass-through to Gnuplot,
thus making available the full power and flexibility of the Gnuplot backend.""",

      license      = 'LGPL-3+',
      py_modules   = ['gnuplotlib'],
      install_requires = ('numpy', 'numpysane >= 0.3'))
