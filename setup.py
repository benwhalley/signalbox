import os
from pip.req import parse_requirements
from distutils.core import setup

reqs = parse_requirements("requirements.txt")
install_reqs = [str(ir.req) for ir in reqs]

scripts = []
if 'DYNO' in os.environ:  # assume we are on heroku
  scripts = scripts + ['bin/pandoc']  # and use our bespoke pandoc build

setup(
    name='signalbox',
    version='0.1.7',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=['signalbox', 'ask', 'twiliobox'],
    scripts=scripts,
    url='http://pypi.python.org/pypi/signalbox/',
    license='LICENSE.txt',
    description='Run longitudinal studies and randomised trials over the web and telephone.',
    long_description=open('README.txt').read(),
    install_requires=install_reqs,
    entry_points = {
            'console_scripts': [
                'bootstrap_signalbox = signalbox.utilities.bootstrap:bootstrap_signalbox',
            ]
    }
)