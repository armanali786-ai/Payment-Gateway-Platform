from setuptools import setup, find_packages

setup(
    name='nexapay',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['requests'],
    description='NexaPay Payment Gateway SDK',
    author='NexaPay',
)
