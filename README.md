# Tech_Doc
# Problem statement:

The aim of this project is to develop a user friendly and efficient python application that uses custom made Natural language processing technique combined with speech to text api to comprehend a long input video (over 40 mins) and output a summarized version of the video with highlights of important topics without losing any of the original meaning of the video. The motivation for this project is that in the current situation a lot of learning is happening online through video lectures and also all events are live streamed, through our application we hope to summarize in a comprehensive manner the many hours of learning and entertainment material (in video form), so that the users can make the most effecient use of their time.

# Tech-Stack used:

PyQt5, Speech to text api ,Custom NLP code

In this project we have attempted to create the tec-stack of the proposed solution from scratch. The Tech-stack is Pyqt5 python module for desiging the custom video player to display the summarized video with subtitles and advanced options, Speech to text api and webscrapping was used to get text from the videeo clip in an effient manner, and custom python natural language processing code to comprehend out put of Speech to text api to filter out the important sentences based on the keywords. 

# Custom natural language processing in detail:

We performed two things to extract important lines from the transcript generated 
1 Extraction of keywords from the transcript
2 Extraction of key sentences from the transcript using these key words

So to extract keywords, We used a statistical method called TFIDF scores.

In this firstly we sort the words on basis of their frequency of occurrence in the whole transcript from highest occurrence to lowest occurrence. Each of these lines are assigned their corresponding frequency score 

Then we take the words from the previously arranged order, calculate its frequency of occurrence per line and multiple this with the frequency score of the word which gives us a TFIDF score

Now finally to make our program extract words more efficiently we perform a Wikipedia search on the topic of speech collect all the hyperlink text phrases present in this page and perform another layer of Wikipedia search on each of these hypertext phrases. Now we make a record of all the key phrases in this two layer Wikipedia search. The words within the top 70 percentile TFIDF scores and these Wikipedia key phrase collection together make our final key words collection. 

This way we also grab the words that are less frequent yet relevant to the topic

Finally we extract the key lines, by picking those sentences from the transcript which have a high structural match with the keyword collection we made. We calculate this structural correlation using Levstien distances. We again assign a score to every sentence based on their correlation and the number of key words it has.
The  sentences within the top 70 percentile sentence scores become our key lines.

# Design of PyQT5 Application

# challenges of proposed solution:

Improving the speed of the algorithm and application was most important challenge we faced. To use the api effectively we used multiple api calls in a mutlithreaded manner and also multithreading was used while converting and preparing large video files (over 40 mins) for processing.  
## GUI IMAGES
<img src="https://github.com/yuvaraj-06/Tech_Doc/blob/main/img1.JPG?raw=true">
## SUBTITLES OF THE VIDEO WITH MEDIA PLAYER SETTINGS
<img src="https://github.com/yuvaraj-06/Tech_Doc/blob/main/img2.JPG?raw=true">
