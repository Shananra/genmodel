from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='genmodel',
      version=version,
      description="Automatically populate database models by reading from the database",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Adam Weber',
      author_email='toastbusters@gmail.com',
      url='https://github.com/Shananra',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
            'console_scripts':['genmodel = genmodel.genmodel:main']  
        },
      )
