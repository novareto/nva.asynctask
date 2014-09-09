# -*- coding: utf-8 -*-
"""
This module contains the tool of nva.calendarview
"""

from setuptools import setup, find_packages

version = '1.0'


setup(
    name='nva.asynctask',
    version=version,
    description="",
    long_description="",
    classifiers=[
        'Intended Audience :: Developers',
        ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='ZPL',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['nva'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'ZODB.interfaces.IDatabase',
        'celery',
        'kombu',
        'transaction',
        'zope.app.publication',
        'zope.component',
        ],
    entry_points="""
      # -*- entry_points -*
      """,
    )
