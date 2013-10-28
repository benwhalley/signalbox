import os
from pip.req import parse_requirements
from distutils.core import setup

reqs = parse_requirements("requirements.txt")
install_reqs = [str(ir.req) for ir in reqs]

scripts = []
if 'DYNO' in os.environ:  # assume we are on heroku
  scripts = script + ['bin/pandoc']  # and use our bespoke pandoc build
    
setup(
    name='signalbox',
    version='0.1.1',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=['signalbox'],
    scripts=scripts,
    url='http://pypi.python.org/pypi/signalbox/',
    license='LICENSE.txt',
    description='Run longitudinal studies and RCTs over the web and phone.',
    long_description=open('README.txt').read(),
    install_requires=install_reqs
)