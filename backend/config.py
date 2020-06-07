import pathlib
import os

default_dl_path = str((pathlib.Path(__file__).parent / "static" /
                       "models" / "deepspeech-0.7.3-models.pbmm").resolve())


class Config:
    DL_MODEL_PATH = os.getenv("DL_MODEL_PATH", default_dl_path)
    DL_SCORER_PATH = os.getenv("DL_SCORER_PATH", None)
    CLOUDANT_USER = os.getenv('CLOUDANT_USER')
    CLOUDANT_APIKEY = os.getenv('CLOUDANT_APIKEY')
    DEBUG = True
