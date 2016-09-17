import datetime

from flask import Flask, request, json, jsonify
from sqlalchemy import exc
import random

from analyzrr import db, stats


class RfcDatetimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(RfcDatetimeJsonEncoder, self).default(obj)


# run with:
#   FLASK_DEBUG=1 FLASK_APP=path/to/analyzrr/app.py flask run --host=0.0.0.0
api = Flask(__name__)
api.json_encoder = RfcDatetimeJsonEncoder
session = db.get_session()

@api.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

@api.route('/')
def hello_world():
    return "Hello, James!"

@api.route('/ingest', methods=['POST'])
def ingest_data():
    payload = request.get_json()

    if 'spyData' in payload:
        # spyData = "lines_of_sql; delimited by ;\n"
        sql = payload['spyData']
        for row in sql.split(";\n"):
            session.execute(row.replace("INSERT INTO", "INSERT OR IGNORE INTO", 1))

        session.commit()

    if 'network' in payload:
        # network = {
        #   'fingerprint': "e.g. SSID",
        #   'kind': "work|personal",
        #   'action': "connect|disconnect"
        # }
        network = payload['network']

        network_location = db.NetworkLocation(
            fingerprint=network['fingerprint'],
            kind=network['kind']
        )
        try:
            session.add(network_location)
            session.flush()
        except exc.IntegrityError as e:
            session.rollback()
            network_location = session.query(db.NetworkLocation).filter_by(
                fingerprint=network['fingerprint']
            ).first()
            network_location.kind = network['kind']

        network_entry = db.Network(action=network['action'], location=network_location)
        session.add(network_entry)
        session.commit()

    return "OK!"

@api.route('/workstatus')
def work_status():
    process, window, time_event = stats.get_last_used_application(session)
    network = stats.get_network_status(session)
    classification = stats.classify_event(process, window, network, time_event)
    return classification

@api.route('/workperiods')
def work_periods():
    events = stats.get_events_for_a_day(session, int(request.args.get('delta', 0)))
    intervals = stats.create_intervals(session, events)
    work_periods = stats.flatten_intervals(intervals)
    return jsonify(work_periods)
