import serial
import matplotlib.pyplot as plt
import pub 
from matplotlib.animation import FuncAnimation
import threading

DEVICE = '/dev/ttyACM0'
BAUD_RATE = 115200
IBI = 600
BPM = 0

GRAPH_POINTS = 100

rate = [0 for i in range(11)]                     # array to hold last ten IBI values

sampleCounter = 0;          # used to determine pulse timing
lastBeatTime = 0;           # used to find IBI
P = 512;                      # used to find peak in pulse wave, seeded
T = 512;                     # used to find trough in pulse wave, seeded
thresh = 530;                # used to find instant moment of heart beat, seeded
amp = 0;                   # used to hold amplitude of pulse waveform, seeded
firstBeat = True;        # used to seed rate array so we startup with reasonable BPM
secondBeat = False;      # used to seed rate array so we startup with reasonable BPM
Pulse = False
# Receive data
ser = serial.Serial(DEVICE, BAUD_RATE)
sampleCounter = 0
lastBeatTime = 0

data = 0
data_vec = [0 for i in range(GRAPH_POINTS + 1)]                    

time = [0 for i in range(GRAPH_POINTS + 1)]                    
idx_data = 0
len_data = GRAPH_POINTS

bpm_vec = [0 for i in range(GRAPH_POINTS + 1)]
fig = plt.figure(figsize=(20, 5))

def update_data(i):
  global idx_data
  plt.cla()
  data_vec[0:-1] = data_vec[1:]
  data_vec[-1] = data
  time[0:-1] = time[1:]
  time[-1] = time[-1] + 2
  idx_data += 1 
  plt.plot(time, data_vec)

ani = FuncAnimation(fig, update_data, interval=2)

def plot(i):
  plt.show()

if __name__ == "__main__":
  client = pub.configure()

  while True:
    data = ser.readline().strip()

    try:
      Signal = int(data)
    except:
      Signal = 0
    
    sampleCounter = sampleCounter + 2
    N = sampleCounter - lastBeatTime
    if Signal < thresh and N > (IBI/5)*3:
      if Signal < T:  
        T = Signal


    if Signal > thresh and Signal > P:
      P = Signal
    
    if N > 250:
      if Signal > thresh and Pulse == False and N > (IBI/5)*3:
        Pulse = True
        IBI = sampleCounter - lastBeatTime        
        lastBeatTime = sampleCounter      

        if secondBeat:                        
          secondBeat = False                  
          for i in range(0, len(rate)):              
            rate[i] = IBI
        
        if firstBeat:                           # if it's the first time we found a beat, if firstBeat == TRUE

          firstBeat = False                   # clear firstBeat flag
          secondBeat = True                   # set the second beat flag
          continue

        runningTotal = 0

        for i in range(0, 9):
          rate[i] = rate[i+1]                  # and drop the oldest IBI value
          runningTotal += rate[i]              # add up the 9 oldest IBI values 

        rate[9] = IBI;                         # add the latest IBI to the rate array
        runningTotal += rate[9]                # add the latest IBI to runningTotal
        runningTotal /= 10                     # average the last 10 IBI values
        BPM = 60000/runningTotal               # how many beats can fit into a minute? that's BPM!
        pub.publish(client, BPM)
    

    if Signal < thresh and Pulse == True:   # when the values are going down, the beat is over
      Pulse = False                         # reset the Pulse flag so we can do it again
      amp = P - T                           # get amplitude of the pulse wave
      thresh = amp/2 + T                    # set thresh at 50% of the amplitude
      P = thresh                            # reset these for next time
      T = thresh

    if N > 2500:                           # if 2.5 seconds go by without a beat
      thresh = 530                          # set thresh default
      P = 512                               # set P default
      T = 512                               # set T default
      lastBeatTime = sampleCounter          # bring the lastBeatTime up to date
      firstBeat = True                      # set these to avoid noise
      secondBeat = False                    # when we get the heartbeat back
    
    print("BPM = ", BPM, " sigal = ", data)


    