from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import pygame

import time
import threading
import wave
import os


# focus on decode audio and video
# TODO: may beuse mutex to protect shared variable

class AvPlayer():
    def __init__(self):

        # file information
        self.video_path = None
        self.audio_path = None

        # video/audio information
        self.width = None
        self.height = None
        self.channel = None
        self.num_frame = None
        self.frame_size = None

        # player status
        self.is_playing = False
        self.is_stop = True
        self.video_time = None

        self.video = None
        pygame.mixer.init(frequency=48000, size=-16, channels=1, buffer=1024)

        # other
        self.video_display_handle = None

    def set_video_path(self, video_path):
        self.video_path = video_path

    def set_audio_path(self, audio_path):
        self.audio_path = audio_path

    def open_file(self):
        # set up video paramters
        self.width = 480
        self.height = 270
        self.channel = 3
        self.frame_rate = 30
        # self.video_length = 15
        # self.num_frame = 450
        # self.num_frame = self.video_length * self.frame_rate
        self.num_frame = int(os.path.getsize(
            self.video_path) / (self.width * self.height * 3))
        self.frame_size = self.height * self.width * self.channel

        # load video into memory
        self.video = np.zeros(
            (self.num_frame, self.frame_size), dtype=np.uint8)
        with open(self.video_path, "rb") as f:
            for i in range(self.num_frame):
                buffer = f.read(self.frame_size)
                frame = np.frombuffer(buffer, dtype=np.uint8)
                frame = frame.reshape((self.channel, -1))
                frame = frame.transpose()
                self.video[i] = frame.reshape(1, -1)

        # load audio into memory
        pygame.mixer.music.load(self.audio_path)

    def set_video_display_handle(self, handle):
        self.video_display_handle = handle

    def onPlay(self):

        # def audio_time_to_video_time(audio_time, fps):
        #     return int((audio_time + 16)*fps/1000)

        # playing loop
        self.video_time = 0
        while not self.is_stop and self.video_time < self.num_frame:
            if self.is_playing:
                self.video_time = int(
                    (pygame.mixer.music.get_pos() - 3) * self.frame_rate / 1000)
                self.draw(self.video_time)
            time.sleep(1 / self.frame_rate / 4)

        # finish playing
        self.is_playing = False
        self.is_stop = True
        pygame.mixer.music.stop()

    def onPlayAudio(self):
        pygame.mixer.music.play()

    def play(self):
        if self.is_stop:
            self.open_file()
            print("finish loading file")

            self.is_playing = True
            self.is_stop = False

            t = threading.Thread(target=self.onPlay)
            t.start()
            t1 = threading.Thread(target=self.onPlayAudio)
            t1.start()

    def draw(self, index):
        if index < self.video.shape[0]:
            image = QtGui.QImage(
                self.video[index].data, self.width, self.height, QtGui.QImage.Format_RGB888)
            pixemap = QtGui.QPixmap.fromImage(image)
            self.video_display_handle.setPixmap(pixemap)
            self.video_display_handle.setGeometry(
                QtCore.QRect(160, 70, 480, 270))

            QtWidgets.QApplication.processEvents()

    def pause(self):
        if not self.is_stop:
            self.is_playing = False
            pygame.mixer.music.pause()

    def resume(self):
        if not self.is_stop:
            self.is_playing = True
            pygame.mixer.music.unpause()

    def stop(self):
        self.is_playing = False
        self.is_stop = True
        self.video_time = 0
        self.draw(self.video_time)
        pygame.mixer.music.stop()
    
    def get_pos(self):
        return self.video_time/ self.num_frame


if __name__ == "__main__":
    p = AvPlayer()
