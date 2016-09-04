#! /usr/bin/env python
# -*- coding: utf-8 -*-
# By i@BlahGeek.com at 10/03/2013

from io import BytesIO

from jinja2.ext import babel_extract as extract_jinja2
from pyjade import process as compile_jade
from pyjade.ext.jinja import Compiler as Jinja2Compiler


def extract_jade(fileobj, keywords, comment_tags, options):
    jinja = compile_jade(fileobj.read(), fileobj.name,
                         compiler=Jinja2Compiler)

    return extract_jinja2(BytesIO(jinja.encode('UTF-8')),
                          keywords, comment_tags, options)
