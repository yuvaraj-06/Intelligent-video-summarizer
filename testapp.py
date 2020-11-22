from moviepy.editor import *
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Q_ARG, QAbstractItemModel,
                          QFileInfo, qFuzzyCompare, QMetaObject, QModelIndex, QObject, Qt,
                          QThread, QTime, QUrl)
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette
from PyQt5.QtMultimedia import (QAbstractVideoBuffer, QMediaContent,
                                QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
                             QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
                             QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QWidget)


class VideoWidget(QVideoWidget):

    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super(VideoWidget, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.setFullScreen(not self.isFullScreen())
        event.accept()


class PlaylistModel(QAbstractItemModel):
    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)

        self.m_playlist = None

    def rowCount(self, parent=QModelIndex()):
        return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()):
        return self.ColumnCount if not parent.isValid() else 0

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row,
                                column) if self.m_playlist is not None and not parent.isValid() and row >= 0 and row < self.m_playlist.mediaCount() and column >= 0 and column < self.ColumnCount else QModelIndex()

    def parent(self, child):
        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.m_playlist.media(index.row()).canonicalUrl()
                return QFileInfo(location.path()).fileName()

            return self.m_data[index]

        return None

    def playlist(self):
        return self.m_playlist

    def setPlaylist(self, playlist):
        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.disconnect(
                self.beginInsertItems)
            self.m_playlist.mediaInserted.disconnect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.disconnect(
                self.beginRemoveItems)
            self.m_playlist.mediaRemoved.disconnect(self.endRemoveItems)
            self.m_playlist.mediaChanged.disconnect(self.changeItems)

        self.beginResetModel()
        self.m_playlist = playlist

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.connect(
                self.beginInsertItems)
            self.m_playlist.mediaInserted.connect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.connect(
                self.beginRemoveItems)
            self.m_playlist.mediaRemoved.connect(self.endRemoveItems)
            self.m_playlist.mediaChanged.connect(self.changeItems)

        self.endResetModel()

    def beginInsertItems(self, start, end):
        self.beginInsertRows(QModelIndex(), start, end)

    def endInsertItems(self):
        self.endInsertRows()

    def beginRemoveItems(self, start, end):
        self.beginRemoveRows(QModelIndex(), start, end)

    def endRemoveItems(self):
        self.endRemoveRows()

    def changeItems(self, start, end):
        self.dataChanged.emit(self.index(start, 0),
                              self.index(end, self.ColumnCount))


class PlayerControls(QWidget):
    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()
    next = pyqtSignal()
    previous = pyqtSignal()
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    changeRate = pyqtSignal(float)

    def __init__(self, parent=None):
        super(PlayerControls, self).__init__(parent)

        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False

        self.playButton = QToolButton(clicked=self.playClicked)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        self.nextButton = QToolButton(clicked=self.next)
        self.nextButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.previousButton = QToolButton(clicked=self.previous)
        self.previousButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSkipBackward))

        self.muteButton = QToolButton(clicked=self.muteClicked)
        self.muteButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaVolume))

        self.volumeSlider = QSlider(Qt.Horizontal,
                                    sliderMoved=self.changeVolume)
        self.volumeSlider.setRange(0, 100)

        self.rateBox = QComboBox(activated=self.updateRate)
        self.rateBox.addItem("0.5x", 0.5)
        self.rateBox.addItem("1.0x", 1.0)
        self.rateBox.addItem("2.0x", 2.0)
        self.rateBox.setCurrentIndex(1)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.rateBox)
        self.setLayout(layout)

    def state(self):
        return self.playerState

    def setState(self, state):
        if state != self.playerState:
            self.playerState = state

            if state == QMediaPlayer.StoppedState:
                self.stopButton.setEnabled(False)
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
            elif state == QMediaPlayer.PlayingState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
            elif state == QMediaPlayer.PausedState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def volume(self):
        return self.volumeSlider.value()

    def setVolume(self, volume):
        self.volumeSlider.setValue(volume)

    def isMuted(self):
        return self.playerMuted

    def setMuted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted

            self.muteButton.setIcon(
                self.style().standardIcon(
                    QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume))

    def playClicked(self):
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause.emit()

    def muteClicked(self):
        self.changeMuting.emit(not self.playerMuted)

    def playbackRate(self):
        return self.rateBox.itemData(self.rateBox.currentIndex())

    def setPlaybackRate(self, rate):
        for i in range(self.rateBox.count()):
            if qFuzzyCompare(rate, self.rateBox.itemData(i)):
                self.rateBox.setCurrentIndex(i)
                return

        self.rateBox.addItem("%dx" % rate, rate)
        self.rateBox.setCurrentIndex(self.rateBox.count() - 1)

    def updateRate(self):
        self.changeRate.emit(self.playbackRate())


class FrameProcessor(QObject):
    histogramReady = pyqtSignal(list)

    @pyqtSlot(QVideoFrame, int)
    def processFrame(self, frame, levels):
        histogram = [0.0] * levels

        if levels and frame.map(QAbstractVideoBuffer.ReadOnly):
            pixelFormat = frame.pixelFormat()

            if pixelFormat == QVideoFrame.Format_YUV420P or pixelFormat == QVideoFrame.Format_NV12:
                # Process YUV data.
                bits = frame.bits()
                for idx in range(frame.height() * frame.width()):
                    histogram[(bits[idx] * levels) >> 8] += 1.0
            else:
                imageFormat = QVideoFrame.imageFormatFromPixelFormat(pixelFormat)
                if imageFormat != QImage.Format_Invalid:
                    # Process RGB data.
                    image = QImage(frame.bits(), frame.width(), frame.height(), imageFormat)

                    for y in range(image.height()):
                        for x in range(image.width()):
                            pixel = image.pixel(x, y)
                            histogram[(qGray(pixel) * levels) >> 8] += 1.0

            # Find the maximum value.
            maxValue = 0.0
            for value in histogram:
                if value > maxValue:
                    maxValue = value

            # Normalise the values between 0 and 1.
            if maxValue > 0.0:
                for i in range(len(histogram)):
                    histogram[i] /= maxValue

            frame.unmap()

        self.histogramReady.emit(histogram)


class HistogramWidget(QWidget):

    def __init__(self, parent=None):
        super(HistogramWidget, self).__init__(parent)

        self.m_levels = 128
        self.m_isBusy = False
        self.m_histogram = []
        self.m_processor = FrameProcessor()
        self.m_processorThread = QThread()

        self.m_processor.moveToThread(self.m_processorThread)
        self.m_processor.histogramReady.connect(self.setHistogram)

    def __del__(self):
        self.m_processorThread.quit()
        self.m_processorThread.wait(10000)

    def setLevels(self, levels):
        self.m_levels = levels

    def processFrame(self, frame):
        if self.m_isBusy:
            return

        self.m_isBusy = True
        QMetaObject.invokeMethod(self.m_processor, 'processFrame',
                                 Qt.QueuedConnection, Q_ARG(QVideoFrame, frame),
                                 Q_ARG(int, self.m_levels))

    @pyqtSlot(list)
    def setHistogram(self, histogram):
        self.m_isBusy = False
        self.m_histogram = list(histogram)
        self.update()


class Player(QWidget):
    fullScreenChanged = pyqtSignal(bool)

    def __init__(self, playlist, parent=None):
        super(Player, self).__init__(parent)

        self.colorDialog = None
        self.trackInfo = ""
        self.statusInfo = ""
        self.duration = 0

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)
        self.player.mediaStatusChanged.connect(self.statusChanged)
        self.player.bufferStatusChanged.connect(self.bufferingProgress)
        self.player.videoAvailableChanged.connect(self.videoAvailableChanged)
        self.player.error.connect(self.displayErrorMessage)

        self.videoWidget = VideoWidget()
        self.player.setVideoOutput(self.videoWidget)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
            self.playlistModel.index(self.playlist.currentIndex(), 0))

        self.playlistView.activated.connect(self.jump)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.player.duration() / 1000)

        self.labelDuration = QLabel()
        self.slider.sliderMoved.connect(self.seek)

        self.labelHistogram = QLabel()

        self.histogram = HistogramWidget()
        histogramLayout = QHBoxLayout()
        histogramLayout.addWidget(self.labelHistogram)
        histogramLayout.addWidget(self.histogram, 1)

        self.probe = QVideoProbe()
        self.probe.videoFrameProbed.connect(self.histogram.processFrame)
        self.probe.setSource(self.player)

        openButton = QPushButton("Open", clicked=self.open)

        controls = PlayerControls()
        controls.setState(self.player.state())
        controls.setVolume(self.player.volume())
        controls.setMuted(controls.isMuted())

        controls.play.connect(self.player.play)
        controls.pause.connect(self.player.pause)
        controls.stop.connect(self.player.stop)
        controls.next.connect(self.playlist.next)
        controls.previous.connect(self.previousClicked)
        controls.changeVolume.connect(self.player.setVolume)
        controls.changeMuting.connect(self.player.setMuted)
        controls.changeRate.connect(self.player.setPlaybackRate)
        controls.stop.connect(self.videoWidget.update)

        self.player.stateChanged.connect(controls.setState)
        self.player.volumeChanged.connect(controls.setVolume)
        self.player.mutedChanged.connect(controls.setMuted)

        self.fullScreenButton = QPushButton("FullScreen")
        self.fullScreenButton.setCheckable(True)

        self.colorButton = QPushButton("Color Options...")
        self.colorButton.setEnabled(False)
        self.colorButton.clicked.connect(self.showColorDialog)

        displayLayout = QHBoxLayout()
        displayLayout.addWidget(self.videoWidget, 2)
        displayLayout.addWidget(self.playlistView)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addStretch(1)
        controlLayout.addWidget(controls)
        controlLayout.addStretch(1)
        controlLayout.addWidget(self.fullScreenButton)
        controlLayout.addWidget(self.colorButton)

        layout = QVBoxLayout()
        layout.addLayout(displayLayout)
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.slider)
        hLayout.addWidget(self.labelDuration)
        layout.addLayout(hLayout)
        layout.addLayout(controlLayout)
        layout.addLayout(histogramLayout)

        self.setLayout(layout)

        if not self.player.isAvailable():
            QMessageBox.warning(self, "Service not available",
                                "The QMediaPlayer object does not have a valid service.\n"
                                "Please check the media service plugins are installed.")

            controls.setEnabled(False)
            self.playlistView.setEnabled(False)
            openButton.setEnabled(False)
            self.colorButton.setEnabled(False)
            self.fullScreenButton.setEnabled(False)

        self.metaDataChanged()

        self.addToPlaylist(playlist)


    def open(self):
        global vid
        fileNames, _ = QFileDialog.getOpenFileNames(self, "Open Files")
        fx=fileNames[0]
        fx = fx.split("/")
        vid = str(fx[-1])

        ##import apitestspeech
        from threading import Thread
        import requests
        global a, b
        a = 0
        b = 0
        import base64

        url = "https://proxy.api.deepaffects.com/audio/generic/api/v1/async/asr"
        # "https://webhook.site/9a465f54-10e2-44a7-b8d6-989c17c9bf50"
        #

        #audio_file_name = "mity.wav"
        clip = VideoFileClip(vid)
        #vid="apple.mp4"
        clipA = VideoFileClip(vid)
        clipB = VideoFileClip(vid)
        clipC = VideoFileClip(vid)
        clipD = VideoFileClip(vid)



        # getting duration of the video

        def intervals(parts, duration):
            part_duration = duration / parts
            return [(i * part_duration, (i + 1) * part_duration) for i in range(parts)]

        duration = clip.duration
        dur = (intervals(4, duration))

        import moviepy.editor as mp
        def a():
            x1=dur[0][0]
            y1=dur[0][1]
            clip1 = clipA.subclip(x1,y1)
            clip1.write_videofile("clip1.mp4")
            clipa = mp.VideoFileClip(r"clip1.mp4")
            clipa.audio.write_audiofile(r"v1.wav")

        def b():
            x2 = dur[1][0]
            y2 = dur[1][1]

            clip2 = clipB.subclip(x2, y2)
            clip2.write_videofile("clip2.mp4")
            clipb = mp.VideoFileClip(r"clip2.mp4")
            clipb.audio.write_audiofile(r"v2.wav")

        def c():
            x3 = dur[2][0]
            y3 = dur[2][1]

            clip3 = clipC.subclip(x3, y3)
            clip3.write_videofile("clip3.mp4")
            clipc = mp.VideoFileClip(r"clip3.mp4")
            clipc.audio.write_audiofile(r"v3.wav")

        def d():
            x4 = dur[3][0]
            y4 = dur[3][1]

            clip4 = clipD.subclip(x4, y4)
            clip4.write_videofile("clip4.mp4")
            clipd = mp.VideoFileClip(r"clip4.mp4")
            clipd.audio.write_audiofile(r"v4.wav")

        a1 = Thread(target=a)
        a2 = Thread(target=b)
        a3 = Thread(target=c)
        a4 = Thread(target=d)
        a1.start()
        a2.start()
        a3.start()
        a4.start()
        a1.join()
        a2.join()
        a3.join()
        a4.join()

        # Test: Final11: sample rate 1411000, enableSpeakerDiarization": False,audioType": "meeting
        # Test2: Final12: sample rate 1411000, enableSpeakerDiarization": False,audioType": "meeting, lang: eng-GB
        # Test3: Final13: sample rate 44100, enableSpeakerDiarization": False,audioType": "meeting,lang: eng-GB (uk)
        # Test4: Final14: sample rate 44100, enableSpeakerDiarization": False,audioType": "meeting,lang: eng-US
        def one():
            querystring1 = {"apikey": "i8gDv4qSRMSjLaW3iFjCSvcPGPv16caE",
                            "webhook": "https://webhook.site/7396dbb9-c236-4997-aa62-571c8aca0ce7"}
            audio_file_name1 = "v1.wav"
            with open(audio_file_name1, 'rb') as fin1:
                audio_content1 = fin1.read()

            payload1 = {"content": base64.b64encode(audio_content1).decode('utf-8'), "encoding": "WAV",
                        "languageCode": "en-IN", "sampleRate": 44100, "audioType": "meeting",
                        "enableSpeakerDiarization": False, "enablePunctuation": True}

            # payload["content"] = base64.b64encode(audio_content1).decode('utf-8')
            headers = {
                'Content-Type': "application/json",
            }
            response = requests.post(url, json=payload1, headers=headers, params=querystring1)
            print(response.text)

        # SaWFpL5SZPtEhQYJRNKfFtXzxhhNcqwc
        # Due2ogG7EZnO9SS94SDNlsycExyqBHCh
        def two():
            querystring2 = {"apikey": "YutmVabaOak8xQuHruvWuGsSURX7dY4N",
                            "webhook": "https://webhook.site/a703f1c6-b728-4562-9eee-a91d299c6f8f"}
            audio_file_name2 = "v2.wav"
            with open(audio_file_name2, 'rb') as fin2:
                audio_content2 = fin2.read()

            payload2 = {"content": base64.b64encode(audio_content2).decode('utf-8'), "encoding": "WAV",
                        "languageCode": "en-IN",
                        "sampleRate": 44100, "audioType": "meeting",
                        "enableSpeakerDiarization": False, "enablePunctuation": True}

            # payload["content"] = base64.b64encode(audio_content2).decode('utf-8')
            headers = {
                'Content-Type': "application/json",
            }
            response = requests.post(url, json=payload2, headers=headers, params=querystring2)
            print(response.text)

        def three():
            querystring3 = {"apikey": "G0phDz499IRPLCJHSObdmsGI131LXhlr",
                            "webhook": "https://webhook.site/bb5f026f-6d96-46c8-ac50-5a4d45b79324"}

            audio_file_name3 = "v3.wav"
            with open(audio_file_name3, 'rb') as fin3:
                audio_content3 = fin3.read()
            payload3 = {"content": base64.b64encode(audio_content3).decode('utf-8'), "encoding": "WAV",
                        "languageCode": "en-IN",
                        "sampleRate": 44100, "audioType": "meeting",
                        "enableSpeakerDiarization": False, "enablePunctuation": True}

            # payload["content"] = base64.b64encode(audio_content3).decode('utf-8')
            headers = {
                'Content-Type': "application/json",
            }
            response = requests.post(url, json=payload3, headers=headers, params=querystring3)
            print(response.text)

        def four():
            querystring4 = {"apikey": "n6oP99r1tGIZeyt77Zxn6LVMUKEtmhlw",
                            "webhook": "https://webhook.site/a5d6f48a-b29e-4f8f-96a3-badb60823be4"}
            audio_file_name4 = "v4.wav"
            with open(audio_file_name4, 'rb') as fin4:
                audio_content4 = fin4.read()
            payload4 = {"content": base64.b64encode(audio_content4).decode('utf-8'), "encoding": "WAV",
                        "languageCode": "en-IN",
                        "sampleRate": 44100, "audioType": "meeting",
                        "enableSpeakerDiarization": False, "enablePunctuation": True}

            # payload["content"] = base64.b64encode(audio_content4).decode('utf-8')
            headers = {
                'Content-Type': "application/json",
            }
            response = requests.post(url, json=payload4, headers=headers, params=querystring4)
            print(response.text)

        flag = False
        print("API CALL STARTED")
        t1 = Thread(target=one)
        t2 = Thread(target=two)
        t3 = Thread(target=three)
        t4 = Thread(target=four)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()

        print("WEB SCRAPING STARTED")
        def run1():
            import webscrap

        def run2():
            import webscrap2

        def run3():
            import webscrap3

        def run4():
            import webscrap4

        r1 = Thread(target=run1)
        r2 = Thread(target=run2)
        r3 = Thread(target=run3)
        r4 = Thread(target=run4)
        r1.start()
        r2.start()
        r3.start()
        r4.start()
        r1.join()
        r2.join()
        r3.join()
        r4.join()

        def sum():
            print("NLP STARTED")
            import wikipedia
            from fuzzywuzzy import process
            from fuzzywuzzy import fuzz
            import copy
            import numpy as np
            def superImportant(topic):
                content = wikipedia.summary(topic)
                pageObj = wikipedia.WikipediaPage(topic)

                hyperLinks1 = []
                nonhyperLinks = content.split()
                for words2 in pageObj.links:
                    if words2 in content:
                        hyperLinks1.append(words2)

                contentWords = list(set(copy.deepcopy(hyperLinks1) + nonhyperLinks))

                fails = 0

                for words in hyperLinks1:
                    try:
                        content = wikipedia.summary(words)
                        pageObj = wikipedia.WikipediaPage(words)
                        count = 0
                        for words2 in pageObj.links:
                            if words2 in content:
                                contentWords.append(words2)
                                count += 1
                            if count >= 1 * len(hyperLinks1):
                                break
                    except:
                        fails += 1

                contentWords = set((" ".join(contentWords)).split())
                return contentWords

            def changePriorities(dic, mapWords):
                frequencies = []
                for k, v in dic.items():
                    frequencies.append(v)
                X = copy.deepcopy(np.percentile(np.array(frequencies), 95))

                misMatches = 0
                for words in mapWords:
                    if words in dic.keys():
                        dic[words] = X
                    elif words.lower() in dic.keys():
                        dic[words.lower()] = X
                    else:
                        misMatches += 1

                return dic, misMatches

            import copy
            import nltk
            import numpy as np
            import string
            from sklearn.feature_extraction.text import CountVectorizer
            from nltk.corpus import stopwords
            from fuzzywuzzy import process
            from fuzzywuzzy import fuzz
            from scipy import stats
            import matplotlib.pyplot as plt
            nltk.download('wordnet')
            nltk.download('stopwords')

            def chunk(sourceFile, wordsPerLine=None, endLineAt=None):
                fi = open(sourceFile, "r+")
                text = fi.read()
                text = text.replace("\n", "")

                if wordsPerLine != None:
                    text = text.split()
                    for words in range(1, len(text) + 1):
                        if words % 3 == 0:
                            text[words - 1] = text[words - 1] + "\n"
                    fi.seek(0)
                    fi.write(" ".join(text))
                if endLineAt != None:

                    for words in endLineAt:
                        text = text.split(words)
                        text = "\n".join(text)

                    fi.seek(0)
                    fi.write(text)

                fi.close()
                return

            def getKey(D, val):
                for key, value in D.items():
                    if val == value:
                        return key
                return -1

            def completeFiltering(singleStringTxt, multiLineTxt, limitOnFreq, limitOnDataW=10000):
                wholeText = singleStringTxt
                cleansed = wholeText.split()[:limitOnDataW]
                table = str.maketrans("", "", string.punctuation)
                cleansed = [w.translate(table) for w in cleansed]
                patched = " ".join(cleansed)
                cleansed = patched.split()
                cleansed = [words for words in cleansed if not words.lower() in stopwords.words()]

                cleansedTxt = " ".join(cleansed)

                wholeText = [cleansedTxt]
                lineWiseText = multiLineTxt

                # list of text documents
                # create the transform
                vectorizer1 = CountVectorizer()
                vectorizer2 = CountVectorizer()
                # tokenize and build vocab
                vectorizer1.fit(wholeText)
                vectorizer2.fit(lineWiseText)

                # summarize
                wToInd1 = vectorizer1.vocabulary_
                wToInd2 = vectorizer2.vocabulary_
                # encode document
                vector1 = vectorizer1.transform(wholeText)
                vector2 = vectorizer2.transform(lineWiseText)
                # summarize encoded vector
                v1 = vector1.toarray()
                v2 = vector2.toarray()

                finalCount = np.sum(v1, axis=0, keepdims=False)

                countDict1 = dict()

                countDict2 = dict()
                priorities2 = dict()
                for ind in range(len(finalCount)):
                    if finalCount[ind] >= limitOnFreq:
                        countDict1[getKey(wToInd1, ind)] = finalCount[ind]

                for lines in range(v2.shape[0]):
                    countDict = dict()
                    for ind in range(v2.shape[1]):
                        if v2[lines][ind] >= limitOnFreq:
                            countDict[getKey(wToInd2, ind)] = v2[lines][ind]

                    priorities = sorted(countDict, key=countDict.get, reverse=True)

                    countDict2[str(lines + 1)] = countDict
                    priorities2[str(lines + 1)] = priorities

                contentWords = superImportant("Information security")
                countDict1, misMatch = changePriorities(countDict1, contentWords)
                print("These many got mismatched in WIKEPIDA NEURAL NETWORK: ", misMatch)

                priorities1 = sorted(countDict1, key=countDict1.get, reverse=True)

                return priorities1, priorities2, countDict1, countDict2

            def fuzzyWayCondense(fileSource, priorities1, priorities2, prioritiesMap1, prioritiesMap2, limitOnLines=3,
                                 limitOnDataL=100, method="Frequency", printLineScores=False):
                if method == "Frequency":
                    priorities = priorities1
                    prioritiesMap = prioritiesMap1
                elif method == "TF-IDF":
                    priorities = priorities1
                    prioritiesMap = prioritiesMap1
                    prioritiesMapext = prioritiesMap2
                    includeTFIDF = np.zeros((limitOnDataL, len(priorities)))
                fi = open(fileSource, "r")
                include = np.zeros((limitOnDataL, len(priorities)))

                wholeLines = fi.readlines()[:limitOnDataL]
                maintain = dict()

                for lines in range(1, limitOnDataL + 1):
                    maintain[str(lines)] = []

                fi.close()

                for words in priorities:
                    options = process.extract(words, wholeLines, limit=limitOnDataL)
                    for line, score in options:

                        if (words in line.split()) and method == "Frequency":
                            maintain[str(wholeLines.index(line) + 1)].append(words)
                            include[wholeLines.index(line)][priorities.index(words)] = score * prioritiesMap[words]
                        elif (words in line.split()) and method == "TF-IDF":
                            maintain[str(wholeLines.index(line) + 1)].append(words)
                            includeTFIDF[wholeLines.index(line)][priorities.index(words)] = \
                                prioritiesMapext[str(wholeLines.index(line) + 1)][words] * prioritiesMap[words]
                if method == "TF-IDF":

                    includeTFIDF = list(np.sum(includeTFIDF, axis=0))

                    for words in priorities:
                        options = process.extract(words, wholeLines, limit=limitOnDataL)
                        for line, score in options:

                            if (words in line.split()):
                                include[wholeLines.index(line)][priorities.index(words)] = score * includeTFIDF[
                                    priorities.index(words)]

                for lines in range(1, limitOnDataL + 1):
                    maintain[str(lines)] = set(maintain[str(lines)])

                include = list(np.sum(include, axis=1))
                includeTemp = np.array(copy.deepcopy(include))

                if printLineScores == True:
                    print("\nThe Scores of the Sentences from 1 to", limitOnDataL, " are as follows \n", include)
                    print("\nThe Key Words Per Line for all the lines are : \n", maintain)

                condensedLines = []
                condensedLinesIndices = []
                if limitOnLines != "NormSTDPick":
                    includeTemp = (np.sort(includeTemp))[::-1]
                    for i in range(limitOnLines):
                        condensedLines.append(wholeLines[include.index(includeTemp[i])])
                        condensedLinesIndices.append(include.index(includeTemp[i]) + 1)
                        include[include.index(includeTemp[i])] = -1
                else:
                    includeTemp = np.array([(value >= np.percentile(includeTemp, 50)) for value in includeTemp]).astype(
                        int)
                    includeTemp = np.reshape(np.argwhere(includeTemp), (-1,)) + 1
                    condensedLines = [wholeLines[i - 1] for i in includeTemp]
                    condensedLinesIndices = includeTemp

                condensedText = " ".join(condensedLines)

                return condensedText, condensedLines, condensedLinesIndices

            import json

            T1path = "final1.txt"  # "/content/drive/My Drive/transcript1"
            T2path = "final2.txt"  # "/content/drive/My Drive/transcript2"
            T3path = "final3.txt"  # "/content/drive/My Drive/transcript3"
            T4path = "final4.txt"  # "/content/drive/My Drive/transcript4"
            Tpath = "1.txt"  # "/content/drive/My Drive/entireTranscript.txt"

            transcript = ""
            tpt1 = open(T1path, "r")
            T1 = tpt1.read()
            T1dict = eval(T1)
            tpt1.close()

            tpt2 = open(T2path, "r")
            T2 = tpt2.read()
            T2dict = eval(T2)
            tpt2.close()

            tpt3 = open(T3path, "r")
            T3 = tpt3.read()
            T3dict = eval(T3)
            # T3dict = json.loads(T3dict.decode("utf-8"))
            tpt3.close()

            tpt4 = open(T4path, "r")
            T4 = tpt4.read()
            T4dict = eval(T4)
            # T4dict = json.loads(T4dict.decode("utf-8"))
            tpt4.close()

            transcript += T1dict["response"]["transcript"]
            transcript += T2dict["response"]["transcript"]
            transcript += T3dict["response"]["transcript"]
            transcript += T4dict["response"]["transcript"]

            tpt = open(Tpath, "w")
            tpt.write(transcript)
            tpt.close()

            # tpt  = open(Tpath,"r")
            Tdicts = [T1dict, T2dict, T3dict, T4dict]
            # print(tpt.read())

            # RUN THIS CELL WITH SPECIFIED PATH TO LOAD ALL THE TEXT FILE AS STRING INTO "wholeText" AND TEXT FILE AS LINES INTO "lineWiseText"

            # path = "/content/drive/My Drive/TedTranscript.txt" #Path of the file from the drive
            path = Tpath  # "/content/drive/My Drive/entireTranscript.txt"

            chunk(path, endLineAt=[".", "?"])

            fi = open(path, "r")
            wholeText = fi.read()
            fi.seek(0)
            totalWords = len((fi.read()).split())
            fi.seek(0)
            totalLines = len(fi.readlines())
            fi.seek(0)
            lineWiseText = fi.readlines()
            fi.close()

            # print("Total Lines present in the Source File is : ", totalLines)
            # print("Total Words present in the source File is : ", totalWords)

            # "completeFiltering" func takes "wholeText", "lineWiseText", "limitOnFreq" (let this be unchanged), "limitOnDataW" (this equals the "totalWords" in above cell)
            # "completeFiltering" func returns priorities1,2 and countDict1,2 which are used more for internal purposes so I'm hiding these outputs
            priorities1, priorities2, countDict1, countDict2 = completeFiltering(wholeText, lineWiseText, limitOnFreq=1,
                                                                                 limitOnDataW=totalWords)

            # print("\nTop Prior Words of 10K Words data : ", priorities1)
            # print("\nTop Prior Words of every Line data : ", priorities2)

            # "fuzzyWayCondense" func takes "path", "priorities1,2", "countDict1,2", "limitOnLines" (this is can be anything <= "totalLines"), "limitonDataL"(this equals the "totalLines" in above cell), "method" (let it be unchanged), "printLineScores"(let it be False setting it to True just prints scores which are of no use to u)
            # "fuzzyWayCondense" func returns "condensedText"(optional use to u), "condensedLines"(optional use to u just gives list of line strings) ,"condensedLinesIndices1(u might need this)"
            condensedText, condensedLines, condensedLinesIndices1 = fuzzyWayCondense(path, priorities1, priorities2,
                                                                                     countDict1,
                                                                                     countDict2,
                                                                                     limitOnLines="NormSTDPick",
                                                                                     limitOnDataL=totalLines,
                                                                                     method="TF-IDF",
                                                                                     printLineScores=False)
            #print("\nThis is the TF-IDF Way : \n")
            #print("\nThe Original Lines which made thorugh the filtering process  are the line numbers : \n",
             #     condensedLinesIndices1)
            # print("\nOverall the condensed Text : \n", condensedText)

            # "fuzzyWayCondense" func takes "path", "priorities1,2", "countDict1,2", "limitOnLines" (this is can be anything <= "totalLines"), "limitonDataL"(this equals the "totalLines" in above cell), "method" (let it be unchanged), "printLineScores"(let it be False setting it to True just prints scores which are of no use to u)
            # "fuzzyWayCondense" func returns "condensedText"(optional use to u), "condensedLines"(optional use to u just gives list of line strings) ,"condensedLinesIndices2(u might need this)"
            # condensedText, condensedLines, condensedLinesIndices2 = fuzzyWayCondense(path,priorities1, priorities2,countDict1, countDict2, limitOnLines="NormSTDPick", limitOnDataL = totalLines, method = "Frequency", printLineScores=False)
            # print("\nThis is the Frequency Way : \n")
            # print("\nThe Original Lines which made thorugh the filtering process  are the line numbers : \n", condensedLinesIndices2)
            # print("\nOverall the condensed Text : \n", condensedText)

            # "finalSet" gives union of results of both methods
            # finalSet =  set(condensedLinesIndices1).union(set(condensedLinesIndices2))
            finalSet = set(condensedLinesIndices1)
            print("\nConsider these lines as Important : ", finalSet)
            print("\nPercentage of Condensation of initial Text is : {:.4f}%".format(
               ((totalLines - len(finalSet)) / totalLines) * 100))

            Jsonpath = "2.txt"  # "/content/drive/My Drive/entireJasonObj.txt"

            correction = 0
            for transcripts in range(4):
                for times in Tdicts[transcripts]["response"]["words"]:
                    times["start"] = times["start"] + correction
                    times["end"] = times["end"] + correction
                    mark = times["end"]

                correction = mark

            jsonObjs = {"response": dict()}
            jsonObjs["response"]["words"] = T1dict["response"]["words"] + T2dict["response"]["words"] + \
                                            T3dict["response"][
                                                "words"] + T4dict["response"]["words"]
            jsonObjs = str(jsonObjs)
            json = open(Jsonpath, "w")
            json.write(jsonObjs)
            json.close()

            pathr = Jsonpath  # "/content/drive/My Drive/tedxtJasonObject" # PATH TO THE TEXT FILE CONTAINING JASON OBJECT (DICTIONARY OF REQUEST ID, RESPONSE, TIMESTAMPS OF WORDS ....)
            fi = open(pathr, "r")
            fullDataDict = eval(fi.read())

            def convert(seconds):
                seconds = seconds % (24 * 3600)
                hour = seconds // 3600
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60

                return "%d:%02d:%02d" % (hour, minutes, seconds)

            wholeWords = wholeText.split()
            wholeLines = lineWiseText
            prevWordsCount = dict()
            wds = 0
            for sen in wholeLines:
                prevWordsCount[str(wholeLines.index(sen) + 1)] = wds
                wds += len(sen.split())

            timeStamps = dict()

            for line in finalSet:

                try:
                    startInd = prevWordsCount[str(line)]
                    endInd = prevWordsCount[str(line + 1)] - 1
                    # USE "convert" if u need the output time stamps to be in HH:MM:SS if not remove "convert"
                    timeRange = (
                        fullDataDict["response"]["words"][startInd]["start"],
                        fullDataDict["response"]["words"][endInd]["end"])
                    timeStamps[int(line)] = timeRange
                    count = 1
                except:
                    print("")

            c = 0
            Stamps = []
            for line in sorted(timeStamps):
                c += 1
                Stamps.append(timeStamps[line])

            stamps1 = []
            x = 0

            for i in Stamps:
                d = i[1] - i[0]
                y = x + d
                stamps1.append((x, y))
                x = y



            global ddd
            ddd = dict(zip(stamps1,condensedLines))
            print(ddd)
           # print(Stamps)
            clip = VideoFileClip(vid)
            V = []
            for t in range(0, len(Stamps)):
                a = Stamps[t][0]
                b = Stamps[t][1]
                clipx = clip.subclip(a,b)
                tempvid = clipx
                V.append(tempvid)
            # x concatinating both the clips
            final = concatenate_videoclips(V)
            vid1 = vid.replace("mp4", "avi")
            final.write_videofile(vid1, codec='rawvideo')
            print("FILE PROCESSING IS DONE")


        sum()
        a = fileNames[0]
        a= fileNames[0].replace("lecture.mp4","lecture4.avi")
        print(a)
        fileNames.pop()
        fileNames.append(a)
        print("ADDED TO PLAYLIST")
        self.addToPlaylist(fileNames)



    def addToPlaylist(self, fileNames):
        for name in fileNames:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                if fileInfo.suffix().lower() == 'm3u':
                    self.playlist.load(url)
                else:
                    self.playlist.addMedia(QMediaContent(url))
            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))

    def durationChanged(self, duration):
        duration /= 1000

        self.duration = duration
        self.slider.setMaximum(duration)

    def positionChanged(self, progress):
        progress /= 1000

        if not self.slider.isSliderDown():
            self.slider.setValue(progress)

        self.updateDurationInfo(progress)

    def metaDataChanged(self):
        if self.player.isMetaDataAvailable():
            self.setTrackInfo("%s - %s" % (
                self.player.metaData(QMediaMetaData.AlbumArtist),
                self.player.metaData(QMediaMetaData.Title)))

    def previousClicked(self):
        # Go to the previous track if we are within the first 5 seconds of
        # playback.  Otherwise, seek to the beginning.
        if self.player.position() <= 5000:
            self.playlist.previous()
        else:
            self.player.setPosition(0)

    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.player.play()

    def playlistPositionChanged(self, position):
        self.playlistView.setCurrentIndex(
            self.playlistModel.index(position, 0))

    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)

    def statusChanged(self, status):
        self.handleCursor(status)

        if status == QMediaPlayer.LoadingMedia:
            self.setStatusInfo("Loading...")
        elif status == QMediaPlayer.StalledMedia:
            self.setStatusInfo("Media Stalled")
        elif status == QMediaPlayer.EndOfMedia:
            QApplication.alert(self)
        elif status == QMediaPlayer.InvalidMedia:
            self.displayErrorMessage()
        else:
            self.setStatusInfo("")

    def handleCursor(self, status):
        if status in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.StalledMedia):
            self.setCursor(Qt.BusyCursor)
        else:
            self.unsetCursor()

    def bufferingProgress(self, progress):
        self.setStatusInfo("Buffering %d%" % progress)

    def videoAvailableChanged(self, available):
        if available:
            self.fullScreenButton.clicked.connect(
                self.videoWidget.setFullScreen)
            self.videoWidget.fullScreenChanged.connect(
                self.fullScreenButton.setChecked)

            if self.fullScreenButton.isChecked():
                self.videoWidget.setFullScreen(True)
        else:
            self.fullScreenButton.clicked.disconnect(
                self.videoWidget.setFullScreen)
            self.videoWidget.fullScreenChanged.disconnect(
                self.fullScreenButton.setChecked)

            self.videoWidget.setFullScreen(False)

        self.colorButton.setEnabled(available)

    def setTrackInfo(self, info):
        self.trackInfo = info

        if self.statusInfo != "":
            self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def setStatusInfo(self, info):
        self.statusInfo = info

        if self.statusInfo != "":
            self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def displayErrorMessage(self):
        self.setStatusInfo(self.player.errorString())

    def updateDurationInfo(self, currentInfo):
        duration = self.duration
        if currentInfo or duration:
            currentTime = QTime((currentInfo / 3600) % 60, (currentInfo / 60) % 60,
                                currentInfo % 60, (currentInfo * 1000) % 1000)
            totalTime = QTime((duration / 3600) % 60, (duration / 60) % 60,
                              duration % 60, (duration * 1000) % 1000);

            format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        else:
            tStr = ""


        self.labelDuration.setText(tStr)

        #ddd={(0, 36.400000000000006): " In just the past two months in the midst of enormous challenges this year, Our teams have remained focused and they haven't stopped Innovating were on an unbelievable pace of new product releases, delivering more new products this fall than ever before starting with upgrades to our powerful operating systems, as well as our other remarkable products, the incredibly capable and Affordable Apple Watch, SC, and Apple Watch Series 6 putting the future of Health on your wrist, an entirely new fitness experience with Apple\n", (36.400000000000006, 60.7): '  Fitness, plus a convenient way to subscribe to Apple services with Apple one, the new and more powerful 8th generation iPad and a stunning and versatile new iPad are the amazingly capable and compact homepod mini, and we began a new era for iPhone with iPhone 12 and for people who want the most out of their iPhone\n', (60.7, 62.5): '  The mack is stronger than ever\n', (62.5, 72.30000000000001): '  He continues to lead the industry in customer satisfaction as it has for over a decade and more customers than ever are choosing the Mac\n', (72.30000000000001, 80.70000000000002): '30% last quarter and the Mack is having its best year ever in the back continues to attract new users\n', (80.70000000000002, 88.90000000000002): '  Today, over 50% of buyers are new to the Mac, which is simply amazing and all around the world\n', (88.90000000000002, 96.60000000000001): ' People use the back to do remarkable things like the Mac itself, they challenge the status quo\n', (96.60000000000001, 110.30000000000003): " They make it, It's great to see how people use the Mac to do such amazing things\n", (110.30000000000003, 118.30000000000003): '  We announced that the Mac is taking another huge leap forward by transitioning to Apple silicon and we promised that the first Mac with app\n', (118.30000000000003, 124.2): " Our teams have been working tirelessly to deliver the best lineup of notebooks and desktops that we've ever had will\n", (124.2, 146.7): " We needed to develop a new set of Advanced Technologies so for the past several years we've had our teams working with this singular purpose of defining and building the next generation of Mac at the core of this effort is the Silicon we've been making Apple silicon for more than a decade, it's at the heart of iPhone, iPad and Apple Watch, And now we want to bring it to the Mac\n", (146.7, 165.10000000000002): " So the Mac can take a huge leap forward with Incredible performance, custom technology in Industry leading power efficiency of Apple silicon, and, as we said we're developing a family of chips we're going to transition the Mac line to these new Chips over the next couple of years will today\n", (165.10000000000002, 183.89999999999998): '  We are incredibly excited to announce our first step in this transition with our first chip designed specifically for the Mac and we call it and one and one has been optimized for most popular low power systems were small size and power efficiency are critically important\n', (183.89999999999998, 189.29999999999995): '  It is a stunningly capable chip and it ushers in a whole new era for the\n', (189.29999999999995, 195.10000000000002): "  Mac, now let's get started by spending a few minutes on a deep dive into this new chip with Johnny\n", (195.10000000000002, 203.3): ' I want is a brexel chip for the Mac and one was to deliver industry leading performance and features\n', (203.3, 217.5): 'Efficiency as a result and one delivers a giant leap in performance per watt and every Mac with M1 will be transformed into a completely different class of product system On chip or soc for the Mac\n', (217.5, 246.7): '  Technologies are combined into a single SOC, delivering a whole new level of efficiency, an amazing performance pictures of a unified memory architecture, or, um, a high bandwidth low latency memory into a single food within a custom package of the result, all of the Technologies in there so she can access the same data without cutting it between multiple pools of memory, improves performance and power efficiency\n', (246.7, 256.0): '  M1 is the first personal computer chip built using the interstate heating 5 nanometer process technology\n', (256.0, 268.70000000000005): "  The largest number of transistors we've ever put into a single chip, Someone has a mass of 16 billion transistors, and we use all of these transistors to give em one amazing performance and leading edge\n", (268.70000000000005, 291.5): '  Technologies and our goal is to make each of these Technologies best in class, the incredible performance of M1 start with the CPU, which features mm course high performance by efficiency or thread as efficiently as possible while maximizing performance in advancing it year after year and now with the huge improvements\n', (291.5, 299.5): " And I want when it comes to low power Silicon or a high performance car is the world's fastest\n"}
        for i in ddd.keys():
            if currentInfo >= i[1]:
                continue
            else:
                txt=str(ddd[(i[0], i[1])])
                self.labelHistogram.setText(txt)
                break




    def showColorDialog(self):
        if self.colorDialog is None:
            brightnessSlider = QSlider(Qt.Horizontal)
            brightnessSlider.setRange(-100, 100)
            brightnessSlider.setValue(self.videoWidget.brightness())
            brightnessSlider.sliderMoved.connect(
                self.videoWidget.setBrightness)
            self.videoWidget.brightnessChanged.connect(
                brightnessSlider.setValue)

            contrastSlider = QSlider(Qt.Horizontal)
            contrastSlider.setRange(-100, 100)
            contrastSlider.setValue(self.videoWidget.contrast())
            contrastSlider.sliderMoved.connect(self.videoWidget.setContrast)
            self.videoWidget.contrastChanged.connect(contrastSlider.setValue)

            hueSlider = QSlider(Qt.Horizontal)
            hueSlider.setRange(-100, 100)
            hueSlider.setValue(self.videoWidget.hue())
            hueSlider.sliderMoved.connect(self.videoWidget.setHue)
            self.videoWidget.hueChanged.connect(hueSlider.setValue)

            saturationSlider = QSlider(Qt.Horizontal)
            saturationSlider.setRange(-100, 100)
            saturationSlider.setValue(self.videoWidget.saturation())
            saturationSlider.sliderMoved.connect(
                self.videoWidget.setSaturation)
            self.videoWidget.saturationChanged.connect(
                saturationSlider.setValue)

            layout = QFormLayout()
            layout.addRow("Brightness", brightnessSlider)
            layout.addRow("Contrast", contrastSlider)
            layout.addRow("Hue", hueSlider)
            layout.addRow("Saturation", saturationSlider)

            button = QPushButton("Close")
            layout.addRow(button)

            self.colorDialog = QDialog(self)
            self.colorDialog.setWindowTitle("Color Options")
            self.colorDialog.setLayout(layout)

            button.clicked.connect(self.colorDialog.close)

        self.colorDialog.show()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    player = Player(sys.argv[1:])
    player.show()

    sys.exit(app.exec_())
