from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import wave

import test

import avplayer

base = "./dataset/Ads/Starbucks_Ad_15s"
base = "./dataset/Videos/data_test1"
base = "./dataset/Ads/Subway_Ad_15s"

rgb_file = base + ".rgb"
wav_file = base + ".wav"

# focus on ui and control


class Player(test.Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.avplayer = avplayer.AvPlayer()
        self.avplayer.set_video_path(rgb_file)
        self.avplayer.set_audio_path(wav_file)

        self.timer = None

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.pushButton.clicked.connect(self.play_pause_resume)
        # self.pushButton_2.clicked.connect(self.play_pause)
        self.pushButton_3.clicked.connect(self.stop)

        self.avplayer.set_video_display_handle(self.label_imageDisplay)
        # self.avplayer.set_application_handle(self.frame)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)
    
    def play_pause_resume(self):
        if self.avplayer.is_stop:
           self.play()
           self.pushButton.setText("pause")
        else:
            self.pause_resume() 

    def play(self):
        self.avplayer.play()
        self.timer.start()
        # TODO: update pushbutton label after finishing playing

    # TODO: use paramter to set label, instead instance variable
    def pause_resume(self):
        if self.avplayer.is_playing:
            self.avplayer.pause()
            self.pushButton.setText("play")
            self.timer.stop()
        else:
            self.avplayer.resume()
            self.pushButton.setText("pause")
            self.timer.start()

    def stop(self):
        self.avplayer.stop()
        self.pushButton.setText("play")
        self.horizontalSlider.setValue(0)
    
    def update_ui(self):
        media_pos = int(self.avplayer.get_pos()*100)
        self.horizontalSlider.setValue(media_pos)

        # No need to call this function if nothing is played
        if self.avplayer.is_stop:
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.avplayer.is_playing:
                self.stop()
