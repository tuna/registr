Registr
=======

A "simple" web-based registering tool.

Installation
------------

Create a virtualenv if desired:

```
$ virtualenv venv
$ source venv/bin/activate
(venv)$
```

Install dependencies:

```
$ pip install -r requirements.txt
```

Run it!

```
$ python app.py
```

Or run it with `gunicorn`:
```
$ pip install gunicorn gevent
$ gunicorn --worker-class=gevent --workers=10 --log-level debug --access-logfile - --reload app:app
```

i18n
----

See the `i18n` script

NOTE: If dependencies are installed in virtualenv, remember to run `i18n` in virtualenv.
