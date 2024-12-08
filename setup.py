from setuptools import setup, find_packages
setup(
   name='Bprice',
   version='1.5',
   description='package for cal indicator',
   author='beethofen',
   # packages=find_packages(),
   # author_email='---',
   packages=setuptools.find_packages(),
   packages=['Bprice'],  # same as name
   install_requires=['numpy','pandas'],
)
