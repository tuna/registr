#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import coffeescript
import pyjade
import sendgrid
import datetime
import random
import smtplib
from flask import Flask, request, render_template, redirect, session
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView as _ModelView
from flask_admin.base import AdminViewMeta
from flask_babel import lazy_gettext as _, Babel
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_env_settings import Settings
from babel import Locale
from flask_wtf import Form
from wtforms import StringField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, Optional
from sqlalchemy.exc import IntegrityError
from email.mime.text import MIMEText


# The original coffeescript filter registered by pyjade is wrong for
# its results are wrapped with `script` tag
@pyjade.register_filter('coffeescript')
def coffeescript_filter(text, ast):
    return coffeescript.compile(text)


app = Flask("tuna-registration")

app.config.update(
    SQLALCHEMY_TRACK_MODIFICATIONS=False,  # As suggested by flask_sqlalchemy
)

# retrieve configuration from environment
Settings(app, rules={
    "BABEL_DEFAULT_LOCALE": (str, "en_US"),
    "SQLALCHEMY_DATABASE_URI": str,
    "BASIC_AUTH_USERNAME": str,
    "BASIC_AUTH_PASSWORD": str,
    "SECRET_KEY": str,
    "DEBUG": (bool, False),
    "SENDGRID_KEY": str,
    "SMTP_SERVER": str,
    "SMTP_USER": str,
    "SMTP_PASS": str,
})

babel = Babel()

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.jinja_env.globals['_'] = _
babel.init_app(app)

all_locales = babel.list_translations() + [Locale('en', 'US')]


# setup smtp
def make_smtp():
    smtp = smtplib.SMTP(app.config['SMTP_SERVER'])
    status, msg = smtp.login(
        user=app.config['SMTP_USER'],
        password=app.config['SMTP_PASS'])
    if status != 235:
        raise Exception("Fail to login: {msg}".format(msg=msg))
    return smtp


def send_mail(to):
    today = datetime.date.today()
    with open("mail_template.txt") as template:
        msg = MIMEText(template.read().format(today=today))
    msg['Subject'] = "Welcome to TUNA!"
    msg['From'] = app.config['SMTP_USER']
    msg['To'] = to
    with make_smtp() as smtp:
        smtp.send_message(msg)


def get_sg():
    return sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_KEY'])


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


# Models
db = SQLAlchemy(app)


class Candidate(db.Model):
    __tablename__ = 'Candidate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    department = db.Column(db.String(128), nullable=False)
    stu_number = db.Column(db.String(16), unique=False)
    phone = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(120), unique=True)
    gender = db.Column(db.Enum('男', '女'))
    team = db.Column(db.Enum('DevOps', 'Organizer', 'Publicity', 'Jiangyou'))


class JoinForm(Form):
    name = StringField(_('Name'), [InputRequired()])
    department = StringField(_('Department'), [InputRequired()])
    stu_number = StringField(_('Student Number (Optional)'), [Optional()])
    phone = StringField(_('Phone'), [InputRequired()])
    email = EmailField(_('Email'), [Email()])
    gender = RadioField(
        _('Gender'),
        choices=[
            ('男', _('Boy')),
            ('女', _('Girl'))
        ])
    team = RadioField(
        label=_('Team Preference'),
        choices=[
            ('DevOps', _('DevOps Team')),
            ('Organizer', _('Organizer Team')),
            ('Publicity', _('Publicity Team')),
            ('Jiangyou', _('Member Team')),
        ],
    )


@app.route('/', methods=['GET', 'POST'])
def join():
    form = JoinForm(csrf_enabled=False)
    if form.team.data == 'None':
        form.team.data = random.choice(form.team.choices)[0]

    err_msg = None
    if request.method == "POST" and form.validate():
        # save data
        c = Candidate()
        form.populate_obj(c)
        db.session.add(c)
        try:
            db.session.commit()
            send_mail(form.email.data)
        except IntegrityError:
            err_msg = _('You have already registered.')
        except smtplib.SMTPRecipientsRefused:
            err_msg = _('Mail is refused.')
        except:
            err_msg = _('Unknown Error 0x233333')
        else:
            session["success"] = True
            return redirect("/")

    success = session.pop("success", False)

    return render_template(
        'join.jade',
        form=form,
        success=success,
        err_msg=err_msg,
        all_locales=all_locales)


# A basic admin interface to view candidates
basic_auth = BasicAuth(app)


class LimitAccessMeta(AdminViewMeta):
    def __new__(cls, name, bases, d):
        def find_method(m):
            for base in bases:
                try:
                    return getattr(base, m)
                except AttributeError:
                    pass
            raise AttributeError("No bases have method '{}'".format(m))

        for view, url, methods in [
                ('index_view', '/', None),
                ('create_view', '/new/', ('GET', 'POST')),
                ('edit_view', '/edit/', ('GET', 'POST')),
                ('details_view', '/details/', None),
                ('delete_view', '/delete/', ('POST',)),
                ('action_view', '/action/', ('POST',)),
                ('export', '/export/<export_type>/', None)]:
            if methods is not None:
                d[view] = basic_auth.required(
                    expose(url, methods=methods)(
                        find_method(view)))
            else:
                d[view] = basic_auth.required(
                    expose(url)(
                        find_method(view)))
        return super().__new__(cls, name, bases, d)


class ModelView(_ModelView, metaclass=LimitAccessMeta):
    can_export = True
    export_types = ['json', 'yaml', 'csv', 'xls', 'xlsx']


admin = Admin(app, template_mode="bootstrap3")
admin.add_view(ModelView(Candidate, db.session))

# Boot-time initializations
try:
    db.create_all()  # Create all tables if not existed
except:
    # this may fail when there are many process, it doesn't matter
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

# vim: ts=4 sw=4 sts=4 expandtab
