import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

import ui

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    # ui = test.Ui_MainWindow()
    ui = ui.Player()
    ui.avplayer.set_video_path("../project/dataset/Ads/Starbucks_Ad_15s.rgb")
    ui.avplayer.set_audio_path("../project/dataset/Ads/Starbucks_Ad_15s.wav")
    ui.avplayer.set_video_path("../project/dataset/Videos/data_test1.rgb")
    ui.avplayer.set_audio_path("../project/dataset/Videos/data_test1.wav")
    ui.avplayer.set_video_path("result.rgb")
    ui.avplayer.set_audio_path("result.wav")

    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())