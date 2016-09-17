from flask import Flask, request
from sqlalchemy import exc

from analyzrr import db


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
