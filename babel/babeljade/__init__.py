#! /usr/bin/env python
# -*- coding: utf-8 -*-
# By i@BlahGeek.com at 10/03/2013

from StringIO import StringIO

from jinja2.ext import babel_extract as extract_jinja2
from pyjade import process as compile_jade
from pyjade.ext.jinja import Compiler as Jinja2Compiler


def extract_jade(fileobj, keywords, comment_tags, options):
    jinja = compile_jade(unicode(fileobj.read(), 'utf-8'), fileobj.name,
                         compiler=Jinja2Compiler)

    return extract_jinja2(StringIO(jinja.encode('utf-8')),
                          keywords, comment_tags, options)
