import os
from distutils.core import setup

scripts = []
if 'DYNO' in os.environ:  # assume we are on heroku
  scripts = script + ['bin/pandoc']  # and use our bespoke pandoc build
    
setup(
    name='signalbox',
    version='0.1.0',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=['signalbox'],
    scripts=scripts,
    url='http://pypi.python.org/pypi/signalbox/',
    license='LICENSE.txt',
    description='Run longitudinal studies and RCTs over the web and phone.',
    long_description=open('README.txt').read(),
    install_requires=open('requirements.txt').read().split("\n")
)