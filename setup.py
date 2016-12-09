import codecs
from setuptools import setup


def readme():
    with codecs.open('README.rst', 'r', 'utf-8') as f:
        return f.read()

def version():
    with open('dcard/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.replace("'", '').split()[-1]

setup(
    name='dcard-spider',
    version=version(),
    url='http://github.com/leVirve/dcard-spider',
    description='A spider for Dcard through its newest API.',
    long_description=readme(),
    author='Salas leVirve',
    author_email='gae.m.project@gmail.com',
    license='MIT',
    platforms='any',
    packages=['dcard'],
    zip_safe=False,
    keywords='Dcard crawler spider',
    entry_points={
        'console_scripts': ['dcard=dcard.cli:main'],
    },
    install_requires=[
        'six',
        'requests'
    ],
    dependency_links=[
        'https://github.com/leVirve/prequests/tarball/master#egg=prequests-0.1.1'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Terminals',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
