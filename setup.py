from setuptools import setup, find_packages
setup(
   name='Bprice',
   version='3',
   description='package for cal indicator',
   author='beethofen',
   # packages=find_packages(),
   # author_email='---',
   # packages=setuptools.find_packages(),
   packages=['src','src.LorentzianClassification'],  # same as name
   install_requires=['numpy','pandas'],
)
