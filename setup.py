from setuptools import setup
from chinesevocablist import __version__

setup(name='chinesevocablist',
      version=__version__,
      description='Programmatic interface to the Chinese Vocab List',
      url='http://github.com/kerrickstaley/Chinese-Vocab-List',
      author='Kerrick Staley',
      author_email='k@kerrickstaley.com',
      license='MIT',
      packages=['chinesevocablist'],
      zip_safe=False,
      install_requires=[
        'pyyaml>=3.12',
      ])
