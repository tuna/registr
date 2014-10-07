#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from flask import Flask, request, g, render_template, make_response, escape
from threading import Lock
import csv
import json
import random

CSV_FILE = "registration-2014-2.csv"

app = Flask("tuna-registration")
lock = Lock()

candidates = []

@app.route('/', methods=["GET"])
def index():
    return render_template("index.jinja2")


@app.route('/checkin', methods=['POST'])
def checkin():
    global candidates
    form = request.json
    if form['name'] == '':
        form['name'] = u"匿名者"
    with lock:
        writer = get_csv_writer()
        writer.writerow(
            map(lambda x: x.encode('utf-8'),
                [form['name'], form['email'], ':'.join(form['from'])])
        )
        candidates.append((form['name'], form['email']))
    return "OK"


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


@app.route('/luckydog')
def luckydog():
    return render_template("lucky.jinja2")


@app.route('/choice')
def choose_luckydog():
    random.shuffle(candidates)
    lucky_dog = candidates.pop()
    print lucky_dog
    return json.dumps({"name": lucky_dog[0], "email": lucky_dog[1]})


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
            candidates.append((row[0], row[1]))

    app.run(host='0.0.0.0', debug=True)

# vim: ts=4 sw=4 sts=4 expandtab
