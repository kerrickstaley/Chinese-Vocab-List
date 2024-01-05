from setuptools import setup
from pathlib import Path

version = {}
with open('chinesevocablist/version.py') as fp:
  exec(fp.read(), version)

repo_root = Path(__file__).parent
long_description = (repo_root / 'README.md').read_text()

setup(name='chinesevocablist',
      version=version['__version__'],
      description='Programmatic interface to the Chinese Vocab List',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/kerrickstaley/Chinese-Vocab-List',
      author='Kerrick Staley',
      author_email='k@kerrickstaley.com',
      license='MIT',
      packages=['chinesevocablist'],
      zip_safe=False,
      install_requires=[
        'pyyaml>=3.12',
      ])
