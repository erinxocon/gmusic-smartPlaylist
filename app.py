# -*- coding: utf-8 -*-
import gmusicapi
import core

from flask import Flask, request, render_template, g

app = Flask(__name__)


@app.before_request
def before_request():
    g.api = gmusicapi.Mobileclient()


@app.teardown_request
def teardown_request(exception):
    g.api.logout()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return core.main(request.form)

    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5280)
