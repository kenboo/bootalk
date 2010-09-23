#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, wave, StringIO
import aquestalk2
import alsaaudio
import SocketServer

# WAV file player
def play(device, f):    
    sys.stdout.write('%d channels, %d sampling rate\n' % (f.getnchannels(),
                                                          f.getframerate()))
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
class AquestalkHandler(SocketServer.StreamRequestHandler):

    def setup(self):
        self.device = alsaaudio.PCM(card='default')
        SocketServer.StreamRequestHandler.setup(self)

    def handle(self):
        print "connect from:", self.client_address
        while True:
            data = self.request.recv(8192)
            if len(data) == 0:
                break
            
            wav = aquestalk2.synthe(data)
            f = wave.open(StringIO.StringIO(wav))
            play(self.device, f)
        self.request.close()

def main():
    server = SocketServer.ThreadingTCPServer(('', 50002), AquestalkHandler)
    print 'listening:', server.socket.getsockname()
    server.serve_forever()

if __name__ == '__main__':
    main()
