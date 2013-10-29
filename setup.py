import os
from pip.req import parse_requirements
from setuptools import setup, find_packages


reqs = parse_requirements("requirements.txt")
install_reqs = [str(ir.req) for ir in reqs]

scripts = ['bin/setup_signalbox.sh']
if 'DYNO' in os.environ:  # assume we are on heroku
  scripts = scripts + ['bin/pandoc']  # and use our bespoke pandoc build

setup(
    name='signalbox',
    version='0.1.10',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    scripts=scripts,
    url='http://pypi.python.org/pypi/signalbox/',
    license='LICENSE.txt',
    description='Run longitudinal studies and randomised trials over the web and telephone.',
    long_description=open('README.txt').read(),
    install_requires=install_reqs,
    entry_points = {
            'console_scripts': [
                'signalbox_example_project_dir = signalbox.utilities.bootstrap:example_project_dir',
                'signalbox_heroku_quickstart = signalbox.utilities.bootstrap:signalbox_heroku_quickstart',
            ]
    }
)