from flask import Flask, request
import logging
import os
from storage import azureStorage

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

soundfont_default = 'GeneralUserGS.sf2'
tempfile = 'temp_wav.wav'
local_midi = 'output.mid'


@app.route('/', methods=['POST'])
def convert_midi_to_wav():
    app.logger.info('Conversion request received to convert midi to wav: '
                    + str(request.get_json()))
    blob_in = request.get_json().get('midi')
    if not blob_in:
        app.logger.warning('Conversion request received with ' +
                           'no \'midi\' field.')
        return 'Error: Conversion request received with no \'midi\' field.', 422

    blob_out = blob_in.strip('.mid') + '.wav'
    try:
        azureStorage.download(local_midi, blob_in)
        app.logger.info('Download successful of blob:' + str(blob_in))
        midi_to_wav(local_midi, soundfont_default, tempfile)
        azureStorage.upload(tempfile, blob_out)

        azureStorage.delete(blob_in)
        os.remove(tempfile)
        os.remove(local_midi)
    except Exception as e:
        app.logger.error(e)
        return ('Error: Unexpected error occurred in the conversion process.',
                500)
    return blob_out, 201


def midi_to_wav(midi_file, soundfont, outfile):
    os.system(f'fluidsynth -ni {soundfont} {midi_file} -F {outfile} -r 44100')
