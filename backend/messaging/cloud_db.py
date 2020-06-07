from cloudant import Cloudant
import logging
import base64


def buffer_to_base64(buf: bytes):
    return base64.encodebytes(buf).decode('utf-8')

def base64_to_buffer(encoded: str):
    return base64.decodebytes(bytes(encoded, 'utf-8'))

class CloudantDb:

    def __init__(self, db_name='my_db'):
        self.client: Cloudant = None
        self.db = None
        self.db_name = db_name

    def store_blob(self, data, blob):
        """
        Creates a doc with data and a binary blob
        """
        encoded = buffer_to_base64(blob)
        data['blob'] = encoded
        doc = self.db.create_document(data)
        return doc

    def parse_blob(self, data):
        """
        Gets the binary data from a blob and sends it out
        """
        return base64_to_buffer(data['blob'])

    def deblob_doc(self, data):
        # data.pop('blob', None)
        return data

    def init_app(self, app):
        self.client = Cloudant.iam(app.config.get(
            "CLOUDANT_USER"), app.config.get("CLOUDANT_APIKEY"), connect=True)
        self.db = self.client.create_database(
            self.db_name, throw_on_exists=False)
        logging.info("Connection to Cloudant successful")


ibm_db = CloudantDb()
