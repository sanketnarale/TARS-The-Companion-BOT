# voice_control.py
#Run this code to give commands via voice

import os
os.environ["PYTHONWARNINGS"] = "ignore"


import speech_recognition as sr
import requests
import time
import sys
import smooth_operator as mechanism

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

class LanguageState:
    def __init__(self):
        self.language = 'english'
        self.humor = 0.5
        self.honesty = 0.5

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("? Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=4)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("? TARS: You're mumbling again.")
        except sr.WaitTimeoutError:
            print("? TARS: You had your chance.")
        except sr.RequestError:
            print("? TARS: My ears are broken.")
        return None

def tars_reply(prompt, honesty, humor, language):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": f"You are TARS, the sarcastic robot from Interstellar. "
                           f"Respond in {language} with {honesty*100:.0f}% honesty and {humor*100:.0f}% sarcasm."
            },
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[TARS ERROR] {e}"

def process_command(command, state):
    if command is None:
        return state

    if "take two steps" in command:
        mechanism.move_forward()
        time.sleep(0.5)
        mechanism.move_forward()
        response = tars_reply("Moving forward", state.honesty, state.humor, state.language)

    elif "move forward" in command:
        mechanism.move_forward()
        response = tars_reply("Moving forward", state.honesty, state.humor, state.language)
        
    elif "turn left" in command:
        mechanism.turn_left()
        time.sleep(0.8)
        mechanism.turn_left()
        response = tars_reply("Turning left", state.honesty, state.humor, state.language)

    elif "turn right" in command:
        mechanism.turn_right()
        time.sleep(0.8)
        mechanism.turn_right()
        response = tars_reply("Turning right", state.honesty, state.humor, state.language)

    elif "neutral" in command or "reset" in command:
        mechanism.neutral()
        response = tars_reply("Returning to neutral", state.honesty, state.humor, state.language)

    elif "stop" in command or "shutdown" in command:
        print("TARS: Shutting down. Try not to miss me.")
        sys.exit(0)

    else:
        response = tars_reply(command, state.honesty, state.humor, state.language)

    print(f"TARS: {response}")
    return state

def main():
    state = LanguageState()
    while True:
        command = listen()
        if command:
            state = process_command(command, state)
        time.sleep(1)

if __name__ == "__main__":
    main()
