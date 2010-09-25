#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, wave, StringIO
import aquestalk2
import aquestalk2.yahoo
import alsaaudio
import BaseHTTPServer, urllib
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from optparse import OptionParser

# WAV file player
def play(device, f):    
    #log.debug('%d channels, %d sampling rate\n',
    #          f.getnchannels(), f.getframerate())
    # Set attributes
    device.setchannels(f.getnchannels())
    device.setrate(f.getframerate())

    # 8bit is unsigned in wav files
    if f.getsampwidth() == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif f.getsampwidth() == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif f.getsampwidth() == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_LE)
    elif f.getsampwidth() == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError('Unsupported format')

    device.setperiodsize(320)
    
    data = f.readframes(320)
    while data:
        # Read data from stdin
        device.write(data)
        data = f.readframes(320)

# socket server handler
class AquestalkHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def setup(self):
        self.device = alsaaudio.PCM(card='default')
        BaseHTTPServer.BaseHTTPRequestHandler.setup(self)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        #log.debug("connect from: %s", self.client_address)
        if not self.path.startswith('/say?'):
            self.send_response(404)
            self.end_headers()
            return
        try:
            junk, data = self.path.split('?')
            data = urllib.unquote_plus(data)
            log.debug(data)
            phonetic = aquestalk2.yahoo.to_phonetic(data)
            log.debug(phonetic)
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write("<html><head><title>Bootalk</title></head>")
            self.wfile.write("<body>bad input. UTF8 please</body></html>")
            return

        try:
            wav = aquestalk2.synthe(phonetic)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><head><title>Bootalk</title></head>")
            self.wfile.write("<body>%s</body></html>" % phonetic)
            f = wave.open(StringIO.StringIO(wav))
            play(self.device, f)
        except Exception, e:
            dummy, v =  str(e).split(' ')
            err = aquestalk2.error_code.get(int(v)) or 'Unknown error %s' % v
            log.warn(err)
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><head><title>Bootalk</title></head>")
            self.wfile.write("<body>%s</body></html>" % err)

def main():
    parser = OptionParser()
    parser.add_option('-p', '--port', action="store", type="int",
                      dest="port", default=50002,
                      help="listening port")
    parser.add_option('-v', '--verbose', action="store_true",
                      dest="verbose",
                      help="show debug message")

    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)

    server = BaseHTTPServer.HTTPServer(('', options.port),
                                       AquestalkHandler)
    log.info('listening: %s', server.socket.getsockname())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

if __name__ == '__main__':
    main()
