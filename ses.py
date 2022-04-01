import numpy as np
from scipy.io import wavfile
import serial
import json
import threading
import sys


ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM3'
ser.open()

volume=0
def remap(old_val, old_min, old_max, new_min, new_max):
    old_val = min(old_max, max(old_min, old_val))
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min

volumes = [] # 10 * 30 * 1470
vol_avg=[]


def get_piano_notes():   
    # White keys are in Uppercase and black keys (sharps) are in lowercase
    octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B'] 
    base_freq = 440 #Frequency of Note A4
    keys = np.array([x+str(y) for y in range(0,9) for x in octave])
    # Trim to standard 88 keys
    start = np.where(keys == 'A0')[0][0]
    end = np.where(keys == 'C8')[0][0]
    keys = keys[start:end+1]
    
    note_freqs = dict(zip(keys, [2**((n+1-49)/12)*base_freq for n in range(len(keys))]))
    note_freqs[''] = 0.0 # stop
    return note_freqs


def read_serial():
    # global ser, voltage, resistance
    global volumes
    while True:
        try:
            line = ser.readline() 

            j_obj = json.loads(line)

            voltage = j_obj['voltage']
            resistance = j_obj['resistance']
            volumes.append(remap(resistance, 5, 15, 10, 1000) )
            

            if len(volumes) >= 30 * 10:
              
                return

                    
            #while ser.inWaiting():
             #   print(ser.readline())
        except:
            continue
# read_serial()

def get_sine_wave(frequency, duration, sample_rate=44100, amplitude=4096):
    t = np.linspace(0, duration, int(sample_rate*duration)) # Time axis
    wave = amplitude*np.sin(2 * np.pi * t * frequency)
    return wave

def generate():
    global volumes
    fr=5000

    volumes = np.repeat(np.array(volumes), 1470)
    print(len(volumes))

    sine_wave = get_sine_wave(volumes, duration=10, amplitude=4096)
    wavfile.write('pure_c.wav', rate=44100, data=sine_wave.astype(np.int16))
    print(sine_wave.astype(np.int16))



# t1 = threading.Thread(target=generate)
# t2 = threading.Thread(target=read_serial)
# t1.start()
# t2.start()
# t1.join()
# t2.join()

read_serial()
generate()


 