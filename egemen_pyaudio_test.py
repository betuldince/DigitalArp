import struct
import time
from queue import LifoQueue

import pyaudio

# import librosa
import wave
import sys
import serial
import threading
import json
import pydub
from scipy.io.wavfile import write


from pydub import AudioSegment


import numpy as np

ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM3'
ser.open()

volume=0
def stretch(snd_array, factor, window_size, h):
    """ Stretches/shortens a sound, by some factor. """
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(snd_array) / factor + window_size))
    for i in np.arange(0, len(snd_array) - (window_size + h), h*factor):
        i = int(i)
        # Two potentially overlapping subarrays
        a1 = snd_array[i: i + window_size]
        a2 = snd_array[i + h: i + window_size + h]

        # The spectra of these arrays
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)

        # Rephase all frequencies
        phase = (phase + np.angle(s2/s1)) % 2*np.pi

        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))
        i2 = int(i/factor)
        result[i2: i2 + window_size] += hanning_window*a2_rephased.real
    return result # .astype('int16')

def speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[ indices.astype(int) ]

def pitchshift(snd_array, n, window_size=2**10, h=2**8):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / 12.0)
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)

def read_serial(q):
    # global ser, voltage, resistance
    global volume
    while True:
        try:
            line = ser.readline() 

            j_obj = json.loads(line)

            voltage = j_obj['voltage']
            resistance = j_obj['resistance']
            volume=remap(resistance, 5, 15, -20, 20)
            print(volume)
            q.put((voltage, resistance))
           
            #while ser.inWaiting():
             #   print(ser.readline())
        except:
            continue
# read_serial()

def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min

class AudioFile:
    
    chunk = 1024
    def __init__(self, file):
        """ Init audio stream """

        
        self.wf = wave.open(file, 'rb')
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True,
            
        )
    #
    # def change_pitch(self, frame):
    #     fr = 20
    #     sz =

    def play(self, q):
        
        # global voltage, resistance
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        pitch = 1
        volume=1
        while data != '':
            if q.qsize() > 0:
                vals = q.get(block=False)
                resistance = vals[1]
                pitch = remap(resistance, 0, 100, 1, 2)
                #volume=remap(resistance, 5, 40, 1, 100)

              
                # if a is not None:
                #print(pitch)
                #print(vals)

            # final_data = librosa.effects.pitch_shift(np.array(final_data), self.wf.getframerate(), n_steps=1.0)
            # waveform = map(ord, list(data))
            # data = np.fft.irfft(waveform)
            # dataout = np.array(data * 0.5, dtype='int16')  # undo the *2 that was done at reading
            # final_data = struct.pack("%dh" % (len(dataout)), *list(dataout))  # convert back to 16-bit data

            # data = np.fromstring(data, dtype=np.int16)
            # data *= 2

            interleaved = np.frombuffer(data, dtype=f'int{self.wf.getsampwidth() * 8}')
            # Reshape it into a 2D array separating the channels in columns.
            data = np.reshape(interleaved, (-1, self.wf.getnchannels()))

            # Do operations here
            # data = stretch(data, 2**(5/12), 2**13, 2**11)
            # data = np.repeat(data, 2)
            #data = speedx(data, 2)
            # data = pitchshift(data, n=4)
            # Do operations here ^
            
            data = (data.astype(np.int16).tostring())
            data *= -2
            self.stream.write(data)
             
            data = self.wf.readframes(self.chunk) 
            

          

            

    def close(self):
        """ Graceful shutdown """
        self.stream.close()
        self.p.terminate()

# Usage example for pyaudio
#new_file= AudioSegment.from_file("file_example_WAV_1MG.wav") 
#new_file=new_file+volume
#print(volume)
#new_file.export(out_f = "louder_wav_file.wav",format = "wav")
#a = AudioFile("louder_wav_file.wav")
a = AudioFile("file_example_WAV_1MG.wav")
# a.play()
# a.play()

queue = LifoQueue(1)

t1 = threading.Thread(target=a.play, args=(queue, ))
t2 = threading.Thread(target=read_serial, args=(queue, ))
t1.start()
t2.start()
t1.join()
t2.join()




a.close()