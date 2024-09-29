import pyttsx3

def stage_tts():
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 106)
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    return engine

def speak(engine, text):
    engine.say(text)
    engine.runAndWait()
