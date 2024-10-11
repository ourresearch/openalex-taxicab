from setuptools import setup

def parse_requirements(filename):
    with open(filename) as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('git+'):
                    pkg_name = line.split('#egg=')[-1]
                    requirements.append(f'{pkg_name} @ {line}')
                else:
                    requirements.append(line)
    return requirements

setup(
    name='openalex-taxicab',
    version='0.1',
    packages=['openalex_taxicab', 'openalex_taxicab.legacy'],
    url='https://github.com/ourresearch/openalex-taxicab',
    install_requires=parse_requirements('./requirements.txt'),
    license='',
    author='',
    author_email='',
    description=''
)
