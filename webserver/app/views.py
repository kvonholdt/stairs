import logging
import hashlib
import json
import random

from app import app
from app import database as db
from app import util
from datetime import datetime
from datetime import timedelta
from flask import abort
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from os import path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if request.method == 'POST':
        entries_json = json.loads(request.data.decode('utf-8'))
        entries = map(lambda entry_json: db.Entry(timestamp=int(entry_json['timestamp']), count=int(entry_json['count']),
                                                  type=entry_json['type']), entries_json)
        db.merge_many(entries)
        return 'ok'
    else:
        return json.dumps(list(map(lambda entry: entry.as_dict(), db.all(db.Entry))))


@app.route('/entries_by_type', methods=['GET'])
def entries_by_type(type='stairs'):
    #return jsonify(db.find_entries_by_entry_type(type = type))
    return json.dumps(list(map(lambda entry: entry.as_dict(), db.find_entries_by_entry_type(type = type))))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db._current_session.remove()
