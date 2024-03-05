from flask import Flask, request
import logging
import os
from storage import azureStorage

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

soundfont = 'GeneralUserGS.sf2'
tempfile = 'temp_wav.wav'
local_midi = 'output.mid'


@app.route('/', methods=['POST'])
def convert_midi_to_wav():
    blob_in = request.get_json().get('midi')
    if not blob_in:
        app.logger.warning('Conversion request received with no \'midi\' field.')
        return 'Error', 500

    # toDo: name generator
    blob_out = 'wav_out.wav'
    app.logger.info('Converting MIDI:' + blob_in + ' to WAV:' + blob_out)
    try:
        azureStorage.download(local_midi, blob_in)
        midi_to_wav(local_midi, soundfont, tempfile)
        azureStorage.upload(tempfile, blob_out)

        os.remove(tempfile)
        os.remove(local_midi)
    except Exception as e:
        app.logger.error(e)
        return 'error', 500
    return blob_out, 201


def midi_to_wav(midi_file, soundfont, outfile):
    os.system(f'fluidsynth -ni {soundfont} {midi_file} -F {outfile} -r 44100')