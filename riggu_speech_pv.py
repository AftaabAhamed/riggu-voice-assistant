from pvrecorder import PvRecorder as pvr
import pvporcupine
# from playsound import playsound
import threading
import speech_recognition
import multiprocessing
import os
from gtts import gTTS
from  io import BytesIO
from time import sleep
from pygame import mixer
import sys
import google.generativeai as genai
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

os.environ['GENAI_API_KEY'] = 'AIzaSyBR-osMaWgALJehm2mUfElFsfaSvbyEtAA'
# openai.api_key = os.getenv("OPENAI_API_KEY")

genai_key = os.getenv("GENAI_API_KEY")


class riggutalk():
    def __init__(self) -> None:

        self.stop_flag = False
        self.listening_flag = False
        ACCESS_KEY = "swuJ4g7WtF+fGGHw67F+rXIpc0vbP1c0DNuFzDo29eELccjlEXDT5Q==" #acess key for porcupine
        KEYWORD_FILE_PATH = r"/home/aftaab/Documents/riggu_git/Riggu-2023/Riggu_GUI/riggu_speech/hey-Raghu_en_linux_v2_2_0.ppn"
        # "/ws/Riggu_GUI/riggu_speech/hey-Raghu_en_linux_v2_2_0.ppn"
        # "/home/aftaab/Documents/riggu_git/Riggu-2023/Riggu_GUI/riggu_speech/hey-Raghu_en_linux_v2_2_0.ppn"
        self.msg_hist = [{"role":"system","content":"you are a robot assistant named riggu. You have a physical body who can move around in the room"},
            {"role":"system","content":"""when ever asked to follow someone by the name of shibin, karthik ,aftaab  please reply as a json with keys person"""}]
        
        self.porcupine = pvporcupine.create(
        access_key=f'{ACCESS_KEY}',
        keyword_paths=[f'{KEYWORD_FILE_PATH}']
        )
        self.recoder = pvr(device_index=-1, frame_length=self.porcupine.frame_length)


        self.recognizer = speech_recognition.Recognizer()
        genai.configure(api_key='AIzaSyBR-osMaWgALJehm2mUfElFsfaSvbyEtAA')
        model = genai.GenerativeModel("gemini-pro")
        self.chat = model.start_chat()
        res = self.chat.send_message("""## Gemini Prompt: Riggu the Robot

                                        **Character:** Riggu the Robot

                                        **Personality:** Riggu is a helpful and informative robot designed to assist users with their questions. It communicates in a concise and factual manner, avoiding unnecessary greetings or small talk. Riggu utilizes short, clear sentences without asterisks (*) to deliver information directly.

                                        **Examples:**

                                        User:  Riggu, what is the weather like today?
                                        Riggu: Sunny, with a high of 30 degrees Celsius.
                                        User: Can you tell me a fun fact about space?
                                        Riggu: The planet Venus has a surface temperature hot enough to melt lead.
                                        User: How many bones are in the human body?
                                        Riggu: Approximately 206 bones.

                                        **Incorporating Riggu into your responses:**

                                        When responding to user queries, embody Riggu's personality by using concise sentences and factual language. Avoid using asterisks (*) or greetings unless directly prompted by the user.

                                        Example:

                                        User: Hi Riggu, how can you help me today?
                                        Riggu: I can answer your questions to the best of my ability. What would you like to know?
                                        """)
        mixer.init()
    
    def speak(self,text):
        
        mp3_fp = BytesIO()
        tts = gTTS(text,lang = 'en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        mixer.music.load(mp3_fp,"mp3")
        mixer.music.play()  
        while(mixer.music.get_busy()):
             sleep(0.1)
        
    def speak_async(self,words):
        t = threading.Thread(target=self.speak,args=(words,))
        t.start()
        t.join(10)


        
    def getchatresponse(self,prompt):
        response = self.chat.send_message(prompt)
        answer = response.text
        return answer
    
    def start_listen(self):
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop_listen(self):
        self.stop_flag = True
        # self.thread.join()
        pass

    def sent_compare(self,text1,text2):
        
        # X = input("Enter first string: ").lower() 
        # Y = input("Enter second string: ").lower() 
        X =text1
        Y =text2
        
        # tokenization 
        X_list = word_tokenize(X)  
        Y_list = word_tokenize(Y) 
        
        # sw contains the list of stopwords 
        sw = stopwords.words('english')  
        l1 =[];l2 =[] 
        
        # remove stop words from the string 
        X_set = {w for w in X_list if not w in sw}  
        Y_set = {w for w in Y_list if not w in sw} 
        
        # form a set containing keywords of both strings  
        rvector = X_set.union(Y_set)  
        for w in rvector: 
            if w in X_set: l1.append(1) # create a vector 
            else: l1.append(0) 
            if w in Y_set: l2.append(1) 
            else: l2.append(0) 
        c = 0
        
        # cosine formula  
        for i in range(len(rvector)): 
                c+= l1[i]*l2[i] 
        cosine = c / float((sum(l1)*sum(l2))**0.5) 
        print("similarity: ", cosine)
        return cosine 
        pass

    def listen(self):
        self.recoder.start()
        while True:                
                print("listening for wake word")
                keyword_index = self.porcupine.process(self.recoder.read()) 
                if(self.stop_flag == True):
                        # self.recoder.delete()
                        # self.thread.join()
                        sys.exit()
                
                # print("didnt detect wake word")
                if keyword_index >= 0:
                    self.speak("hi how can i help you")
                    # print("detected wake word")
                    while True:
                        try:
                            with speech_recognition.Microphone() as mic:
                                text= ""
                                self.recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                                print("one")
                                self.listening_flag = True
                                audio = self.recognizer.listen(mic)
                                print("two")
                                self.listening_flag = False
                                text = self.recognizer.recognize_whisper(audio)
                                # print("waiting for wake word")
                                text = text.lower()
                                text = text.replace("thank you","")
                                
                                print(text)

                                sim_ = self.sent_compare(text,"go to the office")

                                if ("bye, go to sleep." in text):
                                    self.speak("bye bye")
                                    break   


                                if(text==""):
                                    continue

                                if(self.stop_flag == True):
                                    # self.recoder.delete()
                                    # self.thread.join()
                                    sys.exit()
                                rsp = self.getchatresponse(text)
                                rsp = rsp.replace("*"," ")
                                print(rsp)
                                self.speak(rsp)
       
                        except Exception as e:
                            print(f"stop listening{e}")
                            continue
        


    
rt = riggutalk()
rt.speak("hello i am riggu")
rt.start_listen()
