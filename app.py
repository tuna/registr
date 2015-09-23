#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from flask import Flask, request, g, render_template, make_response, escape
from flask.ext.babel import lazy_gettext as _, Babel
from babel import Locale
from threading import Lock
from flask_wtf import Form
from wtforms import StringField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Regexp, Email, Optional
import csv
import json
import random
import coffeescript
import pyjade

CSV_FILE = "registration-2014-2.csv"

app = Flask("tuna-registration")
babel = Babel()
lock = Lock()

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.jinja_env.globals['_'] = _
app.jinja_env.globals['unicode'] = unicode
app.config['BABEL_DEFAULT_LOCALE']='zh_CN'

babel.init_app(app)

all_locales = babel.list_translations() + [Locale('en', 'US')]

# The original coffeescript filter registered by pyjade is wrong for
# its results are wrapped with `script` tag
@pyjade.register_filter('coffeescript')
def coffeescript_filter(text, ast):
    return coffeescript.compile(text)

@babel.localeselector
def get_locale():
    # Try to retrieve locale from query strings.
    locale = request.args.get('locale', None)
    if locale is not None:
        return locale

    # print type(request.accept_languages.best_match(str(
    locale = request.accept_languages.best_match(
            list(str(locale) for locale in all_locales))
    if locale is not None:
        return locale

    # Fall back to default locale
    return None

class JoinForm(Form):
    name = StringField(_(u'Name'), [InputRequired()])
    department = StringField(_(u'Department'), [InputRequired()])
    stu_number = StringField(_(u'Student Number'), [Optional()])
    phone = StringField(_(u'Phone'), [InputRequired(), Regexp('\d{11}', message=_(u'This is not valid phone number'))])
    email = EmailField(_(u'Email'), [Email()])
    gender = RadioField(
            _(u'Gender'),
            choices = [
                (u'男', _(u'Boy')),
                (u'女', _(u'Girl'))])

@app.route('/', methods=['GET', 'POST'])
def join():
    form = JoinForm(csrf_enabled=False)
    success = False
    if form.validate_on_submit():
        # save data
        success = True
    return render_template(
            'join.jade',
            form=form,
            success=success,
            all_locales=all_locales)

def get_csv_writer():
    if not hasattr(g, 'csv_file'):
        f = open(CSV_FILE, 'a+b')
        g.csv_file = f

    return csv.writer(g.csv_file)


if __name__ == "__main__":
    with open(CSV_FILE, 'rb') as f:
        r = csv.reader(f)
        for row in r:
            row = map(lambda x: x.decode('utf-8'), row)

    app.run(host='0.0.0.0', debug=True)

# vim: ts=4 sw=4 sts=4 expandtab
