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

