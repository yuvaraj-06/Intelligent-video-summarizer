from threading import Thread
import requests

import base64
from moviepy.editor import *
url = "https://proxy.api.deepaffects.com/audio/generic/api/v1/async/asr"
#"https://webhook.site/9a465f54-10e2-44a7-b8d6-989c17c9bf50"
#

audio_file_name="mity.wav"

clipA = VideoFileClip("apple.mp4")
clipB = VideoFileClip("apple.mp4")
clipC = VideoFileClip("apple.mp4")
clipD = VideoFileClip("apple.mp4")

import moviepy.editor as mp
def a():
    clip1 = clipA.subclip(62.4, 180)
    clip1.write_videofile("clip1.mp4")
    clipa = mp.VideoFileClip(r"clip1.mp4")
    clipa.audio.write_audiofile(r"mit1.wav")

def b():
    clip2 = clipB.subclip(180, 300)
    clip2.write_videofile("clip2.mp4")
    clipb = mp.VideoFileClip(r"clip2.mp4")
    clipb.audio.write_audiofile(r"mit2.wav")
def c():
    clip3 = clipC.subclip(300, 420)
    clip3.write_videofile("clip3.mp4")
    clipc = mp.VideoFileClip(r"clip3.mp4")
    clipc.audio.write_audiofile(r"mit3.wav")
def d():
    clip4 = clipD.subclip(420, 540)
    clip4.write_videofile("clip4.mp4")
    clipd = mp.VideoFileClip(r"clip4.mp4")
    clipd.audio.write_audiofile(r"mit4.wav")
a1=Thread(target =a)
a2=Thread(target =b)
a3=Thread(target =c)
a4=Thread(target =d)
a1.start()
a2.start()
a3.start()
a4.start()
a1.join()
a2.join()
a3.join()
a4.join()

#Test: Final11: sample rate 1411000, enableSpeakerDiarization": False,audioType": "meeting
#Test2: Final12: sample rate 1411000, enableSpeakerDiarization": False,audioType": "meeting, lang: eng-GB
#Test3: Final13: sample rate 44100, enableSpeakerDiarization": False,audioType": "meeting,lang: eng-GB (uk)
#Test4: Final14: sample rate 44100, enableSpeakerDiarization": False,audioType": "meeting,lang: eng-US
def one():
    querystring1 = {"apikey": "i8gDv4qSRMSjLaW3iFjCSvcPGPv16caE",
                    "webhook": "https://webhook.site/7396dbb9-c236-4997-aa62-571c8aca0ce7"}
    audio_file_name1 = "mit1.wav"
    with open(audio_file_name1, 'rb') as fin1:
        audio_content1 = fin1.read()

    payload1 = {"content":base64.b64encode(audio_content1).decode('utf-8'),"encoding": "WAV", "languageCode": "en-US", "sampleRate": 44100, "audioType": "meeting",
               "enableSpeakerDiarization": False, "enablePunctuation": True}

    #payload["content"] = base64.b64encode(audio_content1).decode('utf-8')
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(url, json=payload1, headers=headers, params=querystring1)
    print(response.text)
#SaWFpL5SZPtEhQYJRNKfFtXzxhhNcqwc
#Due2ogG7EZnO9SS94SDNlsycExyqBHCh
def two():
    querystring2 = {"apikey": "YutmVabaOak8xQuHruvWuGsSURX7dY4N","webhook": "https://webhook.site/a703f1c6-b728-4562-9eee-a91d299c6f8f"}
    audio_file_name2 = "mit2.wav"
    with open(audio_file_name2, 'rb') as fin2:
        audio_content2 = fin2.read()

    payload2 = {"content": base64.b64encode(audio_content2).decode('utf-8'), "encoding": "WAV", "languageCode": "en-US",
                "sampleRate": 44100, "audioType": "meeting",
                "enableSpeakerDiarization": False, "enablePunctuation": True}

    #payload["content"] = base64.b64encode(audio_content2).decode('utf-8')
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(url, json=payload2, headers=headers, params=querystring2)
    print(response.text)
def three():
    querystring3 = {"apikey": "G0phDz499IRPLCJHSObdmsGI131LXhlr","webhook": "https://webhook.site/bb5f026f-6d96-46c8-ac50-5a4d45b79324"}

    audio_file_name3 = "mit3.wav"
    with open(audio_file_name3, 'rb') as fin3:
        audio_content3 = fin3.read()
    payload3 = {"content": base64.b64encode(audio_content3).decode('utf-8'), "encoding": "WAV", "languageCode": "en-US",
                "sampleRate": 44100, "audioType": "meeting",
                "enableSpeakerDiarization": False, "enablePunctuation": True}

    #payload["content"] = base64.b64encode(audio_content3).decode('utf-8')
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(url, json=payload3, headers=headers, params=querystring3)
    print(response.text)
def four():
    querystring4 = {"apikey": "n6oP99r1tGIZeyt77Zxn6LVMUKEtmhlw","webhook": "https://webhook.site/a5d6f48a-b29e-4f8f-96a3-badb60823be4"}
    audio_file_name4 = "mit4.wav"
    with open(audio_file_name4,'rb') as fin4:
        audio_content4 = fin4.read()
    payload4 = {"content": base64.b64encode(audio_content4).decode('utf-8'), "encoding": "WAV", "languageCode": "en-US",
                "sampleRate": 44100, "audioType": "meeting",
                "enableSpeakerDiarization": False, "enablePunctuation": True}

    #payload["content"] = base64.b64encode(audio_content4).decode('utf-8')
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(url, json=payload4, headers=headers, params=querystring4)
    print(response.text)

flag=False
print("started")
t1=Thread(target =one)
t2=Thread(target =two)
t3=Thread(target =three)
t4=Thread(target =four)
t1.start()
t2.start()
t3.start()
t4.start()
t1.join()
t2.join()
t3.join()
t4.join()
def run1():
    import webscrap
def run2():
   import webscrap2
def run3():
    import webscrap3
def run4():
    import webscrap4

r1=Thread(target =run1)
r2=Thread(target =run2)
r3=Thread(target =run3)
r4=Thread(target =run4)
r1.start()
r2.start()
r3.start()
r4.start()
r1.join()
r2.join()
r3.join()
r4.join()
