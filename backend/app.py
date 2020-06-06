# from werkzeug import secure_filename
import atexit
import copy
import json
import logging
import os
import pathlib
import wave
from io import BytesIO, StringIO
from threading import Thread

import pika
from cloudant import Cloudant
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask.blueprints import Blueprint
from flask_sockets import Sockets
from gevent import pywsgi

from backend.dl_model.ogg_to_wav import convert
from backend.dl_model.recording import deep_learning_model
from backend.messaging.rmq import Connecter

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

load_dotenv()

conn = Connecter()
db = None
urls = Blueprint("urls", "urls", "static")
ws = Blueprint('ws', __name__)


client = None

sockets = Sockets()
sockets.all_conns = []

logging.info('connected to RMQ')


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 5000))


@urls.route('/')
def root():
    return urls.send_static_file('index.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */


@urls.route('/api/visitors', methods=['GET'])
def get_visitor():
    if client:
        return jsonify(list(map(lambda doc: doc['name'], db)))
    else:
        logging.warning('No database')
        return jsonify([])

# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */


@urls.route('/api/visitors', methods=['POST'])
def put_visitor():
    user = request.json['name']
    data = {'name': user}
    if client:
        my_document = db.create_document(data)
        data['_id'] = my_document['_id']
        return jsonify(data)
    else:
        logging.info('No database')
        return jsonify(data)


@urls.route('/upload', methods=['GET', 'POST'])
def uploader():
    if request.method == "GET":
        return render_template("upload.html")
    if request.method == 'POST':
        f = request.files['file']
        username = request.form.get('username', 'anonymous')
        buffer = f.read()
        extension = f.filename.split(".")[1]

        conn.produce(f'hello-{extension}', buffer, {"username": username})
        sample = buffer
        if extension == "ogg":
            sample = convert(BytesIO(sample))
        return jsonify({"message": "processing..."})


@ws.route('/transcript')
def transcript_socket(socket):
    global sockets
    sockets.all_conns.append(socket)
    while not socket.closed:
        print("not closed")
        message = socket.receive()
        logging.info(f"Received: {message}")
        socket.send(message)


@atexit.register
def shutdown():
    if client:
        client.disconnect()


def callback_results(ch, method, properties, body):
    logging.info(body)
    global sockets
    utf_body = str(body, encoding='utf-8')
    to_remove = []
    for conn in sockets.all_conns:
        if not conn.closed:
            conn.send(utf_body)
        else:
            to_remove.append(conn)
    for t in to_remove:
        sockets.all_cons.remove(t)


def results_thread(app):
    logging.info('Listening for result transcript messages')
    results_conn = Connecter()
    results_conn.init_app(app)
    results_conn.listen('results', callback_results)


def create_app():

    app = Flask(__name__, static_url_path='')

    app.config.from_object("backend.config.Config")

    # Init the deep learning model
    # deep_learning_model.init_app(app)
    # Init the RMQ connection
    conn.init_app(app)
    sockets.init_app(app)

    conn.define_queue("hello-wav")
    conn.define_queue("hello-ogg")

    sockets.register_blueprint(ws)
    app.register_blueprint(urls)

    db_name = 'mydb'

    if 'VCAP_SERVICES' in os.environ:
        vcap = json.loads(os.getenv('VCAP_SERVICES'))
        print('Found VCAP_SERVICES')
        if 'cloudantNoSQLDB' in vcap:
            creds = vcap['cloudantNoSQLDB'][0]['credentials']
            user = creds['username']
            password = creds['password']
            url = 'https://' + creds['host']
            client = Cloudant(user, password, url=url, connect=True)
            db = client.create_database(db_name, throw_on_exists=False)
    elif "CLOUDANT_URL" in os.environ:
        client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'],
                          url=os.environ['CLOUDANT_URL'], connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
    elif os.path.isfile('vcap-local.json'):
        with open('vcap-local.json') as f:
            vcap = json.load(f)
            print('Found local VCAP_SERVICES')
            creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
            user = creds['username']
            password = creds['password']
            url = 'https://' + creds['host']
            client = Cloudant(user, password, url=url, connect=True)
            db = client.create_database(db_name, throw_on_exists=False)

    return app


app = create_app()
results_thread = Thread(target=results_thread, args=(app,), daemon=True)
results_thread.start()


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=port, debug=True)
if __name__ == "__main__":
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)
    server.serve_forever()
