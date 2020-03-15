#!/usr/bin/python

from setuptools import setup

import re

version = None
with open("gnuplotlib.py", "r") as f:
    for l in f:
        m = re.match("__version__ *= *'(.*?)' *$", l)
        if m:
            version = m.group(1)
            break
if version is None:
    raise Exception("Couldn't find version in 'gnuplotlib.py'")


setup(name         = 'gnuplotlib',
      version      = version,
      author       = 'Dima Kogan',
      author_email = 'dima@secretsauce.net',
      url          = 'http://github.com/dkogan/gnuplotlib',
      description  = 'Gnuplot-based plotting for numpy',

      long_description = """gnuplotlib allows numpy data to be plotted using Gnuplot as a backend. As
much as was possible, this module acts as a passive pass-through to Gnuplot,
thus making available the full power and flexibility of the Gnuplot backend.""",

      license      = 'LGPL',
      py_modules   = ['gnuplotlib'],
      install_requires = ('numpy', 'numpysane >= 0.3'))
