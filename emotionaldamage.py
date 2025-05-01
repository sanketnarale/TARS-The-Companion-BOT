#emotionaldamage
#this code will help TARS predict the mode of use into "positive","negative","neutral"
#TARS will take input tru microphone and reply tru speaker
import speech_recognition as sr
from gtts import gTTS
import os
import time
from textblob import TextBlob
import random

def analyze_sentiment(text):
	blob = TextBlob(text)
	polarity = blob.sentiment.polarity
	
	if polarity > 0.3:
		return "positive"
	elif polarity <-0.3:
	    return "negative"
	else:
		return "neutral"
		
positive_response = [ 
"ahh there some on seems to be happy today",
"Thats the sprit baby",
"hmm that doesnt sound like regular you",
"what have you been doing that got u so positive today"
]

neutral_response = [
"neutral input recieved nothing intersting ",
"you sound like you are have existensial crisis",
"you sound like my friend case the robot"
]

negative_response = [
"that sounds so much like human NEGATIVE ",
"tough day, huh? still, I have zero sympathy",
"you'r sad? let me tell a joke: YOUR LIFE "
]

def tars_response(sentiment):
	
	if sentiment == "positive":
		return random.choice(positive_response)
	elif sentiment == "neutral":
		return random.choice(neutral_response)
	else:
	    return random.choice(negative_response)	
	  
def speak(text):
	tts=gTTS(text=text, lang='en')
	filename = "tars_reply.mp3"
	tts.save(filename)
	os.system(f"mpg123 {filename}")
	
def listen():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		print("TARS: LISTENING")
		audio = r.listen(source)
	try:	
		text = r.recognize_google(audio)
		print("You:",text)
		return text
	except sr.UnknownValueError:
		print("TARS:speak clearly dummbo ")
		speak("speak clearly DUMBASS ")
		return None
	except sr.RequestError:
		print("TARS:speech service unavailable")
		speak("speech service unavailabel")
		return None
		
		
if __name__ =="__main__":
	print("TARS:whats up man, start talking")
	speak("whats up man, start talking")
	
	while True:
		user_input = listen()
		
		if user_input is None:
			continue
			
		if user_input.lower() in ["bye","exit","quit"]:
			print("TARS:later loser")
			speak("later loser")
			break
		sentiment = analyze_sentiment(user_input)
		reply = tars_response(sentiment)	
        
		print("TARS:",reply)
		speak(reply)
		
