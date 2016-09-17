import datetime

from flask import Flask, request
from sqlalchemy import exc
import random

from analyzrr import db, stats


# run with:
#   FLASK_DEBUG=1 FLASK_APP=path/to/analyzrr/app.py flask run --host=0.0.0.0
api = Flask(__name__)
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
    # TODO: inlcude network status
    process, window, time_event = stats.get_last_used_application(session)
    network = stats.get_network_status(session)

    is_idle = datetime.datetime.now() - time_event > stats.IDLE_TIMEOUT

    is_work_process = stats.APP_CLASSIFIERS['work'].search(process.name)
    is_work_window = stats.WINDOW_CLASSIFIERS['work'].search(window.title)
    is_work_app = is_work_process or is_work_window

    is_personal_process = stats.APP_CLASSIFIERS['personal'].search(process.name)
    is_personal_window = stats.WINDOW_CLASSIFIERS['personal'].search(window.title)
    is_personal_app = is_personal_process or is_personal_window

    # XXX(fubu): In the following decision tree the conditions have to be met
    #   exactly, otherwise the decision has to fall through to "undecided".
    if network is None or network.action == "disconnect":
        # network=none && app=personal && idle=True  => "not-working"
        # network=none && app=personal && idle=False => "not-working"
        # network=none && app=work && idle=True      => "not-working"
        # network=none && app=work && idle=False     => "productive"
        if is_work_app:
            return "not-working" if is_idle else "productive"
        elif is_personal_app:
            return "not-working"

    elif network.location == "personal":
        # network=personal && app=personal && idle=True  => "not-working"
        # network=personal && app=personal && idle=False => "not-working"
        # network=personal && app=work && idle=True      => "not-working"
        # network=personal && app=work && idle=False     => "productive"
        if is_work_app:
            return "not-working" if is_idle else "productive"
        elif is_personal_app:
            return "not-working"

    elif network.location == "work":
        # network=work && app=personal && idle=True  => "unproductive"
        # network=work && app=personal && idle=False => "unproductive"
        # network=work && app=work && idle=True      => "unproductive"
        # network=work && app=work && idle=False     => "productive"
        if is_work_app:
            return "unproductive" if is_idle else "productive"
        elif is_personal_app:
            return "unproductive"

    return "undecided"


@api.route('/workperiods')
def work_periods():
    pass
