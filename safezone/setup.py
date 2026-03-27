"""
Setup script for the SafeZone library.
Enables installation via pip install -e . for local development.
Author: Adithya Reddy Madireddy
"""

from setuptools import setup, find_packages

setup(
    name='safezone',
    version='1.0.0',
    author='Adithya Reddy Madireddy',
    author_email='adithya.madireddy@student.ncirl.ie',
    description='A neighbourhood safety analysis and incident management library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/adithya-madireddy/safezone',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[],
    extras_require={
        'dev': ['pytest>=8.0', 'pytest-cov>=5.0']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
    ],
)
