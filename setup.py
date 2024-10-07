from setuptools import setup

setup(
    name='openalex-taxicab',
    version='0.1',
    packages=['openalex_taxicab'],
    url='https://github.com/ourresearch/openalex-taxicab',
    install_requires=[line for line in open('./requirements.txt').read().splitlines() if len(line) > 3],
    license='',
    author='',
    author_email='',
    description=''
)
