from setuptools import setup

setup(name='chinese_vocab_list',
      version='0.2.1',
      description='Programmatic interface to the Chinese Vocab List',
      url='http://github.com/kerrickstaley/chinese_vocab_list',
      author='Kerrick Staley',
      author_email='k@kerrickstaley.com',
      license='MIT',
      packages=['chinese_vocab_list'],
      package_data={'chinese_vocab_list': ['chinese_vocab_list.yaml']},
      zip_safe=False,
      install_requires=[
        'pyyaml>=3.12',
      ])
