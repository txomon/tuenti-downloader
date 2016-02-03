from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='tuenti-downloader',
    version='1.0.0',
    description='Tuenti photo downloader',
    author='Javier Domingo Cansino',
    author_email='javierdo1@gmail.com',
    long_description=long_description,
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['python-tuenti'],
    entry_points={
        'console_scripts': [
            'td=td:main'
        ]
    }
)
