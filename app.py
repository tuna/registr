#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from flask import Flask, request, g, render_template, redirect, session
from flask_babel import lazy_gettext as _, Babel
from babel import Locale
from threading import Lock
from flask_wtf import Form
from wtforms import StringField, RadioField, FileField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, Optional
import csv
import coffeescript
import pyjade
import base64

CSV_FILE = "registration-2016-fall.csv"

app = Flask("tuna-registration")
babel = Babel()
lock = Lock()

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.jinja_env.globals['_'] = _
app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
babel.init_app(app)

app.secret_key = '29898604a6b00b7f8c1cf65183289321a6c8b7f1'

all_locales = babel.list_translations() + [Locale('en', 'US')]


def cmp(a, b):
    (a > b) - (a < b)


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
        session["locale"] = locale
        return locale

    locale = session.get('locale', None)
    if locale is not None:
        return locale

    locale = request.accept_languages.best_match(
        list(str(locale) for locale in all_locales))
    if locale is not None:
        return locale

    # Fall back to default locale
    return None


class JoinForm(Form):
    image = FileField(_(u'image'), [Optional()])
    pic_took = HiddenField(_(u'pic_took'), [InputRequired()])
    name = StringField(_(u'Name'), [InputRequired()])
    department = StringField(_(u'Department'), [InputRequired()])
    stu_number = StringField(_(u'Student Number (Optional)'), [Optional()])
    phone = StringField(_(u'Phone'), [InputRequired()])
    email = EmailField(_(u'Email'), [Email()])
    gender = RadioField(
        _(u'Gender'),
        choices=[
            (u'男', _(u'Boy')),
            (u'女', _(u'Girl'))
        ])


@app.route('/', methods=['GET', 'POST'])
def join():
    form = JoinForm(csrf_enabled=False)
    if request.method == "POST":
        session["success"] = False
        if form.validate():
            # save data
            with lock:
                writer = get_csv_writer()
                writer.writerows(
                    map(lambda x: x.encode('utf-8'),
                        [form.name.data, form.gender.data,
                         form.stu_number.data, form.department.data,
                         form.email.data, form.phone.data])
                )
            head = "data:image/png;base64,"
            if cmp(form.pic_took.data[:22], head) == 0:
                img_encoded = form.pic_took.data[22:]
                img = base64.b64decode(img_encoded)
                file_name = "pics/{}_{}.png".format(
                    form.name.data, form.stu_number.data)
                fp = open(file_name, 'w')
                fp.write(img)
                fp.flush()
                fp.close()

            session["success"] = True
            return redirect("/")

    success = session.get("success", False)
    session["success"] = False
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

    sslContext = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', debug=True, ssl_context=sslContext)

# vim: ts=4 sw=4 sts=4 expandtab
