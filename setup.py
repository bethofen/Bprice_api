from setuptools import setup

setup(
   name='Bprice',
   version='1.0',
   description='A useful module',
   author='Man Foo',
   author_email='foomail@foo.example',
   packages=['Bprice'],  # same as name
   install_requires=['pandas','numpy'],
)
