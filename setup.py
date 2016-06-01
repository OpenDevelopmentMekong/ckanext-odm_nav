from setuptools import setup, find_packages
import sys, os

version = '1.9.1'

setup(
    name='ckanext-odm_nav',
    version=version,
    description="OD Mekong CKAN's extension containing new nav concept",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Christopher Krempel',
    author_email='christopher@aeviator.cc',
    url='http://www.aeviator.cc',
    license='AGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    package_dir={'odm_nav': 'ckanext/odm_nav'},
    package_data={'odm_nav': ['odm-taxonomy/*.json']},
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_nav=ckanext.odm_nav.plugin:OdmNavPlugin
    ''',
)
