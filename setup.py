from setuptools import setup

setup(
   name='Bprice',
   version='1.5',
   description='package for cal indicator',
   author='beethofen',
   # author_email='---',
   # packages=setuptools.find_packages(),
   packages=['Bprice'],  # same as name
   install_requires=['numpy','pandas'],
)
