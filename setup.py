from setuptools import setup

setup(
   name='Bprice',
   version='1.5',
   description='package for cal indicator',
   author='beethofen',
   packages=find_packages(),
    include_package_data=True,
   # author_email='---',
   # packages=setuptools.find_packages(),
   packages=['Bprice'],  # same as name
   install_requires=['numpy','pandas'],
)
