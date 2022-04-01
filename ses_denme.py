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
    nota='A0'
    nota1='A0'
    nota2='A0'
    nota3='A0'
    nota4='A0'
    nota5='A0'





    nota_array=[]
    #volumes = np.repeat(np.array(volumes), 1470)
    #print(len(volumes))
    
    note_freqs = get_piano_notes()

    if(np.average(volumes[0:50] )>0.0 and np.average(volumes[0:50] )<190.0):
        nota='A2'
    elif(np.average(volumes[0:50] )>190.0 and np.average(volumes[0:50] )<220.0):
        nota='B4'
    elif(np.average(volumes[0:50] )>220.0 and np.average(volumes[0:50] )<250.0):
        nota='d4'
    elif(np.average(volumes[0:50] )>250.0 and np.average(volumes[0:50] )<280.0):
        nota='C2'
    elif(np.average(volumes[0:50] )>280.0 and np.average(volumes[0:50] )<300.0):
        nota='E3'
    elif(np.average(volumes[0:50] )>300.0 and np.average(volumes[0:50] )<800.0):
        nota='C8'

    if(np.average(volumes[50:100] )>0.0 and np.average(volumes[50:100] )<190.0):
        nota1='A2'
    elif(np.average(volumes[50:100] )>190.0 and np.average(volumes[50:100] )<220.0):
        nota1='B4'
    elif(np.average(volumes[50:100] )>220.0 and np.average(volumes[50:100] )<250.0):
        nota1='d4'
    elif(np.average(volumes[50:100] )>250.0 and np.average(volumes[50:100] )<280.0):
        nota1='C2'
    elif(np.average(volumes[50:100] )>280.0 and np.average(volumes[50:100] )<300.0):
        nota1='E3'
    elif(np.average(volumes[50:100] )>300.0 and np.average(volumes[50:100] )<800.0):
        nota1='C8'

    if(np.average(volumes[100:150] )>0.0 and np.average(volumes[100:150] )<190.0):
        nota2='A2'
    elif(np.average(volumes[100:150] )>190.0 and np.average(volumes[100:150] )<220.0):
        nota2='B4'
    elif(np.average(volumes[100:150] )>220.0 and np.average(volumes[100:150] )<250.0):
        nota2='d4'
    elif(np.average(volumes[100:150] )>250.0 and np.average(volumes[100:150] )<280.0):
        nota2='C2'
    elif(np.average(volumes[100:150] )>280.0 and np.average(volumes[100:150] )<300.0):
        nota2='E3'
    elif(np.average(volumes[100:150] )>300.0 and np.average(volumes[100:150] )<800.0):
        nota2='C8'

    if(np.average(volumes[150:200] )>0.0 and np.average(volumes[150:200] )<190.0):
        nota3='A2'
    elif(np.average(volumes[150:200] )>190.0 and np.average(volumes[150:200] )<220.0):
        nota3='B4'
    elif(np.average(volumes[150:200] )>220.0 and np.average(volumes[150:200] )<250.0):
        nota3='d4'
    elif(np.average(volumes[150:200] )>250.0 and np.average(volumes[150:200] )<280.0):
        nota3='C2'
    elif(np.average(volumes[150:200] )>280.0 and np.average(volumes[150:200] )<300.0):
        nota3='E3'
    elif(np.average(volumes[150:200] )>300.0 and np.average(volumes[150:200] )<800.0):
        nota3='C8'

    if(np.average(volumes[200:250] )>0.0 and np.average(volumes[200:250] )<190.0):
        nota4='A2'
    elif(np.average(volumes[200:250] )>190.0 and np.average(volumes[200:250] )<220.0):
        nota4='B4'
    elif(np.average(volumes[200:250] )>220.0 and np.average(volumes[200:250] )<250.0):
        nota4='A8'
    elif(np.average(volumes[200:250] )>250.0 and np.average(volumes[200:250] )<280.0):
        nota4='C2'
    elif(np.average(volumes[200:250] )>280.0 and np.average(volumes[200:250] )<300.0):
        nota4='E3'
    elif(np.average(volumes[200:250] )>300.0 and np.average(volumes[200:250] )<800.0):
        nota4='C8'

    if(np.average(volumes[250:300] )>0.0 and np.average(volumes[250:300] )<190.0):
        nota5='A2'
    elif(np.average(volumes[250:300] )>190.0 and np.average(volumes[250:300] )<220.0):
        nota5='B4'
    elif(np.average(volumes[250:300] )>220.0 and np.average(volumes[250:300] )<250.0):
        nota5='A8'
    elif(np.average(volumes[250:300] )>250.0 and np.average(volumes[250:300] )<280.0):
        nota5='C2'
    elif(np.average(volumes[250:300] )>280.0 and np.average(volumes[250:300] )<300.0):
        nota5='E3'
    elif(np.average(volumes[250:300] )>300.0 and np.average(volumes[250:300] )<320.0):
        nota5='C8'


 


    frequency = note_freqs[nota]
    frequency1 = note_freqs[nota1]
    frequency2 = note_freqs[nota2]
    frequency3 = note_freqs[nota3]
    frequency4 = note_freqs[nota4]
    frequency5 = note_freqs[nota5]

    print(np.average(volumes[150:300]))
    print(np.average(volumes[0:150]))
    print(frequency)
    print(frequency1)
    print(frequency)
    print(frequency1)
    print(frequency)
    print(frequency1)    
    t = np.linspace(0, 1, int(44100*2)) # Time axis
 

    wave1 = 4096*np.sin(2 * np.pi * t * frequency)
    wave2 = 4096*np.sin(2 * np.pi * t * frequency1)
    wave3 = 4096*np.sin(2 * np.pi * t * frequency2)
    wave4 = 4096*np.sin(2 * np.pi * t * frequency3)
    wave5 = 4096*np.sin(2 * np.pi * t * frequency4)
    wave6 = 4096*np.sin(2 * np.pi * t * frequency5)

   
    wavfile.write('pure_c.wav', rate=44100, data=np.concatenate((wave1.astype(np.int16), wave2.astype(np.int16), wave3.astype(np.int16),wave4.astype(np.int16),wave5.astype(np.int16),wave6.astype(np.int16)   ), axis=None))
   


   



# t1 = threading.Thread(target=generate)
# t2 = threading.Thread(target=read_serial)
# t1.start()
# t2.start()
# t1.join()
# t2.join()

read_serial()
generate()


 