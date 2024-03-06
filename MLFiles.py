import torch
from transformers import pipeline, SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
from IPython.display import Audio

def translate(audio):
    outputs = pipe(audio, max_new_tokens=256, generate_kwargs={"task": "translate"})
    return outputs["text"]

def startModel():
    global pipe
    global device
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    pipe = pipeline(
    "automatic-speech-recognition", model="openai/whisper-base", device=device
    )

def startSpeechProcessor():  
    global processor, model, vocoder, speaker_embeddings
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    model.to(device)
    vocoder.to(device)
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

def synthesise(text, noneOrBytesOrTensor):
    inputs = processor(text=text, return_tensors="pt")
    speech = model.generate_speech(
        inputs["input_ids"].to(device), speaker_embeddings.to(device), vocoder=vocoder
    )
    if noneOrBytesOrTensor == -1: #nothing
        return speech
    if noneOrBytesOrTensor == 0:  #bytes
        return speech.cpu().detach().numpy().tobytes() #return as bytes
    else:  #tensor 
        return speech.cpu()

# startModel()
# startSpeechProcessor()
# speech = synthesise(translate("audioEng.wav"))
# Audio(speech, rate=16000)