import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QListWidget, QSlider, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import pygame
import time
from mutagen.mp3 import MP3


class MP3Player(QMainWindow):
    def __init__(self):
        super(MP3Player, self).__init__()
        pygame.mixer.init()
        uic.loadUi("music_player.ui", self)

        self.stopped = False
        self.paused = False

        self.song_box = self.findChild(QListWidget, "listWidget")

        self.back_button = self.findChild(QPushButton, "back_button")
        self.back_button.clicked.connect(self.previous_song)

        self.forward_button = self.findChild(QPushButton, "forward_button")
        self.forward_button.clicked.connect(self.next_song)

        self.play_button = self.findChild(QPushButton, "play_button")
        self.play_button.clicked.connect(self.play)

        self.pause_button = self.findChild(QPushButton, "pause_button")
        self.pause_button.clicked.connect(self.pause)

        self.stop_button = self.findChild(QPushButton, "stop_button")
        self.stop_button.clicked.connect(self.stop)

        self.volume_meter = self.findChild(QLabel, "volume_meter")

        self.timeSlider = self.findChild(QSlider, "timeSlider")
        self.timeSlider.sliderMoved.connect(self.slide)

        self.volume_slider = self.findChild(QSlider, "volumeSlider")
        self.volume_slider.sliderMoved.connect(self.volume)

        self.labelTimer = self.findChild(QLabel, "labelTimer")

        self.actionAddOneSong.triggered.connect(self.add_songs)
        self.actionAddManySongs.triggered.connect(self.add_many_songs)
        self.actionDeleteASong.triggered.connect(self.delete_song)
        self.actionDeleteAllSongs.triggered.connect(self.delete_all_songs)

    def play_time(self):
        if self.stopped:
            return
        current_time = pygame.mixer.music.get_pos() / 1000
        converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
        song = self.song_box.currentItem().text()
        song = f'D:/pyprojects/music_player/music/{song}.mp3'
        song_mut = MP3(song)
        global song_length
        song_length = song_mut.info.length
        # Convert to Time Format
        converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
        self.labelTimer.setText(f'{converted_current_time} / {converted_song_length}')
        self.timeSlider.setValue(int(current_time))

        if int(self.timeSlider.value()) == int(self.timeSlider.maximum()):
            self.next_song()

        if self.stopped:
            return

        if self.paused:
            return

        if current_time >= song_length:
            self.next_song()

        QTimer().singleShot(1000, self.play_time)

    def play(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            song = self.song_box.currentItem().text()
            song = f'D:/pyprojects/music_player/music/{song}.mp3'
            pygame.mixer.music.load(song)
            pygame.mixer.music.play()

        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        song = self.song_box.currentItem().text()
        song = f'D:/pyprojects/music_player/music/{song}.mp3'
        song_mut = MP3(song)
        song_length = song_mut.info.length
        converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

        self.labelTimer.setText(f'00:00 / {converted_song_length}')
        self.timeSlider.setMaximum(int(song_length))
        self.timeSlider.setValue(0)

        self.play_time()

    def pause(self):
        pygame.mixer.music.pause()
        self.paused = True

        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop(self):
        pygame.mixer.music.stop()
        self.stopped = True

        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.labelTimer.setText('00:00 / 00:00')

    def previous_song(self):
        current_row = self.song_box.currentRow()
        if current_row > 0:
            self.song_box.setCurrentRow(current_row - 1)
            self.play()

    def next_song(self):
        current_row = self.song_box.currentRow()
        if current_row < self.song_box.count() - 1:
            self.song_box.setCurrentRow(current_row + 1)
            self.play()

    def add_songs(self):
        songs = QFileDialog.getOpenFileNames(self, 'Choose Songs', 'D:/pyprojects/music_player/music/', 'Audio Files (*.mp3)')[0]
        for song in songs:
            song = song.split('/')[-1].split('.')[0]
            self.song_box.addItem(song)

    def add_many_songs(self):
        songs = QFileDialog.getOpenFileNames(self, 'Choose Songs', 'D:/pyprojects/music_player/music/', 'Audio Files (*.mp3)')[0]

        for song in songs:
            song = song.replace("D:/pyprojects/music_player/music/", "")
            song = song.replace(".mp3", "")
            # Insert into playlist
            self.song_box.addItem(song)

    def slide(self):
        song = self.song_box.currentItem().text()
        song = f'D:/pyprojects/music_player/music/{song}.mp3'
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(start=int(self.timeSlider.value()))

    def volume(self):
        volume = self.volume_slider.value()
        pygame.mixer.music.set_volume(volume / 100)
        if volume == 0:
            self.volume_meter.setPixmap(QPixmap('images/volume0.png'))
        elif 0 < volume <= 30:
            self.volume_meter.setPixmap(QPixmap('images/volume1.png'))
        elif 30 < volume <= 70:
            self.volume_meter.setPixmap(QPixmap('images/volume2.png'))
        else:
            self.volume_meter.setPixmap(QPixmap('images/volume3.png'))

    def delete_song(self):
        self.stop()
        current_row = self.song_box.currentRow()
        if current_row >= 0:
            self.song_box.takeItem(current_row)
        # Stop Music if it's playing
        pygame.mixer.music.stop()

    # Delete All Songs from Playlist
    def delete_all_songs(self):
        self.stop()
        # Delete All Songs
        self.song_box.clear()
        # Stop Music if it's playing
        pygame.mixer.music.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MP3Player()
    player.show()
    sys.exit(app.exec_())
