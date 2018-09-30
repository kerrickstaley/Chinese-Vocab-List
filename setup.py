from setuptools import setup

version = {}
with open('chinesevocablist/version.py') as fp:
  exec(fp.read(), version)

setup(name='chinesevocablist',
      version=version['__version__'],
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
