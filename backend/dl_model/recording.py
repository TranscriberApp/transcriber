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
import logging
import audioop

fs = 44100  # Sample rate
seconds = 5  # Duration of recording


def downsample_wav(s_read, inrate=44100, outrate=16000, inchannels=2, outchannels=1):
    
    n_frames = s_read.getnframes()
    data = s_read.readframes(n_frames)

    try:
        converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
        if outchannels == 1:
            converted = audioop.tomono(converted[0], 2, 1, 0)
    except:
        print('Failed to downsample wav')
        return False
    try:
        return outrate, np.frombuffer(converted, np.int16)
    except:
        print('Failed to write wav')
        return False
    return True


def load_scorer(ds, scorer):
    logging.info('Loading scorer from files {}'.format(
        scorer))
    ds.enableExternalScorer(scorer)


def sample_audio(audiofile: str, desired_sample_rate):
    fin = wave.open(audiofile, 'rb')
    fs_orig = fin.getframerate()
    if fs_orig != desired_sample_rate:
        logging.warning('Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.'.format(
            fs_orig, desired_sample_rate))
        fs_new, audio = downsample_wav(fin, outrate=desired_sample_rate)
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
        logging.info('Loading scorer from files {}'.format(
            scorer))
        self.model.enableExternalScorer(scorer)

    def infer(self, audio_sample):
        audio = sample_audio(audio_sample, self.model.sampleRate())
        return self.model.stt(audio)


deep_learning_model = DeepLearnModel()
