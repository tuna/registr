#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from flask import Flask, request, g, render_template, make_response, escape
from flask.ext.babel import lazy_gettext as _, Babel
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
babel = Babel(app)
lock = Lock()

# The original coffeescript filter registered by pyjade is wrong for
# its results are wrapped with `script` tag
@pyjade.register_filter('coffeescript')
def coffeescript_filter(text, ast):
    return coffeescript.compile(text)

class JoinForm(Form):
    name = StringField(_('Name'), [InputRequired()])
    department = StringField(_('Department'), [InputRequired()])
    stu_number = StringField(_('Student Number'), [Optional()])
    phone = StringField(_('Phone'), [InputRequired(), Regexp('\d{11}', message=_('This is not valid phone number'))])
    email = EmailField(_('Email'), [Email()])
    gender = RadioField(
            _('Gender'),
            choices = [
                ('男', _('Boy')),
                ('女', _('Girl'))])

@app.route('/', methods=['GET', 'POST'])
def base():
    form = JoinForm(csrf_enabled=False)
    success = False
    if form.validate_on_submit():
        # save data
        success = True
    return render_template(
            'join.jade', form=form, success=success)

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template('join.jinja2')

    assert request.method == 'POST'
    with lock:
        writer = get_csv_writer()
        form = request.json
        writer.writerow(
            map(lambda x: x.encode('utf-8'),
                [form['name'], form['gender'], form['stu_number'],
                 form['department'], form['class'], form['email'], form['phone']
                 ])
        )
    return 'OK'

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

    # app.jinja_env.line_statement_prefix = '%'
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
    app.jinja_env.globals['_'] = _
    # app.config['BABEL_DEFAULT_LOCALE']='zh_CN'
    app.run(host='0.0.0.0', debug=True)

# vim: ts=4 sw=4 sts=4 expandtab
