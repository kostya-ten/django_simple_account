import io
import os

from setuptools import find_packages, setup

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with io.open("README.rst", encoding="UTF-8") as readme:
    long_description = readme.read()

setup(
    name='django-simple-account',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    license='Apache License 2.0',
    description="Django simple account",
    long_description=long_description,
    url='https://github.com/kostya-ten/django_simple_account/',
    author='Kostya Ten',
    author_email='kostya@yandex.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: SQL',
        'License :: OSI Approved :: Apache Software License',
    ],
    project_urls={
        'Documentation': 'https://github.com/kostya-ten/django_simple_account/',
        'Source': 'https://github.com/kostya-ten/django_simple_account/',
        'Tracker': 'https://github.com/kostya-ten/django_simple_account/issues/',
        'Funding': 'https://www.paypal.me/kostyaten/',
    },
    python_requires='~=3.6',
    install_requires=required,
)
