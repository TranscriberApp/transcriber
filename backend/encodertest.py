import base64
import os

current_dir = os.path.abspath(os.path.dirname(__file__))

def buffer_to_base64(buf: bytes):
    return base64.encodebytes(buf).decode('utf-8')

def base64_to_buffer(encoded: str):
    return base64.decodebytes(bytes(encoded, 'utf-8'))

def _main():
    print(os.path.abspath(__file__))
    filename = os.path.join(current_dir, 'audio_2020-06-05_19-25-42.ogg')
    outfile = os.path.join(current_dir, 'output.ogg')
    outfileencoded = os.path.join(current_dir, 'output.ogg.base64encoded')

    with open(filename, 'rb') as f:
        encoded = buffer_to_base64(f.read())

    print(len(encoded))
    with open(outfile, 'wb') as f:
        outbuffer = base64_to_buffer(encoded)
        f.write(outbuffer)

    with open(outfileencoded, 'w') as f:
        f.write(encoded)
    pass


if __name__ == '__main__':
    _main()
