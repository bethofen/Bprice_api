from setuptools import setup

setup(
   name='Bprice',
   version='1.0',
   description='A useful module',
   author='Man Food',
   author_email='---',
   packages=setuptools.find_packages(),
   packages=['Bprice'],  # same as name
   install_requires=['numpy','pandas'],
)
