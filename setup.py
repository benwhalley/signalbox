import os
from pip.req import parse_requirements
from setuptools import setup, find_packages


reqs = parse_requirements("requirements.txt")
install_reqs = [str(ir.req) for ir in reqs]

<<<<<<< HEAD
scripts = ['bin/setup_signalbox']
if 'DYNO' in os.environ:  # assume we are on heroku
  scripts = scripts + ['bin/pandoc']  # and use our bespoke pandoc build
=======
scripts = ['bin/setup_signalbox.sh']
>>>>>>> e0d61f7949c08d2c7bf2654d52c7d488ea31dd9f

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
                'setup_signalbox_heroku = signalbox.utilities.bootstrap:setup_signalbox_heroku',
            ]
    }
)