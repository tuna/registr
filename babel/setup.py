'''
An adhoc pybabel extractor for jade sources. It assumes

* jade files are encoded in utf-8
* the conversion target is jinja2
'''

from setuptools import setup

if __name__ == '__main__':
    setup(
        name='babeljade',
        entry_points={
            'babel.extractors': ['jade = babeljade:extract_jade', ]
        }
    )
