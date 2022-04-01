import string
from xml.etree.ElementTree import tostring
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
            volumes.append(remap(resistance, 5, 15, 10, 500) )
            avg1=np.average(volumes[0:50])
            avg2=np.average(volumes[50:100])
            avg3=np.average(volumes[100:150])
            avg4=np.average(volumes[150:200])
            avg5=np.average(volumes[200:250])
            avg6=np.average(volumes[250:300])

        
            #print(len(volumes) / 30 * 10)

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
    nota="init"
    nota_array=[]
    freq=[]
    wave=[]
    #volumes = np.repeat(np.array(volumes), 1470)
    #print(len(volumes))
    
    note_freqs = get_piano_notes()

    if(np.average(volumes[0:150] )<200.0):
        nota='C4'

    elif(np.average(volumes[0:150] )<200.0):
        nota='D4'

    if(np.average(volumes[150:300] )>200.0):
        nota1='D4'
    elif(np.average(volumes[150:300] )<200.0):
        nota1='D4'

    for i in range(14):
        for j in range(8):
            if(np.average(volumes[(i+1)*20:(i+2)*20] )<50*j and np.average(volumes[i*20:(i+1)*20] )>50*(j-1)):
                nota_array.append('A'+str(j))
            else:
                nota_array.append('A0')
                #np.concatenate('A',str(j))

    #for i in range(10):
     #       if(np.average(volumes[(i)*20:(i+1)*20] )<500 ):
      #          nota_array[i]='A0'
       #     print(nota_array)
                #np.concatenate('A',str(j))



    print(nota_array)
    for i in range(10):
        t = np.linspace(0, 1, int(44100*4)) # Time axis
         
        freq.append(note_freqs[nota_array[i]])
        wave.append((4096*np.sin(2 * np.pi * t * freq[i])).astype(np.int16))
    print(wave)
    t = np.linspace(0, 4, int(44100*4)) # Time axis
    t1 = np.linspace(4, 8, int(44100*4)) # Time axis

 
    wavfile.write('pure_c.wav', rate=44100, data=wave )
    


   



# t1 = threading.Thread(target=generate)
# t2 = threading.Thread(target=read_serial)
# t1.start()
# t2.start()
# t1.join()
# t2.join()

read_serial()
generate()


 