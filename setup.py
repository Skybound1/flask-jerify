"""
Flask-Jerify
------------

"JSON Verify". Provides a decorator to verify request data is valid JSON.
Optionally validates the JSON against a JSON Schema.
"""
from setuptools import setup


setup(
    name='Flask-Jerify',
    packages=['flask_jerify'],
    version='0.0.12',
    url='http://github.com/alx-k/flask-jerify',
    license='BSD',
    author='Alexandre Kaskasoli',
    author_email='alexkaskasoli@hotmail.om',
    description='Validate JSON requests against schemas',
    long_description=__doc__,
    py_modules=['flask_jerify'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'jsonschema>=2.6.0'
    ],
    keywords=['flask', 'json', 'schema', 'validator', 'jsonschema'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
