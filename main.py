import datetime
import os
from random import randint
import wave
import sys
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import pyaudio
from MLFiles import *
import numpy as np

def deleteAudioFiles(directoryToDeleteFromRoot):
    # Get the path of the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Directory to delete
    delDirectory = current_directory + "/" + directoryToDeleteFromRoot

    # Check if directory exists
    directoryExists = os.path.exists(delDirectory)
    if not directoryExists:
        print (f"{getDateTime()}Creating " + directoryToDeleteFromRoot + " directory")
        os.mkdir(directoryToDeleteFromRoot)
        return
    
    # List all files in the directory
    files = os.listdir(delDirectory)

    fileCounter = 0
    # Delete files starting with "output"
    for file in files:
        if file.startswith("output"):
            file_path = os.path.join(delDirectory, file)
            os.remove(file_path)
            fileCounter+=1

    print(f"{getDateTime()}Deleted " + str(fileCounter) + " audio files.")
    
def getDateTime():
    return f'[{datetime.datetime.now().strftime("%H:%M:%S")}]: '

class Client(DatagramProtocol):
    
    def __init__(self, speech, audioFile) -> None:
        super().__init__()
        self.audioFileLocation = audioFile
        self.counter = 0
        # Convert the speech tensor to a PyAudio-compatible format
        #self.audio_data = speech.numpy().astype('float32')

    def startProtocol(self):
        #Audio File
        self.chunk_size = 1024
        self.sample_rate = 16000
        self.py_audio = pyaudio.PyAudio()
        self.buffer = 1024  
        self.THRESHOLD = int(input("Enter Energy Threshold (1000 is default): ")) 
        self.another_client = input("Write address: "), int(input("Write port: "))
        self.frames = []
        self.silence_counter = 0
        self.speaking = False

        if self.another_client[0] == "":
            self.another_client="127.0.0.1", self.another_client[1]

        self.input_stream = self.py_audio.open(format=pyaudio.paInt16,
                                          input=True, rate=44100, channels=1,
                                          frames_per_buffer=self.buffer)

        self.output_stream = self.py_audio.open(format=pyaudio.paFloat32,
                                        channels=1,
                                        rate=self.sample_rate,
                                        output=True)
        
        # self.output_stream = self.py_audio.open(format=pyaudio.paInt16,
        #                                   output=True, rate=44100, channels=1,
        #                                   frames_per_buffer=self.buffer)
        reactor.callInThread(self.record)

    def record(self):
        print(f"{getDateTime()}Beginning to record")

        while True:
            data = self.input_stream.read(self.buffer, False)
            self.transport.write(data, self.another_client)
    
    def save_recording_and_translate(self, frames):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.wav"
        filename = f"./{self.audioFileLocation}/" + filename
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.py_audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
        frames.clear()

        return translate(filename)
    
    def outputTextToSpeech(self, text):
        speech = synthesise(text, -1)
        print (f"{getDateTime()}Audio created for: " + text)
        audio_data = speech.numpy().astype('float32')
        self.output_stream.write(audio_data.tobytes())
    
    def translationBlockingMethod(self):
        print (f"{getDateTime()} Blocking Method Called")
        self.outputTextToSpeech(self.save_recording_and_translate(self.frames))
        print (f"{getDateTime()} Blocking Method Finished")

    def datagramReceived(self, datagram, addr):
                
        if self.speaking:
            self.frames.append(datagram)

        audio = np.frombuffer(datagram, dtype=np.int16) #hmm is this correct type
        energy = np.sum(np.abs(audio)) / len(audio)
        #print(f"{getDateTime()}Energy level: {energy}")
        if energy < self.THRESHOLD:
            self.silence_counter += 1
            if self.silence_counter > 50: 
                if self.speaking:
                    reactor.callInThread(self.translationBlockingMethod) #output stream translates and writes in new thread
                    self.silence_counter=0
                    self.speaking = False
                else:
                    if self.counter == 500: 
                        reactor.stop() #close stream after long silence
        else:
            self.speaking = True
            self.silence_counter = 0

if __name__ == '__main__':
    #Delete previous files
    audioFileLocation = "audioFiles"
    deleteAudioFiles(audioFileLocation)

    #Start models
    startModel()
    startSpeechProcessor()

    # Generate speech
    text = "Hello world!"
    speech = synthesise(text, -1)

    port = randint(1000, 3000)
    print(f"{getDateTime()}Working on port: ", port)

    reactor.listenUDP(port, Client(speech, audioFileLocation))
    reactor.run()
    print(f"{getDateTime()}Reactor stopped!")