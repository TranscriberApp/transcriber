import datetime
import json
import logging
import os
from io import BytesIO
import time
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from flask.json import jsonify

from backend.dl_model.ogg_to_wav import convert
from backend.dl_model.recording import deep_learning_model
from backend.messaging.cloud_db import ibm_db
from cloudant.document import Document

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


load_dotenv()


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


def callback_ogg(data):
    try:
        blob = ibm_db.parse_blob(data)
        sample = convert(BytesIO(blob))
        translation = deep_learning_model.infer(BytesIO(sample.read()))
        result = json.dumps({
            "time": str(datetime.datetime.now()),
            "transcript": translation,
            "username": data["username"]
        })
        return result
    except Exception:
        logging.exception("Error processing ogg file")


def try_delete_doc(doc_id):
    try:
        with Document(ibm_db.db, doc_id) as doc:
            doc['_deleted'] = True
    except:
        logging.exception("Could not delete document")


def listen_to_ogg(app):
    logging.info('Listening for OGG messages')
    while True:
        logging.debug("Checking for new ogg files")
        selector = {'extension': {'$eq': 'ogg'}, "processed": {'$eq': False}}
        docs = ibm_db.db.get_query_result(selector)
        for doc in docs:
            logging.info(f"processing: {doc['_id']}")
            transcript = callback_ogg(doc)
            if transcript is not None:
                logging.info(transcript)
                try_delete_doc(doc['_id'])
        time.sleep(5)


def create_app():
    """
    Create a flask app just for dependency injection etc
    """

    app = Flask(__name__)
    app.config.from_object("backend.config.Config")

    # Init db connection
    ibm_db.init_app(app)

    # Init the deep learning model
    deep_learning_model.init_app(app)
    return app


app = create_app()

if __name__ == '__main__':
    # Start the thread and run forever
    ogg_thread = Thread(target=listen_to_ogg, args=(app,), daemon=True)
    ogg_thread.start()
    while True:
        time.sleep(1)
