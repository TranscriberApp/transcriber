# from werkzeug import secure_filename
import atexit
import copy
import json
import logging
import os
import pathlib
import wave
from datetime import datetime
from io import BytesIO, StringIO
from threading import Thread

import pika
from cloudant import Cloudant
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, abort, send_file
from flask.blueprints import Blueprint
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from backend.dl_model.ogg_to_wav import convert, convert_wav_to_ogg
from backend.dl_model.recording import deep_learning_model
from backend.messaging.cloud_db import ibm_db

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

load_dotenv()

db = None
urls = Blueprint("urls", "urls", "static")
ws = Blueprint('ws', __name__)


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


@urls.route('/api/files', methods=['GET'])
def get_uploads():
    return jsonify(list(map(lambda doc: ibm_db.deblob_doc(doc), ibm_db.db)))


@urls.route('/api/files', methods=['DELETE'])
def delete_uploads():
    for f in ibm_db.db:
        f.delete()
    return jsonify({"deleted": True})


@urls.route("/api/files/<file_id>/attachment", methods=['GET'])
def download_attachment(file_id):
    extracted_file = ibm_db.db.get(file_id)
    if not extracted_file:
        abort(400, {"message": "Not found!"})
    blob = ibm_db.parse_blob(extracted_file)
    result_filename = f"{extracted_file['filename']}.{extracted_file['extension']}"
    return send_file(BytesIO(blob), as_attachment=True, attachment_filename=result_filename)


@urls.route("/api/files/<file_id>", methods=['GET'])
def get_file_by_id(file_id):
    extracted_file = ibm_db.db.get(file_id)
    if not extracted_file:
        abort(400, {"message": "Not found!"})
    return jsonify(ibm_db.deblob_doc(extracted_file))


@urls.route('/upload', methods=['GET', 'POST'])
def uploader():
    if request.method == "GET":
        return render_template("upload.html")
    if request.method == 'POST':
        f = request.files['file']
        username = request.form.get('username', 'anonymous')
        buffer = f.read()

        split_file = os.path.splitext(f.filename)
        extension = split_file[1][1:]
        file_no_extension = split_file[0]
        if extension not in ["wav", "ogg"]:
            abort(400, {"message": "Only wav or ogg are allowed"})
        data = {
            "username": username,
            "timestamp": str(datetime.now()),
            "filename": file_no_extension,
            "extension": extension,
            "processed": False
        }

        sample = buffer
        if extension == "wav":
            sample = convert_wav_to_ogg(BytesIO(buffer)).read()
            data["extension"] = "ogg"
        saved = ibm_db.store_blob(data, sample)
        # saved.pop('blob', None)
        return jsonify({"doc": saved})


@ws.route('/transcript')
def transcript_socket(socket):
    global sockets
    sockets.all_conns.append(socket)
    while not socket.closed:
        print("not closed")
        message = socket.receive()
        logging.info(f"Received: {message}")
        socket.send(message)


def callback_results(ch, method, properties, body):
    logging.info(body)
    global sockets
    utf_body = str(body, encoding='utf-8')
    to_remove = []
    for conn in sockets.all_conns:
        if not conn.closed:
            try:
                conn.send(utf_body)
            except Exception:
                pass
        else:
            to_remove.append(conn)
    for t in to_remove:
        try:
            sockets.all_conns.remove(t)
        except Exception:
            pass


def create_app():

    app = Flask(__name__, static_url_path='')

    app.config.from_object("backend.config.Config")

    # Init the deep learning model
    # deep_learning_model.init_app(app)
    # Init the RMQ connection
    # conn.init_app(app)
    sockets.init_app(app)
    ibm_db.init_app(app)

    sockets.register_blueprint(ws)
    app.register_blueprint(urls)

    return app


app = create_app()
# results_thread = Thread(target=results_thread, args=(app,), daemon=True)
# results_thread.start()

server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)


@atexit.register
def stop_server():
    if server:
        server.stop()


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=port, debug=True)
if __name__ == "__main__":
    server.serve_forever()
