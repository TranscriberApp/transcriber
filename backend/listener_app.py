from flask import Flask
from backend.messaging.rmq import Connecter
from flask.json import jsonify
import os
from dotenv import load_dotenv
from threading import Thread
from backend.dl_model.recording import deep_learning_model
from backend.dl_model.ogg_to_wav import convert
from io import BytesIO
import json
import datetime
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


load_dotenv()
conn = Connecter()


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


def callback_ogg(ch, method, properties, body):
    sample = convert(BytesIO(body))
    translation = deep_learning_model.infer(BytesIO(sample.read()))
    result = json.dumps({
        "time": str(datetime.datetime.now()),
        "transcript": translation
    })
    print(ch)
    print(method)
    print(properties)
    logging.info(result)
    conn.produce('results', result)


def callback_wav(ch, method, properties, body):
    translation = deep_learning_model.infer(BytesIO(body))
    result = json.dumps({
        "time": str(datetime.datetime.now()),
        "transcript": translation
    })
    logging.info(result)
    conn.produce('results', result)


def listen_to_ogg(app):
    logging.info('Listening for OGG messages')
    ogg_conn = Connecter()
    ogg_conn.init_app(app)
    ogg_conn.listen('hello-ogg', callback_ogg)


def listen_to_wav(app):
    logging.info('Listening for WAV messages')
    wav_conn = Connecter()
    wav_conn.init_app(app)
    wav_conn.listen('hello-wav', callback_wav)


def create_app():

    app = Flask(__name__)
    app.config.from_object("backend.config.Config")

    # Init RMQ connection
    conn.init_app(app)
    conn.define_queue("results")

    # Init the deep learning model
    deep_learning_model.init_app(app)
    return app


app = create_app()

ogg_thread = Thread(target=listen_to_ogg, args=(app,), daemon=True)
wav_thread = Thread(target=listen_to_wav, args=(app,), daemon=True)

ogg_thread.start()
wav_thread.start()


@app.route("/")
def hello():
    return jsonify({"hello": "world"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
