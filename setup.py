import os
from pip.req import parse_requirements
from setuptools import setup, find_packages

reqs = parse_requirements("requirements.txt", session=False)
install_reqs = filter(bool,[str(ir.req) for ir in reqs])

setup(
    name='signalbox',
    version='0.3.5.3',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://pypi.python.org/pypi/signalbox/',
    license='LICENSE.txt',
    description='Run longitudinal studies and randomised trials over the web and telephone.',
    long_description=open('README.txt').read(),
    install_requires=install_reqs,
)
