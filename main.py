import datetime
import os
from random import randint
import wave

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
        print ("Creating " + directoryToDeleteFromRoot + " directory")
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

    print("Deleted " + str(fileCounter) + " audio files.")
    
class Client(DatagramProtocol):
    
    def __init__(self, speech, audioFile) -> None:
        super().__init__()
        self.audioFileLocation = audioFile
        self.counter = 0
        # Convert the speech tensor to a PyAudio-compatible format
        self.audio_data = speech.numpy().astype('float32')
        print("Instantiated class!")

    def startProtocol(self):
        #Audio File
        self.chunk_size = 1024
        self.sample_rate = 16000
        self.py_audio = pyaudio.PyAudio()
        self.buffer = 1024  
        self.THRESHOLD = 1000
        self.another_client = input("Write address: "), int(input("Write port: "))
        if self.another_client[0] == "":
            self.another_client="127.0.0.1", self.another_client[1]

        self.output_stream = self.py_audio.open(format=pyaudio.paFloat32,
                                        channels=1,
                                        rate=self.sample_rate,
                                        output=True)
        
        self.input_stream = self.py_audio.open(format=pyaudio.paInt16,
                                          input=True, rate=44100, channels=1,
                                          frames_per_buffer=self.buffer)
        reactor.callInThread(self.record)

    def record(self):
        frames = []
        silence_counter = 0
        speaking = False
        while True:
            data = self.input_stream.read(self.buffer, False)
            if speaking:
                frames.append(data)
            audio = np.frombuffer(data, dtype=np.int16)
            energy = np.sum(np.abs(audio)) / len(audio)
            if energy < self.THRESHOLD:
                silence_counter += 1
                if silence_counter > 50:  # Adjust the number of consecutive silent chunks required for a pause
                    if speaking:
                        transcribedText = self.save_recording_and_translate(frames)
                        print(transcribedText)
                        speech = synthesise(transcribedText, -1)
                        self.audio_data = speech.numpy().astype('float32')
                        print("Transporting..")
                        self.transport.write(data, self.another_client) #speech done, translate and output  
                        #MAKE SURE TO USE FRAMES
                        silence_counter=0
                        speaking = False
                    else:
                        pass
            else:
                speaking = True
                silence_counter = 0
    
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


    #This is not printing probably because the recording thread is on first? Main thread?
    def datagramReceived(self, datagram, addr):
        self.counter+=1
        print(self.counter, end = " ")
        self.output_stream.write(self.audio_data.tobytes())
        # self.output_stream.write(datagram)
        if self.counter == 10:
            reactor.stop()
            #close the stream


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
    print("Working on port: ", port)

    reactor.listenUDP(port, Client(speech, audioFileLocation))
    reactor.run()
    print("Reactor stopped!")
