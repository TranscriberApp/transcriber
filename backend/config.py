import pathlib
import os

default_dl_path = str((pathlib.Path(__file__).parent / "static" /
                       "models" / "deepspeech-0.7.3-models.pbmm").resolve())


class Config:
    DL_MODEL_PATH = os.getenv("DL_MODEL_PATH", default_dl_path)
    DL_SCORER_PATH = os.getenv("DL_SCORER_PATH", None)
    RMQ_USER = os.getenv("RMQ_USER")
    RMQ_PASS = os.getenv("RMQ_PASS")
    RMQ_HOST = os.getenv("RMQ_HOST", "localhost")
    RMQ_VHOST = os.getenv("RMQ_VHOST")
    DEBUG = True
