import os
import wave
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
from scipy.io.wavfile import write
import subprocess
import shutil
import glob
import shlex
from shlex import quote
import sys
from deepspeech import Model
import argparse
import pathlib

fs = 44100  # Sample rate
seconds = 5  # Duration of recording


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(
        quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(
            shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, 'SoX not found, use {}hz files or install it: {}'.format(
            desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)


def load_scorer(ds, scorer):
    print('Loading scorer from files {}'.format(scorer), file=sys.stderr)
    ds.enableExternalScorer(scorer)


def sample_audio(audiofile: str, desired_sample_rate):
    fin = wave.open(audiofile, 'rb')
    fs_orig = fin.getframerate()
    if fs_orig != desired_sample_rate:
        print('Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.'.format(
            fs_orig, desired_sample_rate), file=sys.stderr)
        fs_new, audio = convert_samplerate(audiofile, desired_sample_rate)
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    audio_length = fin.getnframes() * (1/fs_orig)
    fin.close()
    return audio


class DeepLearnModel:

    def __init__(self):
        self.model = None

    def init_app(self, app):
        self.model = Model(str(app.config["DL_MODEL_PATH"]))
        scorer = app.config['DL_SCORER_PATH']
        if scorer:
            self._load_scorer(scorer)

    def _load_scorer(self, scorer):
        print('Loading scorer from files {}'.format(scorer), file=sys.stderr)
        self.model.enableExternalScorer(scorer)

    def infer(self, audio_sample):
        audio = sample_audio(audio_sample, self.model.sampleRate())
        return self.model.stt(audio)


dl = DeepLearnModel()
