# Tech_Doc
# Problem statement:

The aim of this project is to develop a user friendly and efficient python application that uses custom made Natural language processing technique combined with speech to text api to comprehend a long input video (over 40 mins) and output a summarized version of the video with highlights of important topics without losing any of the original meaning of the video. The motivation for this project is that in the current situation a lot of learning is happening online through video lectures and also all events are live streamed, through our application we hope to summarize in a comprehensive manner the many hours of learning and entertainment material (in video form), so that the users can make the most effecient use of their time.

# Tech-Stack used:

In this project we have attempted to create the tec-stack of the proposed solution from scratch. The Tech-stack is Pyqt5 python module for desiging the custom video player to display the summarized video with subtitles and advanced options, Speech to text api and webscrapping was used to get text from the videeo clip in an effient manner, and custom python natural language processing code to comprehend out put of Speech to text api to filter out the important sentences based on the keywords. 

# Custom natural language processing in detail:

We have mainly used two statistical methods to extract keywords from the transcript generated.

One is the Frequency method where we sort the words on basis of their frequency of occurrence in the whole transcript, and assign these frequency scores to them accordingly and then extract key lines from the transcript using them.

The second method is the TF-IDF(Term Frequency Inverse Document Frequency) where we not just calculate the frequency scores like we did in the previous method but also calculate frequency of occurrence of every keyword generated in the previous method in a every sentence. We then multiply both these in-line frequencies and whole-text-frequencies of every word (which gives a product called the TFIDF score) and then extract key lines using these scores.

In both of these situations we extract the key lines from keywords by picking the sentences that have top 70 percentile  Levlstein ratios with all the key words generated above and they become our key lines.

# challenges of proposed solution:
