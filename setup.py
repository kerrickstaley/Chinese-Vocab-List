from setuptools import setup

setup(name='chinesevocablist',
      version='0.3.1',
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
