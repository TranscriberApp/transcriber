import argparse
from pydub import AudioSegment


def convert(ogg_file):
    return AudioSegment.from_ogg(ogg_file).export(format="wav", bitrate="16k", parameters=["-ar", "16000"])


def _main():
    parser = argparse.ArgumentParser(
        __name__, description="Source ogg to wav file")
    parser.add_argument(
        "--src", help="The source ogg file path", required=True)
    parser.add_argument("--dst", default="test.wav",
                        help="The destination of the script. Default: test.wav")
    args = parser.parse_args()
    sound = AudioSegment.from_ogg(args.src)
    # sound = sound.set_frame_rate(16000)
    sound.export(args.dst, format="wav", bitrate="16k",
                 parameters=["-ar", "16000"])


if __name__ == '__main__':
    _main()
