from setuptools import setup

setup(
   name='Bprice',
   version='1.0',
   description='A useful module',
   author='Man Foo',
   author_email='---',
   packages=['test.py'],  # same as name
   install_requires=['numpy','pandas'],
)
