# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name='transcriber-server',
    version='1.0.0',
    description='WebRTC server for the HackYeah2020 hackathon',
    url='https://github.com/TranscriberApp/transcriber',
    license='Apache-2.0'
)
