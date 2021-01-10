"""
************************************************************************************************************************
------------------------------------------------------------------------------------------------------------------------
PyMusX v2.4.3 (8/1/2021)
Original Revision (4/7/20)
Thanks to: Olivier Aubert, John Elder, np1, blackjack4494, Steve Adi Pratama

PyMusX is licensed under:

MIT License

Copyright (c) 2020 Kevin Putra Satrianto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
------------------------------------------------------------------------------------------------------------------------
************************************************************************************************************************
"""

import sys
import datetime

write_to_log = True

if write_to_log:
    sys.stderr = open('pmx.log', 'w')  # log the error messages from console to "pmx.log"
    sys.stdout = open('pmx.log', 'w')  # log the output from console to "pmx.log"
    print("==================== System Info ====================")
    print(sys.version_info)
    print(sys.version)
    print("PyMusX v2.4.3 (8/1/2021)")

    print("==================== Logs Started ====================")

    print("Application starts at: " + str(datetime.datetime.now()))
else:
    pass

# import all necessary modules
from PySide2 import QtWidgets, QtGui, QtCore, QtWinExtras
from PySide2.QtCore import Qt, QTimer, QSize
from PySide2.QtGui import QIcon, QPalette, QColor, QPixmap, QFont
from PySide2.QtWidgets import QMessageBox, QMainWindow, QApplication, QWidget, QDesktopWidget, QDialog
from tkinter import filedialog, messagebox, Tk
from configparser import ConfigParser
import vlc
import os
import time
import pafy

config = ConfigParser()  # config parser instance for app configurations
langconf = ConfigParser()  # config parser instance for language configurations

config.read('configs/config.ini', encoding='utf-8')  # load configuration file

lang = config.get('ui', 'lang')

if lang == "en":
    langconf.read('configs/lang/en.ini', encoding='utf-8')
elif lang == "id":
    langconf.read('configs/lang/id.ini', encoding='utf-8')
elif lang == "de":
    langconf.read('configs/lang/de.ini', encoding='utf-8')


def error_popup():  # error popup
    root = Tk()
    root.withdraw()
    warn = messagebox.showerror("Failed to launch PyMusX: Missing config file",
                                r"Could not find configuration file (PyMusX\configs\config.ini)")
    sys.exit()

print("checking config file")
if not os.path.isfile('configs/config.ini'):  # if config.pmx is not present, then show popup
    print("config file (config.ini) not found")
    error_popup()
else:
    print("config file successfully loaded")



class dockedWindow(QWidget):  # docked window class
    def __init__(self):
        print("initializing docked window")
        super(dockedWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("PyMusX (Docked)")
        self.setFixedWidth(250)
        self.setFixedHeight(150)
        self.setWindowPositionRight()
        self.setWindowIcon(QIcon('Icon/main_logo.png'))
        self.initDockedWindow()

    def setWindowPositionRight(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().right()
        qr.moveRight(cp)
        self.move(qr.bottomLeft())

    def initDockedWindow(self):
        self.expandWindow_btn = QtWidgets.QPushButton(self)
        self.expandWindow_btn.setGeometry(2, 118, 30, 30)
        self.expandWindow_btn.setIcon(QIcon('Icon/expand.png'))
        self.expandWindow_btn.setToolTip(langconf.get('docked', 'expand'))

        self.docked_song_title = QtWidgets.QTextBrowser(self)
        self.docked_song_title.setGeometry(15, 10, 225, 34)
        self.docked_song_title.setHtml('<p align="center" style="'
                                       ' margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;'
                                       '-qt-block-indent:0; text-indent:0px;">Nothing (No Track '
                                       'Selected)</p></body></html>')

        self.docked_seekbar = QtWidgets.QSlider(Qt.Horizontal, self)
        self.docked_seekbar.setGeometry(35, 45, 185, 25)
        self.docked_seekbar.setToolTip(langconf.get('main_window', 'seek_tooltip'))
        self.docked_seekbar.setMaximum(0)
        self.docked_seekbar.setMinimum(0)

        self.docked_browse = QtWidgets.QPushButton(self)
        self.docked_browse.setIcon(QIcon('Icon/play.png'))
        self.docked_browse.setGeometry(100, 70, 50, 50)
        self.docked_browse.setToolTip(langconf.get('main_window', 'play_tooltip'))

        self.docked_stop_btn = QtWidgets.QPushButton(self)
        self.docked_stop_btn.setIcon(QIcon('Icon/stop.png'))
        self.docked_stop_btn.setGeometry(155, 90, 30, 30)
        self.docked_stop_btn.setToolTip(langconf.get('main_window', 'stop_tooltip'))

        self.docked_pause_btn = QtWidgets.QPushButton(self)
        self.docked_pause_btn.setIcon(QIcon('Icon/pause.png'))
        self.docked_pause_btn.setGeometry(65, 90, 30, 30)
        self.docked_pause_btn.setToolTip(langconf.get('main_window', 'pause_tooltip'))

        self.docked_eq_btn = QtWidgets.QPushButton(self)
        self.docked_eq_btn.setGeometry(218, 118, 30, 30)
        self.docked_eq_btn.setIcon(QIcon('Icon/eq.png'))
        self.docked_eq_btn.setToolTip(langconf.get('main_window', 'eq_tooltip'))

        self.docked_volume_slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.docked_volume_slider.setGeometry(80, 125, 95, 25)
        self.docked_volume_slider.setMinimum(0)
        self.docked_volume_slider.setToolTip(langconf.get('main_window', 'volume_tooltip'))
        self.docked_volume_slider.setMaximum(100)
        self.docked_volume_slider.setValue(config.getint('audio', 'master_volume'))


class StreamWindow(QDialog):  # Stream Window class
    def __init__(self):
        print("initializing pystreamer window")
        super(StreamWindow, self).__init__()
        self.move(400, 100)
        self.setWindowIcon(QIcon('Icon/main_logo.png'))
        self.setWindowTitle("PyStreamer")  # set window title
        self.setFixedHeight(220)  # set the fixed height of the window
        self.setFixedWidth(300)  # set the fixed width of the window
        self.initStreamWindow()  # execute all widgets inside initStreamWindow()
        self.song = ""
        self.setWindowFlags(Qt.WindowCloseButtonHint)  # this line will disable the help button which enabled by default

    def closeEvent(self, a0: QtGui.QCloseEvent):
        a0.ignore()  # if the x button pressed, do not close the window
        self.hide()  # hide it instead

    def initStreamWindow(self):
        self.startStream = QtWidgets.QPushButton(self)  # start stream button
        self.startStream.setGeometry(215, 190, 80, 25)
        self.startStream.setText(langconf.get('pystreamer', 'start_btn'))

        self.link_lbl = QtWidgets.QLabel(self)
        self.link_lbl.setText(langconf.get('pystreamer', 'link_lbl'))
        self.link_lbl.move(5, 5)

        self.link = QtWidgets.QLineEdit(self)  # this is where you put the yt link in
        self.link.setGeometry(5, 20, 150, 25)

        self.process_btn = QtWidgets.QPushButton(self)  # process link button
        self.process_btn.setText(langconf.get('pystreamer', 'process_btn'))
        self.process_btn.setGeometry(155, 20, 65, 25)
        self.process_btn.clicked.connect(self.processLink)  # if pressed, execute all code in processLink()

        self.title_lbl = QtWidgets.QLabel(self)  # shows what the streamed song's title
        self.title_lbl.setText(langconf.get('pystreamer', 'title_lbl'))
        self.title_lbl.move(5, 55)
        self.title = QtWidgets.QLineEdit(self)
        self.title.setText("")
        self.title.setGeometry(5, 75, 200, 25)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setReadOnly(True)

        self.duration_lbl = QtWidgets.QLabel(self)  # shows the streamed song's total duration
        self.duration_lbl.setText(langconf.get('pystreamer', 'duration_lbl'))
        self.duration_lbl.move(5, 105)
        self.duration = QtWidgets.QLineEdit(self)
        self.duration.setText("")
        self.duration.setGeometry(5, 125, 200, 25)
        self.duration.setAlignment(Qt.AlignCenter)
        self.duration.setReadOnly(True)

        self.author_lbl = QtWidgets.QLabel(self)  # shows the channel
        self.author_lbl.setText(langconf.get('pystreamer', 'auth_lbl'))
        self.author_lbl.move(5, 155)
        self.author = QtWidgets.QLineEdit(self)
        self.author.setText("")
        self.author.setGeometry(5, 175, 200, 25)
        self.author.setAlignment(Qt.AlignCenter)
        self.author.setReadOnly(True)

    def processLink(self):  # process the link (if exist)
        if self.link.text() == "":  # if the link field is empty then show popup
            warn = QMessageBox(self)
            warn.setWindowTitle("Stream Failed")
            warn.setText(langconf.get('pystreamer', 'empty_link_warn'))
            warn.setIcon(QMessageBox.Warning)
            warn.exec_()
        else:
            self.song_url = pafy.new(self.link.text())  # declare the variable "song_url" to contain the song's yt url
            self.title.setText(self.song_url.title)  # display the song's title in Stream Window
            self.duration.setText(self.song_url.duration)  # display the song's duration in Stream Window
            self.author.setText(self.song_url.author)  # display the song's channel in Stream Window
            self.song = self.song_url.getbestaudio()  # get the best audio quality to stream


class ModuleListWindow(QDialog):
    def __init__(self):
        print("initializing module list window")
        super(ModuleListWindow, self).__init__()
        self.initModule()
        self.move(500, 100)
        self.setFixedHeight(300)
        self.setFixedWidth(250)
        self.setWindowTitle("Modules")
        self.setWindowIcon(QIcon('Icon/main_logo.png'))
        self.setWindowFlags(Qt.WindowCloseButtonHint)  # this line will disable the help button which enabled by default

    def closeEvent(self, a0: QtGui.QCloseEvent):
        a0.ignore()
        self.hide()

    def initModule(self):
        self.title = QtWidgets.QLabel(self)
        self.title.setText("Modules Used by PyMusX")
        self.title.move(25, 5)
        self.title.setFont(QFont('Arial', 13))

        self.pysd_lbl = QtWidgets.QLabel(self)
        self.pysd_lbl.move(10, 50)
        self.pysd_lbl.setToolTip("PyMusX use PySide2 as its main"
                                 "\nGraphical User Interface.")
        self.pysd_lbl.setOpenExternalLinks(True)
        self.pysd_lbl.setText("<a href=\"https://wiki.qt.io/Qt_for_Python\">PySide2</a>")
        self.pysd_description = QtWidgets.QLabel(self)
        self.pysd_description.move(10, 65)
        self.pysd_description.setText("© The QT Company (LGPL)")

        self.pyvlc_lbl = QtWidgets.QLabel(self)
        self.pyvlc_lbl.move(10, 90)
        self.pyvlc_lbl.setToolTip("PyMusx use Python-VLC to access"
                                  "\nVideoLAN's media engine (LibVLC) with Python,"
                                  "\nEssentialy, a Python binding for LibVLC.")
        self.pyvlc_lbl.setOpenExternalLinks(True)
        self.pyvlc_lbl.setText("<a href=\"http://www.github.com/oaubert/python-vlc\">Python-VLC</a>")
        self.pyvlc_description = QtWidgets.QLabel(self)
        self.pyvlc_description.move(10, 105)
        self.pyvlc_description.setText("© Olivier Aubert (GNU GPLv2)")

        self.libvlc_lbl = QtWidgets.QLabel(self)
        self.libvlc_lbl.move(10, 130)
        self.libvlc_lbl.setToolTip("PyMusX use LibVLC to handle"
                                   "\naudio playback and processing.")
        self.libvlc_lbl.setOpenExternalLinks(True)
        self.libvlc_lbl.setText("<a href=\"http://www.videolan.org/vlc/libvlc.html\">LibVLC</a>")
        self.libvlc_description = QtWidgets.QLabel(self)
        self.libvlc_description.move(10, 145)
        self.libvlc_description.setText("© VideoLAN (GNU GPLv2)")

        self.tk_lbl = QtWidgets.QLabel(self)
        self.tk_lbl.move(10, 170)
        self.tk_lbl.setToolTip("PyMusX use tkinter for"
                               "\nminor gui feature, such as file dialog"
                               "\nor popup.")
        self.tk_lbl.setOpenExternalLinks(True)
        self.tk_lbl.setText("<a href=\"http://www.python.org\">Tkinter</a>")
        self.tk_description = QtWidgets.QLabel(self)
        self.tk_description.move(10, 185)
        self.tk_description.setText("© Python (GNU GPL)")

        self.pfy_lbl = QtWidgets.QLabel(self)
        self.pfy_lbl.move(10, 210)
        self.pfy_lbl.setToolTip("Used to retrieve metadata from youtube-dl.")
        self.pfy_lbl.setOpenExternalLinks(True)
        self.pfy_lbl.setText("<a href=\"https://pythonhosted.org/pafy/\">Pafy</a>")
        self.pfy_description = QtWidgets.QLabel(self)
        self.pfy_description.move(10, 225)
        self.pfy_description.setText("© np1, (GitHub Open Source)")

        self.yt_lbl = QtWidgets.QLabel(self)
        self.yt_lbl.move(10, 250)
        self.yt_lbl.setToolTip("Used for downloading data from youtube.")
        self.yt_lbl.setOpenExternalLinks(True)
        self.yt_lbl.setText("<a href=\"https://github.com/blackjack4494/yt-dlc\">Youtube-dlc</a>")
        self.yt_description = QtWidgets.QLabel(self)
        self.yt_description.move(10, 265)
        self.yt_description.setText("© blackjack4494, (GitHub Open Source)")


# settings window
class SettingsWindow(QDialog):
    def __init__(self):
        print("initializing settings window")
        super(SettingsWindow, self).__init__()
        self.initSettingsUI()
        self.setWindowTitle(langconf.get('settings', 'window_name'))
        self.setWindowIcon(QIcon("Icon/main_logo.png"))
        self.move(750, 100)
        self.setFixedHeight(160)
        self.setFixedWidth(250)
        self.module_win = ModuleListWindow()
        self.setWindowFlags(Qt.WindowCloseButtonHint)  # this line will disable the help button which enabled by default

    def closeEvent(self, a0: QtGui.QCloseEvent):
        a0.ignore()
        self.hide()

    def initSettingsUI(self):
        self.blur = QtWidgets.QGraphicsBlurEffect()

        self.opacityframe = QtWidgets.QFrame(self)
        self.opacityframe.setGeometry(QtCore.QRect(2, 2, 110, 42))
        self.opacityframe.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.opacity_lbl = QtWidgets.QLabel(self)
        self.opacity_lbl.setText(langconf.get('settings', 'win_opacity'))
        self.opacity_lbl.move(5, 2)

        self.opacity_lbl_val = QtWidgets.QLabel(self)
        self.opacity_lbl_val.setText("100")
        self.opacity_lbl_val.setGeometry(5, 25, 30, 20)

        self.opacity_sld = QtWidgets.QSlider(Qt.Horizontal, self)
        self.opacity_sld.setGeometry(5, 15, 100, 15)
        self.opacity_sld.setValue(100)
        self.opacity_sld.setMinimum(50)
        self.opacity_sld.setMaximum(100)

        self.transtoggleframe = QtWidgets.QFrame(self)
        self.transtoggleframe.setGeometry(QtCore.QRect(2, 46, 110, 42))
        self.transtoggleframe.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.translucent_toggle = QtWidgets.QCheckBox(self)
        self.translucent_toggle.clicked.connect(self.setTranslucent)
        self.translucent_toggle.setText(langconf.get('settings', 'trans'))
        self.translucent_toggle.setToolTip(langconf.get('settings', 'trans_tooltip'))
        self.translucent_toggle.move(5, 58)

        self.info = QtWidgets.QPushButton(self)
        self.info.setGeometry(215, 125, 35, 35)
        self.info.setIcon(QIcon('Icon/info.png'))
        self.info.setToolTip("Info")
        self.info.clicked.connect(self.open_about)

        self.sys_aud = QtWidgets.QPushButton(self)
        self.sys_aud.setGeometry(175, 125, 35, 35)
        self.sys_aud.clicked.connect(self.open_audctrl)
        self.sys_aud.setToolTip(langconf.get('settings', 'sys_aud'))

        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText(langconf.get('settings', 'theme_lbl'))
        self.lbl.setGeometry(5, 85, 200, 25)

        self.themeframe = QtWidgets.QFrame(self)
        self.themeframe.setGeometry(QtCore.QRect(2, 90, 110, 68))
        self.themeframe.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.dark_btn = QtWidgets.QCheckBox(self)
        self.dark_btn.setText(langconf.get('settings', 'thm_dark'))
        self.dark_btn.setGeometry(5, 105, 80, 30)
        self.dark_btn.clicked.connect(self.set_dark)

        self.light_btn = QtWidgets.QCheckBox(self)
        self.light_btn.setText(langconf.get('settings', 'thm_light'))
        self.light_btn.setGeometry(5, 130, 80, 30)
        self.light_btn.clicked.connect(self.set_light)

        self.timerframe = QtWidgets.QFrame(self)
        self.timerframe.setGeometry(QtCore.QRect(120, 2, 125, 68))
        self.timerframe.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.timerLabel = QtWidgets.QLabel(self)
        self.timerLabel.setText(langconf.get('settings', 'timer_lbl'))
        self.timerLabel.move(123, 2)
        self.timerLabel.setToolTip("Limit the song playback time")

        self.timerToggle = QtWidgets.QCheckBox(self)
        self.timerToggle.setText(langconf.get('settings', 'timer_check'))
        self.timerToggle.move(123, 22)
        self.timerToggle.stateChanged.connect(self.setTimerBool)

        self.timerInput = QtWidgets.QLineEdit(self)
        self.timerInput.setText(str(config.getint('trackTimer', 'duration')))
        self.timerInput.setGeometry(123, 42, 100, 25)
        self.timerInput.textChanged.connect(self.writeValue)
        self.timerInput.setGraphicsEffect(self.blur)

        self.lang_selectorframe = QtWidgets.QFrame(self)
        self.lang_selectorframe.setGeometry(QtCore.QRect(120, 75, 125, 45))
        self.lang_selectorframe.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.lang_selector_lbl = QtWidgets.QLabel(self)
        self.lang_selector_lbl.setText(langconf.get('settings', 'language_lbl'))
        self.lang_selector_lbl.move(123, 75)

        lang_list = ["English", "Indonesia", "Deutsche"]
        self.lang_selector = QtWidgets.QComboBox(self)
        self.lang_selector.setGeometry(123, 92, 100, 25)
        self.lang_selector.addItems(lang_list)
        self.lang_selector.setToolTip(langconf.get('settings', 'language_selector_tooltip'))
        self.lang_selector.currentTextChanged.connect(self.change_lang)

        if config.get('ui', 'lang') == "en":
            self.lang_selector.setCurrentText("English")

        elif config.get('ui', 'lang') == "id":
            self.lang_selector.setCurrentText("Indonesia")

        elif config.get('ui', 'lang') == "de":
            self.lang_selector.setCurrentText("Deutsche")

        if config.getboolean('ui', 'translucent'):
            self.translucent_toggle.setChecked(True)
        else:
            self.translucent_toggle.setChecked(False)

        if config.getboolean('theme', 'dark'):
            self.light_btn.setChecked(False)
            self.dark_btn.setChecked(True)
        else:
            self.light_btn.setChecked(True)
            self.dark_btn.setChecked(False)

        if config.getboolean('trackTimer', 'on'):
            self.timerToggle.setChecked(True)
            self.timerInput.setDisabled(False)
            self.blur.setBlurRadius(0)
        else:
            self.timerToggle.setChecked(False)
            self.timerInput.setDisabled(True)
            self.blur.setBlurRadius(2)

    def change_lang(self):
        if self.lang_selector.currentText() == "English":
            config.set('ui', 'lang', 'en')
        elif self.lang_selector.currentText() == "Indonesia":
            config.set('ui', 'lang', 'id')
        elif self.lang_selector.currentText() == "Deutsche":
            config.set('ui', 'lang', 'de')


        with open('configs/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)


    def setTranslucent(self):
        if self.translucent_toggle.isChecked():
            config.set('ui', 'translucent', 'True')
        elif not self.translucent_toggle.isChecked():
            config.set('ui', 'translucent', 'False')

        with open('configs/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def writeValue(self):
        config.set('trackTimer', 'duration', self.timerInput.text())

    def setTimerBool(self):
        if self.timerToggle.isChecked():
            self.timerInput.setDisabled(False)
            self.blur.setBlurRadius(0)

            config.set('trackTimer', 'on', 'True')
        elif not self.timerToggle.isChecked():
            self.timerInput.setDisabled(True)
            self.blur.setBlurRadius(2)

            config.set('trackTimer', 'on', 'False')
        with open('configs/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def open_mdl_list(self):
        abt.close()
        self.module_win.show()

    def set_dark(self):
        config.set('theme', 'dark', 'True')
        with open('configs/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        self.light_btn.setChecked(False)
        change_theme()

    def set_light(self):
        config.set('theme', 'dark', 'False')
        with open('configs/config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        self.dark_btn.setChecked(False)
        change_theme()

    def open_audctrl(self):
        os.system('control.exe mmsys.cpl')

    def open_about(self):
        global abt
        ver = open('configs/version.txt', 'r')
        bld_date = open('configs/dateofbuild.txt', 'r')
        version = ver.read()
        build = bld_date.read()
        abt = QtWidgets.QMessageBox(self)
        abt.setWindowTitle("About")
        abt.setIcon(QMessageBox.Information)
        abt.move(500, 250)
        module_lst_btn = QtWidgets.QPushButton(abt)
        module_lst_btn.setGeometry(150, 67, 100, 25)
        module_lst_btn.clicked.connect(self.open_mdl_list)
        module_lst_btn.setText("External Modules")
        module_lst_btn.setToolTip("Open External Modules list")
        abt.setText("Version: PyMusX v" + str(version) + " by Kevin Putra (a.k.a Negated)"
                                                         "\nPython Version: Python 3.8.5"
                                                         "\nDate of Build: " + str(build) + " (GMT+7)")

        abt.exec_()


# equalizer window
class eq_win(QDialog):
    def __init__(self):
        print("initializing equalizer window")
        super(eq_win, self).__init__()
        self.initEQ()
        self.setWindowTitle("PyEQ")
        self.setWindowIcon(QIcon("Icon/main_logo.png"))
        self.move(100, 400)
        self.setFixedHeight(180)
        self.setFixedWidth(500)
        self.setWindowFlags(Qt.WindowCloseButtonHint)  # this line will disable the help button which enabled by default

    def closeEvent(self, a0: QtGui.QCloseEvent):
        a0.ignore()
        self.hide()

    def initEQ(self):
        self.reset_eq_btn = QtWidgets.QPushButton(self)
        self.reset_eq_btn.setGeometry(430, 155, 70, 25)
        self.reset_eq_btn.setText("Reset")
        self.reset_eq_btn.clicked.connect(self.reset_eq)

        self.pre = QtWidgets.QSlider(self)
        self.pre.setGeometry(5, 5, 15, 150)
        self.pre.setMaximum(20)
        self.pre.setValue(config.getint('audio', 'preamp'))
        self.pre_lbl = QtWidgets.QLabel(self)
        self.pre_lbl.setGeometry(20, 60, 25, 150)
        self.pre_lbl.setText(str(self.pre.value()) + "dB")
        self.pre_freq_lbl = QtWidgets.QLabel(self)
        self.pre_freq_lbl.setText("Pre")
        self.pre_freq_lbl.setGeometry(20, -60, 25, 150)

        self.freq31 = QtWidgets.QSlider(self)
        self.freq31.setGeometry(50, 5, 15, 150)
        self.freq31.setMaximum(20)
        self.freq31.setMinimum(-20)
        self.freq31.setValue(config.getint('audio', '31hz'))
        self.freq31_lbl = QtWidgets.QLabel(self)
        self.freq31_lbl.setGeometry(65, 60, 30, 150)
        self.freq31_lbl.setText(str(self.freq31.value()) + "dB")
        self.freq31_freq_lbl = QtWidgets.QLabel(self)
        self.freq31_freq_lbl.setText("31hz")
        self.freq31_freq_lbl.setGeometry(65, -60, 25, 150)

        self.freq62 = QtWidgets.QSlider(self)
        self.freq62.setGeometry(95, 5, 15, 150)
        self.freq62.setMaximum(20)
        self.freq62.setMinimum(-20)
        self.freq62.setValue(config.getint('audio', '62hz'))
        self.freq62_lbl = QtWidgets.QLabel(self)
        self.freq62_lbl.setGeometry(110, 60, 30, 150)
        self.freq62_lbl.setText(str(self.freq62.value()) + "dB")
        self.freq62_freq_lbl = QtWidgets.QLabel(self)
        self.freq62_freq_lbl.setText("62hz")
        self.freq62_freq_lbl.setGeometry(110, -60, 25, 150)

        self.freq125 = QtWidgets.QSlider(self)
        self.freq125.setGeometry(140, 5, 15, 150)
        self.freq125.setMaximum(20)
        self.freq125.setMinimum(-20)
        self.freq125.setValue(config.getint('audio', '125hz'))
        self.freq125_lbl = QtWidgets.QLabel(self)
        self.freq125_lbl.setGeometry(155, 60, 30, 150)
        self.freq125_lbl.setText(str(self.freq125.value()) + "dB")
        self.freq125_freq_lbl = QtWidgets.QLabel(self)
        self.freq125_freq_lbl.setText("125hz")
        self.freq125_freq_lbl.setGeometry(155, -60, 30, 150)

        self.freq250 = QtWidgets.QSlider(self)
        self.freq250.setGeometry(185, 5, 15, 150)
        self.freq250.setMaximum(20)
        self.freq250.setMinimum(-20)
        self.freq250.setValue(config.getint('audio', '250hz'))
        self.freq250_lbl = QtWidgets.QLabel(self)
        self.freq250_lbl.setGeometry(200, 60, 30, 150)
        self.freq250_lbl.setText(str(self.freq250.value()) + "dB")
        self.freq250_freq_lbl = QtWidgets.QLabel(self)
        self.freq250_freq_lbl.setText("250hz")
        self.freq250_freq_lbl.setGeometry(200, -60, 30, 150)

        self.freq500 = QtWidgets.QSlider(self)
        self.freq500.setGeometry(230, 5, 15, 150)
        self.freq500.setMaximum(20)
        self.freq500.setMinimum(-20)
        self.freq500.setValue(config.getint('audio', '500hz'))
        self.freq500_lbl = QtWidgets.QLabel(self)
        self.freq500_lbl.setGeometry(245, 60, 30, 150)
        self.freq500_lbl.setText(str(self.freq500.value()) + "dB")
        self.freq500_freq_lbl = QtWidgets.QLabel(self)
        self.freq500_freq_lbl.setText("500hz")
        self.freq500_freq_lbl.setGeometry(245, -60, 30, 150)

        self.freq1k = QtWidgets.QSlider(self)
        self.freq1k.setGeometry(275, 5, 15, 150)
        self.freq1k.setMaximum(20)
        self.freq1k.setMinimum(-20)
        self.freq1k.setValue(config.getint('audio', '1khz'))
        self.freq1k_lbl = QtWidgets.QLabel(self)
        self.freq1k_lbl.setGeometry(290, 60, 30, 150)
        self.freq1k_lbl.setText(str(self.freq1k.value()) + "dB")
        self.freq1k_freq_lbl = QtWidgets.QLabel(self)
        self.freq1k_freq_lbl.setText("1khz")
        self.freq1k_freq_lbl.setGeometry(290, -60, 30, 150)

        self.freq2k = QtWidgets.QSlider(self)
        self.freq2k.setGeometry(320, 5, 15, 150)
        self.freq2k.setMaximum(20)
        self.freq2k.setMinimum(-20)
        self.freq2k.setValue(config.getint('audio', '2khz'))
        self.freq2k_lbl = QtWidgets.QLabel(self)
        self.freq2k_lbl.setGeometry(335, 60, 30, 150)
        self.freq2k_lbl.setText(str(self.freq2k.value()) + "dB")
        self.freq2k_freq_lbl = QtWidgets.QLabel(self)
        self.freq2k_freq_lbl.setText("2khz")
        self.freq2k_freq_lbl.setGeometry(335, -60, 30, 150)

        self.freq4k = QtWidgets.QSlider(self)
        self.freq4k.setGeometry(365, 5, 15, 150)
        self.freq4k.setMaximum(20)
        self.freq4k.setMinimum(-20)
        self.freq4k.setValue(config.getint('audio', '4khz'))
        self.freq4k_lbl = QtWidgets.QLabel(self)
        self.freq4k_lbl.setGeometry(380, 60, 30, 150)
        self.freq4k_lbl.setText(str(self.freq4k.value()) + "dB")
        self.freq4k_freq_lbl = QtWidgets.QLabel(self)
        self.freq4k_freq_lbl.setText("4khz")
        self.freq4k_freq_lbl.setGeometry(380, -60, 30, 150)

        self.freq8k = QtWidgets.QSlider(self)
        self.freq8k.setGeometry(410, 5, 15, 150)
        self.freq8k.setMaximum(20)
        self.freq8k.setMinimum(-20)
        self.freq8k.setValue(config.getint('audio', '8khz'))
        self.freq8k_lbl = QtWidgets.QLabel(self)
        self.freq8k_lbl.setGeometry(425, 60, 30, 150)
        self.freq8k_lbl.setText(str(self.freq8k.value()) + "dB")
        self.freq8k_freq_lbl = QtWidgets.QLabel(self)
        self.freq8k_freq_lbl.setText("8khz")
        self.freq8k_freq_lbl.setGeometry(425, -60, 30, 150)

        self.freq16k = QtWidgets.QSlider(self)
        self.freq16k.setGeometry(455, 5, 15, 150)
        self.freq16k.setMaximum(20)
        self.freq16k.setMinimum(-20)
        self.freq16k.setValue(config.getint('audio', '16khz'))
        self.freq16k_lbl = QtWidgets.QLabel(self)
        self.freq16k_lbl.setGeometry(470, 60, 30, 150)
        self.freq16k_lbl.setText(str(self.freq16k.value()) + "dB")
        self.freq16k_freq_lbl = QtWidgets.QLabel(self)
        self.freq16k_freq_lbl.setText("16khz")
        self.freq16k_freq_lbl.setGeometry(470, -60, 30, 150)

    def reset_eq(self):
        self.freq31.setValue(0)
        self.freq62.setValue(0)
        self.freq125.setValue(0)
        self.freq250.setValue(0)
        self.freq500.setValue(0)
        self.freq1k.setValue(0)
        self.freq2k.setValue(0)
        self.freq4k.setValue(0)
        self.freq8k.setValue(0)
        self.freq16k.setValue(0)


# main window class
class MainWindow(QMainWindow):

    def __init__(self):
        print("initializing main window")
        super(MainWindow, self).__init__()
        self.initUI()
        self.initAutoResume()
        self.setWindowTitle("PyMusX")
        self.move(500, 100)
        self.setFixedHeight(420)
        self.setFixedWidth(325)
        self.setWindowIcon(QIcon("Icon/main_logo.png"))
        change_theme()
        self.change_icon_color()
        self.yt_stream_win = StreamWindow()
        self.yt_stream_win.startStream.clicked.connect(self.initPyStreamer)
        app.aboutToQuit.connect(self.closeEvent)
        self.applyTranslucent()
        self.setWindowCentered()
        self.match_master_volume()

    def setWindowCentered(self):  # center the main window at startup
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, a0: QtGui.QCloseEvent):  # all code here executed when you press the "X" button
        config.set('saved_data', 'song_pos', str(self.player.get_time()))  # before closing the app, save the song position to config.pmx
        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

        sys.exit()  # close all windows when you hit the "X" button in main window

    def initUI(self):
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_duration)

        self.track_timer = QTimer()

        self.eq = eq_win()
        self.settings = SettingsWindow()
        self.player = vlc.MediaPlayer()
        self.media_eq = vlc.libvlc_audio_equalizer_new()
        self.val = 1
        self.restart_trigger = 1
        self.settings.opacity_sld.valueChanged.connect(self.win_opacity)

        self.docked_win = dockedWindow()
        self.docked_win.docked_browse.clicked.connect(self.dlg)
        self.docked_win.docked_stop_btn.clicked.connect(self.stop_playback)
        self.docked_win.docked_pause_btn.clicked.connect(self.pause_playback)
        self.docked_win.expandWindow_btn.clicked.connect(self.expand_window)
        self.docked_win.docked_eq_btn.clicked.connect(self.open)
        self.docked_win.docked_volume_slider.valueChanged.connect(self.match_master_volume)

        self.yt_btn = QtWidgets.QPushButton(self)
        self.yt_btn.setGeometry(3, 3, 27, 27)
        self.yt_btn.setIcon(QIcon('Icon/yt.png'))
        self.yt_btn.setIconSize(QSize(25, 25))
        self.yt_btn.setToolTip(langconf.get('main_window', 'yt_tooltip'))
        self.yt_btn.clicked.connect(self.open_ytstream_win)

        self.dockWindow_btn = QtWidgets.QPushButton(self)
        self.dockWindow_btn.setGeometry(295, 3, 27, 27)
        self.dockWindow_btn.clicked.connect(self.openDockedWindow)
        self.dockWindow_btn.setIcon(QIcon('Icon/shrink.png'))
        self.dockWindow_btn.setToolTip(langconf.get('main_window', 'dock_tooltip'))

        self.playback_stat_lbl = QtWidgets.QLabel(self)
        self.playback_stat_lbl.setText(langconf.get('main_window', 'play_stat'))

        if lang == "id":  # align label according to different languages to keep the label centered
            self.playback_stat_lbl.setGeometry(120, 5, 120, 25)
        elif lang == "en":
            self.playback_stat_lbl.setGeometry(130, 5, 120, 25)
        elif lang == "de":
            self.playback_stat_lbl.setGeometry(115, 5, 120, 25)

        self.song_title = QtWidgets.QTextBrowser(self)
        self.song_title.setGeometry(13, 35, 300, 34)
        self.song_title.setHtml('<p align="center" style="'
                                ' margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;'
                                ' -qt-block-indent:0; text-indent:0px;">Nothing (No Track Selected)</p></body></html>')

        self.dial = QtWidgets.QDial(self)
        self.dial.setValue(config.getint('audio', 'master_volume'))
        self.dial.setGeometry(90, 275, 140, 140)
        self.dial.setMinimum(0)
        self.dial.setMaximum(100)
        self.dial.setToolTip(langconf.get('main_window', 'volume_tooltip'))
        self.dial.valueChanged.connect(self.vol)
        vlc.libvlc_audio_set_volume(self.player, self.dial.value())

        self.lbl = QtWidgets.QLabel(self)
        self.lbl.move(170, 250)
        self.lbl.setText(str(self.dial.value()))

        self.browse = QtWidgets.QPushButton(self)
        self.browse.setIcon(QIcon('Icon/play.png'))
        self.browse.setGeometry(125, 115, 75, 75)
        self.browse.clicked.connect(self.dlg)
        self.browse.setToolTip(langconf.get('main_window', 'play_tooltip'))

        self.pause = QtWidgets.QPushButton(self)
        self.pause.setIcon(QIcon('Icon/pause.png'))
        self.pause.setGeometry(50, 135, 50, 50)
        self.pause.clicked.connect(self.pause_playback)
        self.pause.setToolTip(langconf.get('main_window', 'pause_tooltip'))

        self.stop = QtWidgets.QPushButton(self)
        self.stop.setIcon(QIcon('Icon/stop.png'))
        self.stop.setGeometry(224, 135, 50, 50)
        self.stop.clicked.connect(self.stop_playback)
        self.stop.setToolTip(langconf.get('main_window', 'stop_tooltip'))

        self.restart = QtWidgets.QPushButton(self)
        self.restart.setGeometry(132, 200, 60, 35)
        self.restart.clicked.connect(self.rest)
        self.restart.setIcon(QIcon('Icon/restart.png'))
        self.restart.setToolTip(langconf.get('main_window', 'replay_tooltip'))

        self.forward = QtWidgets.QPushButton(self)
        self.forward.setGeometry(300, 77, 20, 20)
        self.forward.setIcon(QIcon('Icon/forward.png'))
        self.forward.clicked.connect(self.seek_forward)
        self.forward.setToolTip(langconf.get('main_window', 'forward_tooltip'))

        self.rewind = QtWidgets.QPushButton(self)
        self.rewind.setGeometry(5, 77, 20, 20)
        self.rewind.setIcon(QIcon('Icon/rewind.png'))
        self.rewind.clicked.connect(self.seek_rewind)
        self.rewind.setToolTip(langconf.get('main_window', 'rewind_tooltip'))

        self.eq_btn = QtWidgets.QPushButton(self)
        self.eq_btn.setGeometry(2, 383, 35, 35)
        self.eq_btn.setIcon(QIcon('Icon/eq.png'))
        self.eq_btn.clicked.connect(self.open)
        self.eq_btn.setToolTip(langconf.get('main_window', 'eq_tooltip'))

        self.stgs_btn = QtWidgets.QPushButton(self)
        self.stgs_btn.setIcon(QIcon('Icon/settings.png'))
        self.stgs_btn.setGeometry(288, 383, 35, 35)
        self.stgs_btn.clicked.connect(self.open_settings)
        self.stgs_btn.setToolTip(langconf.get('main_window', 'settings_tooltip'))

        self.eq.pre.valueChanged.connect(self.pre_sld)
        self.eq.freq31.valueChanged.connect(self.frq31)
        self.eq.freq62.valueChanged.connect(self.frq62)
        self.eq.freq125.valueChanged.connect(self.frq125)
        self.eq.freq250.valueChanged.connect(self.frq250)
        self.eq.freq500.valueChanged.connect(self.frq500)
        self.eq.freq1k.valueChanged.connect(self.frq1k)
        self.eq.freq2k.valueChanged.connect(self.frq2k)
        self.eq.freq4k.valueChanged.connect(self.frq4k)
        self.eq.freq8k.valueChanged.connect(self.frq8k)
        self.eq.freq16k.valueChanged.connect(self.frq16k)

        self.eq.setWindowOpacity(float(self.settings.opacity_sld.value() / 100))
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")
        self.settings.opacity_sld.setValue(100)
        self.pixmap = QPixmap('Icon/med.png')
        self.icon = QtWidgets.QLabel(self)
        self.icon.setPixmap(self.pixmap)
        self.icon.move(140, 250)

        self.seekbar = QtWidgets.QSlider(Qt.Horizontal, self)
        self.seekbar.setGeometry(25, 75, 275, 25)
        self.seekbar.sliderPressed.connect(self.seek_time)
        self.seekbar.sliderReleased.connect(self.seek)
        self.seekbar.setToolTip(langconf.get('main_window', 'seek_tooltip'))
        self.seekbar.setMaximum(0)
        self.seekbar.setMinimum(0)
        self.seekbar.valueChanged.connect(self.update_preview)
        self.seekbar.sliderPressed.connect(self.timer.stop)

        self.docked_win.docked_seekbar.sliderPressed.connect(self.seek_time)
        self.docked_win.docked_seekbar.sliderReleased.connect(self.docked_seekbar_release)
        self.docked_win.docked_seekbar.valueChanged.connect(self.update_preview)
        self.docked_win.docked_seekbar.sliderPressed.connect(self.timer.stop)

        self.time_preview = QtWidgets.QLabel(self)
        self.time_preview.setText("0:00")
        self.time_preview.setGeometry(150, 63, 50, 25)
        self.time_preview.hide()

        self.track_length = QtWidgets.QLabel(self)
        self.track_length.setText("--:--")
        self.track_length.setToolTip(langconf.get('main_window', 'tracklength_tooltip'))
        self.track_length.setGeometry(280, 90, 50, 30)

        self.track_seek = QtWidgets.QLabel(self)
        self.track_seek.setText("--:--")
        self.track_seek.setToolTip(langconf.get('main_window', 'elapsed_tooltip'))
        self.track_seek.setGeometry(25, 90, 50, 30)

        self.settings.dark_btn.clicked.connect(self.change_icon_color)
        self.settings.light_btn.clicked.connect(self.change_icon_color)

    def match_master_volume(self):
        self.dial.setValue(
            self.docked_win.docked_volume_slider.value())  # match the dial with the volume slider in shrunked window

    def expand_window(self):
        self.docked_win.hide()
        self.show()

    def openDockedWindow(self):
        self.docked_win.show()
        self.hide()
        self.settings.hide()

    def applyTranslucent(self):
        if config.getboolean('ui', 'translucent'):
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            QtWinExtras.QtWin.enableBlurBehindWindow(self)
            self.settings.setAttribute(Qt.WA_TranslucentBackground, True)
            QtWinExtras.QtWin.enableBlurBehindWindow(self.settings)
            self.eq.setAttribute(Qt.WA_TranslucentBackground, True)
            QtWinExtras.QtWin.enableBlurBehindWindow(self.eq)
            self.yt_stream_win.setAttribute(Qt.WA_TranslucentBackground, True)
            QtWinExtras.QtWin.enableBlurBehindWindow(self.yt_stream_win)
            self.settings.module_win.setAttribute(Qt.WA_TranslucentBackground, True)
            QtWinExtras.QtWin.enableBlurBehindWindow(self.settings.module_win)
            self.docked_win.setAttribute(Qt.WA_TranslucentBackground, True)
            QtWinExtras.QtWin.enableBlurBehindWindow(self.docked_win)
        else:
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.settings.setAttribute(Qt.WA_TranslucentBackground, False)
            self.eq.setAttribute(Qt.WA_TranslucentBackground, False)
            self.yt_stream_win.setAttribute(Qt.WA_TranslucentBackground, False)
            self.settings.module_win.setAttribute(Qt.WA_TranslucentBackground, False)
            self.docked_win.setAttribute(Qt.WA_TranslucentBackground, False)

    def trackTimer(self):
        self.track_timer.start(config.getint('trackTimer', 'duration') * 60000)
        self.track_timer.timeout.connect(self.stop_playback)  # if timer limit reached, stop the song

    def initPyStreamer(self):  # this function handles the streaming playback

        if self.yt_stream_win.link.text() == "":  # if no link entered then do nothing
            pass
        else:

            if config.getboolean('trackTimer', 'on'):  # if the track timer is enabled, start counting
                self.trackTimer()
            else:
                pass

            self.playback_stat_lbl.setText(langconf.get('main_window', 'stream_stat'))
            self.playback_stat_lbl.move(120, 5)

            self.yt_stream_win.hide()
            self.player = vlc.MediaPlayer(self.yt_stream_win.song.url)
            print(self.yt_stream_win.song.url)
            self.restart_trigger += 1
            self.songname = self.yt_stream_win.song_url.title
            self.song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px'
                '; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                self.songname + '</p></body></html>')
            self.player.play()
            self.timer.start(100)

            self.docked_win.docked_song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px'
                '; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                self.songname + '</p></body></html>')
            self.player.play()
            self.timer.start(100)

            vlc.libvlc_audio_equalizer_set_preamp(self.media_eq, self.eq.pre.value())
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq31.value(), 0)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq62.value(), 1)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq125.value(), 2)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq250.value(), 3)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq500.value(), 4)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq1k.value(), 5)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq2k.value(), 6)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq4k.value(), 7)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq8k.value(), 8)
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq16k.value(), 9)
            vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)

            time.sleep(0.1)
            # check if song length is more than 1 hour (3600000ms), if it is then change format from mm:ss to hh:mm:ss
            if self.player.get_length() < 3600000:
                self.track_seek.setText(str(int((self.player.get_time() / 1000) / 60)) + ":" + str(
                    '%02d' % int((self.player.get_time() / 1000) % 60)))

            else:
                self.track_seek.setText(str(int((self.player.get_time() / (1000 * 60 * 60) % 24))) + ":" + str(
                    '%02d' % int((self.player.get_time() / (1000 * 60)) % 60)) + ":" + str(
                    '%02d' % int((self.player.get_time() / 1000) % 60)))

            # set the maximum slider value to match the track length
            self.track_length.setText(str(self.player.get_length()))
            self.seekbar.setMaximum(self.player.get_length())

    def open_ytstream_win(self):
        self.yt_stream_win.show()

    def change_icon_color(self):  # this function executed everytime you changed theme and at the start
        print("loading icons")
        if config.getboolean('theme', 'dark'):
            if self.dial.value() > 80:
                self.pixmap = QPixmap('Icon/full.png')
                self.icon.setPixmap(self.pixmap)

            elif self.dial.value() > 35 and self.dial.value() < 80:
                self.pixmap = QPixmap('Icon/med.png')
                self.icon.setPixmap(self.pixmap)

            elif self.dial.value() < 35 and self.dial.value() < 80:
                self.pixmap = QPixmap('Icon/low.png')
                self.icon.setPixmap(self.pixmap)

            if self.dial.value() == 0:
                self.pixmap = QPixmap('Icon/mute.png')
                self.icon.setPixmap(self.pixmap)
            self.browse.setIcon(QIcon('Icon/play.png'))
            self.docked_win.docked_browse.setIcon(QIcon('Icon/play.png'))
            self.stop.setIcon(QIcon('Icon/stop.png'))
            self.docked_win.docked_stop_btn.setIcon(QIcon('Icon/stop.png'))
            self.restart.setIcon(QIcon('Icon/restart.png'))
            self.pause.setIcon(QIcon('Icon/pause.png'))
            self.docked_win.docked_pause_btn.setIcon(QIcon('Icon/pause.png'))
            self.rewind.setIcon(QIcon('Icon/rewind.png'))
            self.forward.setIcon(QIcon('Icon/forward.png'))
            self.eq_btn.setIcon(QIcon('Icon/eq.png'))
            self.stgs_btn.setIcon(QIcon('Icon/settings.png'))
            self.settings.info.setIcon(QIcon('Icon/info.png'))
            self.yt_btn.setIcon(QIcon('Icon/yt.png'))
            self.settings.sys_aud.setIcon(QIcon('Icon/audio_settings.png'))
            self.dockWindow_btn.setIcon(QIcon('Icon/shrink.png'))
            self.docked_win.expandWindow_btn.setIcon(QIcon('Icon/expand.png'))
            self.docked_win.docked_eq_btn.setIcon(QIcon('Icon/eq.png'))

        else:
            if self.dial.value() > 80:
                self.pixmap = QPixmap('Icon/full_dark.png')
                self.icon.setPixmap(self.pixmap)

            elif self.dial.value() > 35 and self.dial.value() < 80:
                self.pixmap = QPixmap('Icon/med_dark.png')
                self.icon.setPixmap(self.pixmap)

            elif self.dial.value() < 35 and self.dial.value() < 80:
                self.pixmap = QPixmap('Icon/low_dark.png')
                self.icon.setPixmap(self.pixmap)

            if self.dial.value() == 0:
                self.pixmap = QPixmap('Icon/mute_dark.png')
                self.icon.setPixmap(self.pixmap)
            self.browse.setIcon(QIcon('Icon/play_dark.png'))
            self.docked_win.docked_browse.setIcon(QIcon('Icon/play_dark.png'))
            self.stop.setIcon(QIcon('Icon/stop_dark.png'))
            self.docked_win.docked_stop_btn.setIcon(QIcon('Icon/stop_dark.png'))
            self.restart.setIcon(QIcon('Icon/restart_dark.png'))
            self.pause.setIcon(QIcon('Icon/pause_dark.png'))
            self.docked_win.docked_pause_btn.setIcon(QIcon('Icon/pause_dark.png'))
            self.rewind.setIcon(QIcon('Icon/rewind_dark.png'))
            self.forward.setIcon(QIcon('Icon/forward_dark.png'))
            self.eq_btn.setIcon(QIcon('Icon/eq_dark.png'))
            self.stgs_btn.setIcon(QIcon('Icon/settings_dark.png'))
            self.settings.info.setIcon(QIcon('Icon/info_dark.png'))
            self.yt_btn.setIcon(QIcon('Icon/yt_dark.png'))
            self.settings.sys_aud.setIcon(QIcon('Icon/audio_settings_dark.png'))
            self.dockWindow_btn.setIcon(QIcon('Icon/shrink_dark.png'))
            self.docked_win.expandWindow_btn.setIcon(QIcon('Icon/expand_dark.png'))
            self.docked_win.docked_eq_btn.setIcon(QIcon('Icon/eq_dark.png'))

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == Qt.Key_D:
            self.seek_forward()

        elif event.key() == Qt.Key_A:
            self.seek_rewind()

        elif event.key() == Qt.Key_P:
            self.pause_playback()

        elif event.key() == Qt.Key_W:
            self.dial.setValue(self.dial.value() + 1)

        elif event.key() == Qt.Key_S:
            self.dial.setValue(self.dial.value() - 1)

        elif event.key() == Qt.Key_O:
            self.dlg()

        elif event.key() == Qt.Key_Backspace:
            self.stop_playback()

        elif event.key() == Qt.Key_R:
            self.rest()

    # function will show the preview of the
    # current song length (in the middle slightly above seekbar) while browsing the song length via seekbar
    def seek_time(self):
        self.time_preview.show()

    # update the current preview song length while browsing the song length via seekbar
    def update_preview(self):
        if self.seekbar.value() < 3600000:
            self.time_preview.setText(str(int((self.seekbar.value() / 1000) / 60)) + ":" + str(
                '%02d' % int((self.seekbar.value() / 1000) % 60)))
            self.time_preview.setGeometry(150, 63, 50, 25)

        if 600000 < self.seekbar.value() < 3600000:
            self.time_preview.setText(str(int((self.seekbar.value() / 1000) / 60)) + ":" + str(
                '%02d' % int((self.seekbar.value() / 1000) % 60)))
            self.time_preview.setGeometry(145, 63, 50, 25)

        elif self.seekbar.value() > 3600000:
            self.time_preview.setText(str(int((self.seekbar.value() / (1000 * 60 * 60) % 24))) + ":" + str(
                '%02d' % int((self.seekbar.value() / (1000 * 60)) % 60)) + ":" + str(
                '%02d' % int((self.seekbar.value() / 1000) % 60)))
            self.time_preview.setGeometry(140, 63, 50, 25)

    # fast forward 10 seconds (10000ms)

    def seek_forward(self):
        self.player.set_time(self.player.get_time() + 10000)

    # rewind 10 seconds (10000ms)
    def seek_rewind(self):
        # safety to prevent negative value, if the song position is less than 10s then pass.
        if self.seekbar.value() < 10000:
            pass
        else:
            self.player.set_time(self.player.get_time() - 10000)

    # seek the selected part in a song to play
    def seek(self):
        self.time_preview.hide()
        self.player.set_time(self.seekbar.value())
        if self.player.get_length() == -1 or 0:
            pass
        else:
            self.timer.start()

    def docked_seekbar_release(self):
        self.time_preview.hide()
        self.player.set_time(self.docked_win.docked_seekbar.value())

        if self.player.get_length() == -1 or 0:
            pass
        else:
            self.timer.start()

    # this function will be executed every 100ms
    # update seekbar position every 100ms (0.1s)
    def update_duration(self):
        self.seekbar.setMaximum(self.player.get_length())
        self.seekbar.setValue(self.player.get_time())

        self.docked_win.docked_seekbar.setMaximum(self.player.get_length())
        self.docked_win.docked_seekbar.setValue(self.player.get_time())
        self.timer.start(100)

        # check if song length is more than 1 hour (3600000ms), if it is then change format from mm:ss to hh:mm:ss
        if self.player.get_length() < 3600000:
            self.track_seek.setText(str(int((self.player.get_time() / 1000) / 60)) + ":" + str(
                '%02d' % int((self.player.get_time() / 1000) % 60)))
            self.setWindowTitle(str(int((self.player.get_time() / 1000) / 60)) + ":" + str(
                '%02d' % int((self.player.get_time() / 1000) % 60)) + "/" + str(
                int((self.player.get_length() / 1000) / 60)) + ":" + str(
                '%02d' % int((self.player.get_length() / 1000) % 60)) + " - PyMusX")
        else:
            self.track_seek.setText(str(int((self.player.get_time() / (1000 * 60 * 60) % 24))) + ":" + str(
                '%02d' % int((self.player.get_time() / (1000 * 60)) % 60)) + ":" + str(
                '%02d' % int((self.player.get_time() / 1000) % 60)))

            # update duration in window title
            self.setWindowTitle(str(int((self.player.get_time() / (1000 * 60 * 60) % 24))) + ":" + str(
                '%02d' % int((self.player.get_time() / (1000 * 60)) % 60)) + ":" + str(
                '%02d' % int((self.player.get_time() / 1000) % 60)) + "/" + str(
                int((self.player.get_length() / (1000 * 60 * 60) % 24))) + ":" + str(
                '%02d' % int((self.player.get_length() / (1000 * 60)) % 60)) + ":" + str(
                '%02d' % int((self.player.get_length() / 1000) % 60) + " - PyMusX"))

        if self.player.get_length() < 3600000:
            self.track_length.setText(str(int((self.player.get_length() / 1000) / 60)) + ":" + str(
                '%02d' % int((self.player.get_length() / 1000) % 60)))
            self.track_length.setGeometry(280, 90, 50, 30)

        else:
            self.track_length.setText(str(int((self.player.get_length() / (1000 * 60 * 60) % 24))) + ":" + str(
                '%02d' % int((self.player.get_length() / (1000 * 60)) % 60)) + ":" + str(
                '%02d' % int((self.player.get_length() / 1000) % 60)))
            self.track_length.setGeometry(265, 90, 50, 30)

    # def pre_sld to def 16k is to set the eq slider values and save it to config.pmx and theme.ini
    def pre_sld(self):
        vlc.libvlc_audio_equalizer_set_preamp(self.media_eq, self.eq.pre.value())
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', 'preamp', str(self.eq.pre.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq31(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq31.value(), 0)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq31_lbl.setText(str(self.eq.freq31.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '31hz', str(self.eq.freq31.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq62(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq62.value(), 1)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq62_lbl.setText(str(self.eq.freq62.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '62hz', str(self.eq.freq62.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq125(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq125.value(), 2)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq125_lbl.setText(str(self.eq.freq125.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '125hz', str(self.eq.freq125.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq250(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq250.value(), 3)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq250_lbl.setText(str(self.eq.freq250.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '250hz', str(self.eq.freq250.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq500(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq500.value(), 4)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq500_lbl.setText(str(self.eq.freq500.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '500hz', str(self.eq.freq500.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq1k(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq1k.value(), 5)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq1k_lbl.setText(str(self.eq.freq1k.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '1khz', str(self.eq.freq1k.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq2k(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq2k.value(), 6)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq2k_lbl.setText(str(self.eq.freq2k.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '2khz', str(self.eq.freq2k.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq4k(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq4k.value(), 7)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq4k_lbl.setText(str(self.eq.freq4k.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '4khz', str(self.eq.freq4k.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq8k(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq8k.value(), 8)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq8k_lbl.setText(str(self.eq.freq8k.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '8khz', str(self.eq.freq8k.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def frq16k(self):
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq16k.value(), 9)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)
        self.eq.freq16k_lbl.setText(str(self.eq.freq16k.value()) + "dB")
        self.eq.pre_lbl.setText(str(self.eq.pre.value()) + "dB")

        config.set('audio', '16khz', str(self.eq.freq16k.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    # function to set window opacity.
    def win_opacity(self):
        self.setWindowOpacity(float(self.settings.opacity_sld.value() / 100))
        self.settings.setWindowOpacity(float(self.settings.opacity_sld.value() / 100))
        self.eq.setWindowOpacity(float(self.settings.opacity_sld.value() / 100))
        self.settings.opacity_lbl_val.setText(str(self.settings.opacity_sld.value()) + "%")

    # function to show settings window
    def open_settings(self):
        self.settings.show()

    # function to show eq window (pyeq window)
    def open(self):
        self.eq.show()

    # function to open tkinter dialog and select song
    def dlg(self):
        self.restart_trigger += 1
        self.player.stop()
        root = Tk()
        root.withdraw()
        root.iconbitmap('Icon/pmx_browse_icon.ico')
        self.dialog = root.filename = filedialog.askopenfilename(initialdir="\Music", title="Browse For Music",
                                                                 filetypes=(
                                                                     ("MPEG-3", "*mp3"), ("Losless", "*flac"),
                                                                     ("OGG Vorbis", "*ogg"),
                                                                     ("WAV", "*wav"), ("MPEG-4, *m4a"),
                                                                     ("Advanced Audio Codec", "*aac"),
                                                                     ("Windows Media Audio", "*wma")))
        self.player = vlc.MediaPlayer(self.dialog)
        self.player.play()
        self.songname = os.path.basename(self.dialog)

        vlc.libvlc_audio_equalizer_set_preamp(self.media_eq, self.eq.pre.value())
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq31.value(), 0)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq62.value(), 1)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq125.value(), 2)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq250.value(), 3)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq500.value(), 4)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq1k.value(), 5)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq2k.value(), 6)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq4k.value(), 7)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq8k.value(), 8)
        vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq16k.value(), 9)
        vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)

        # check if user canceled to select song
        if self.dialog == "":
            self.track_length.setText("--:--")
            self.song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px;'
                ' margin-left:0px; margin-right:0px; -qt-block-indent:0;'
                ' text-indent:0px;">Nothing (No Track Selected)</p></body></html>')
            print("Playing Nothing")

            self.docked_win.docked_song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px;'
                ' margin-left:0px; margin-right:0px; -qt-block-indent:0;'
                ' text-indent:0px;">Nothing (No Track Selected)</p></body></html>')
            print("Playing Nothing")
        else:

            if config.getboolean('trackTimer', 'on'):  # if the track timer is enabled, start counting
                self.trackTimer()
            else:
                pass

            self.playback_stat_lbl.setText(langconf.get('main_window', 'play_stat'))

            self.song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px'
                '; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                os.path.splitext(self.songname)[0] + '</p></body></html>')

            self.docked_win.docked_song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px'
                '; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                os.path.splitext(self.songname)[0] + '</p></body></html>')
            print("Playing " + self.dialog)
            self.timer.start(100)

            # save directory of the last played song to auto-resume
            config.set('saved_data', 'last_played', str(self.dialog))

            with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
                config.write(configfile)

            time.sleep(0.1)
            # check if song length is more than 1 hour (3600000ms), if it is then change format from mm:ss to hh:mm:ss
            if self.player.get_length() < 3600000:
                self.track_length.setText(str(int((self.player.get_length() / 1000) / 60)) + ":" + str(
                    '%02d' % int((self.player.get_length() / 1000) % 60)))
                self.track_length.setGeometry(280, 90, 50, 30)

            else:
                self.track_length.setText(str(int((self.player.get_length() / (1000 * 60 * 60) % 24))) + ":" + str(
                    '%02d' % int((self.player.get_length() / (1000 * 60)) % 60)) + ":" + str(
                    '%02d' % int((self.player.get_length() / 1000) % 60)))
                self.track_length.setGeometry(265, 90, 50, 30)

        # set the maximum slider value to match the track length
        self.seekbar.setMaximum(self.player.get_length())
        self.seekbar.setMinimum(0)
        self.docked_win.docked_seekbar.setMaximum(self.player.get_length())
        self.docked_win.docked_seekbar.setMinimum(0)

    # auto resume song after reopening music player
    def initAutoResume(self):
        print("checking track to resume")
        if config.get('saved_data', 'last_played') == "":  # if there's no song to resume then pass
            self.track_length.setText("--:--")
            self.song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px;'
                ' margin-left:0px; margin-right:0px; -qt-block-indent:0;'
                ' text-indent:0px;">' + langconf.get('main_window', 'stat_no_track') + '</p></body></html>')

            self.docked_win.docked_song_title.setHtml(
                '<p align="center" style=" margin-top:0px; margin-bottom:0px;'
                ' margin-left:0px; margin-right:0px; -qt-block-indent:0;'
                ' text-indent:0px;">' + langconf.get('main_window', 'stat_no_track') + '</p></body></html>')
            print("no track found to resume")
        else:

            if config.getboolean('trackTimer', 'on'):  # if the track timer is enabled, start counting
                self.trackTimer()
            else:
                pass

            # if the song is moved/deleted then show popup.
            if not os.path.isfile(config.get('saved_data', 'last_played')):  # checking if the song file present or not.

                print("Couldn't auto resume song (" + config.get('saved_data',
                                                                 'last_played') + ") The file is moved to different directory, renamed or deleted")

                warn = QtWidgets.QMessageBox(self)
                warn.setWindowIcon(QIcon('Icon/main_logo.png'))
                warn.setWindowTitle("Failed to auto resume song")
                warn.setText("Failed to auto resume (" + config.get('saved_data',
                                                                    'last_played') + "): The file is moved to a different directory, renamed or deleted")
                warn.setIcon(QMessageBox.Warning)
                warn.exec_()
                config.set('saved_data', 'last_played', '')  # empty the last played section so it wont cause error
            else:
                self.player = vlc.MediaPlayer(config.get('saved_data', 'last_played'))
                self.player.play()
                self.player.set_time(config.getint('saved_data', 'song_pos'))
                self.songname = os.path.basename(config.get('saved_data', 'last_played'))
                self.restart_trigger += 1
                self.song_title.setHtml(
                    '<p align="center" style=" margin-top:0px; margin-bottom:0px'
                    '; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                    os.path.splitext(self.songname)[0] + '</p></body></html>')

                self.docked_win.docked_song_title.setHtml(
                    '<p align="center" style=" margin-top:0px; margin-bottom:0px'
                    '; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                    os.path.splitext(self.songname)[0] + '</p></body></html>')
                print("Resuming " + config.get('saved_data', 'last_played') + " At Position " + str(config.getint('saved_data', 'song_pos')))
                self.timer.start(100)

                vlc.libvlc_audio_equalizer_set_preamp(self.media_eq, self.eq.pre.value())
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq31.value(), 0)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq62.value(), 1)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq125.value(), 2)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq250.value(), 3)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq500.value(), 4)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq1k.value(), 5)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq2k.value(), 6)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq4k.value(), 7)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq8k.value(), 8)
                vlc.libvlc_audio_equalizer_set_amp_at_index(self.media_eq, self.eq.freq16k.value(), 9)
                vlc.libvlc_media_player_set_equalizer(self.player, self.media_eq)

                time.sleep(0.1)
                # check if song length is more than 1 hour (3600000ms), if it is then change format from mm:ss to hh:mm:ss
                if self.player.get_length() < 3600000:
                    self.track_length.setText(str(int((self.player.get_length() / 1000) / 60)) + ":" + str(
                        '%02d' % int((self.player.get_length() / 1000) % 60)))
                    self.track_length.setGeometry(280, 90, 50, 30)

                else:
                    self.track_length.setText(str(int((self.player.get_length() / (1000 * 60 * 60) % 24))) + ":" + str(
                        '%02d' % int((self.player.get_length() / (1000 * 60)) % 60)) + ":" + str(
                        '%02d' % int((self.player.get_length() / 1000) % 60)))
                    self.track_length.setGeometry(265, 90, 50, 30)

                # set the maximum slider value to match the track length
                self.seekbar.setMaximum(self.player.get_length())
                self.seekbar.setMinimum(0)
                self.docked_win.docked_seekbar.setMaximum(self.player.get_length())
                self.docked_win.docked_seekbar.setMinimum(0)

    def rest(self):

        # safety trigger to avoid python to crash, checks if there's available track to replay, if not then pass.
        if self.player.get_length() == -1 or 0:
            pass
        else:
            self.timer.stop()
            self.timer.start()
            if self.restart_trigger > 1:
                self.player.stop()
                self.player.play()
                vlc.libvlc_audio_set_volume(self.player, self.dial.value())
                self.song_title.setHtml(
                    '<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px'
                    '; margin-right:0px; -qt-block-indent:0; text-indent:0px;">' +
                    os.path.splitext(self.songname)[0] + '</p></body></html>')
                time.sleep(0.05)
                self.seekbar.setMaximum(self.player.get_length())

    # function to pause playback
    def pause_playback(self):
        self.player.pause()
        self.val += 1

        # change icon
        if config.getboolean('theme', 'dark'):
            if (self.val % 2) == 0:
                self.pause.setIcon(QIcon('Icon/resume.png'))
                self.docked_win.docked_pause_btn.setIcon(QIcon('Icon/resume.png'))
                self.pause.setToolTip(langconf.get('main_window', 'unpause_tooltip'))
                self.docked_win.docked_pause_btn.setToolTip(langconf.get('main_window', 'unpause_tooltip'))
            else:
                self.pause.setIcon(QIcon('Icon/pause.png'))
                self.docked_win.docked_pause_btn.setIcon(QIcon('Icon/pause.png'))
                self.pause.setToolTip(langconf.get('main_window', 'pause_tooltip'))
                self.docked_win.docked_pause_btn.setToolTip(langconf.get('main_window', 'pause_tooltip'))
        else:
            if (self.val % 2) == 0:
                self.pause.setIcon(QIcon('Icon/resume_dark.png'))
                self.docked_win.docked_pause_btn.setIcon(QIcon('Icon/resume_dark.png'))
                self.pause.setToolTip(langconf.get('main_window', 'unpause_tooltip'))
                self.docked_win.docked_pause_btn.setToolTip(langconf.get('main_window', 'unpause_tooltip'))
            else:
                self.pause.setIcon(QIcon('Icon/pause_dark.png'))
                self.docked_win.docked_pause_btn.setIcon(QIcon('Icon/pause_dark.png'))
                self.pause.setToolTip(langconf.get('main_window', 'pause_tooltip'))
                self.docked_win.docked_pause_btn.setToolTip(langconf.get('main_window', 'unpause_tooltip'))

    # function to stop playback and reset all seekbar values
    def stop_playback(self):

        # if there's no song to stop then pass
        if self.player.get_length() == -1 or 0:
            pass

        else:
            self.track_timer.stop()
            self.setWindowTitle("PyMusX")
            self.seekbar.setMaximum(0)
            self.seekbar.setMinimum(0)
            self.docked_win.docked_seekbar.setMaximum(0)
            self.docked_win.docked_seekbar.setMinimum(0)
            self.timer.stop()
            self.seekbar.setValue(0)
            self.docked_win.docked_seekbar.setValue(0)
            self.track_seek.setText("--:--")
            self.track_length.setText("--:--")
            self.player.stop()
            self.song_title.setHtml('<p align="center" style=" margin-top:0px; margin-bottom:0px;'
                                    ' margin-left:0px; margin-right:0px;'
                                    ' -qt-block-indent:0; text-indent:0px;"> Nothing (Playback Stopped) </p></body></html>')

            self.docked_win.docked_song_title.setHtml('<p align="center" style=" margin-top:0px; margin-bottom:0px;'
                                                      ' margin-left:0px; margin-right:0px;'
                                                      ' -qt-block-indent:0; text-indent:0px;"> Nothing (Playback Stopped) </p></body></html>')

            # this will empty the last played section and song position in config.pmx
            config.set('saved_data', 'last_played', '')
            config.set('saved_data', 'song_pos', '0')

            with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
                config.write(configfile)

    # function to set main volume/master volume and change speaker icon according to specific levels; low, med, full.
    def vol(self):
        vlc.libvlc_audio_set_volume(self.player, self.dial.value())
        self.lbl.setText(str(self.dial.value()))
        self.docked_win.docked_volume_slider.setValue(self.dial.value())
        if self.dial.value() > 80:
            if config.getboolean('theme', 'dark'):
                self.pixmap = QPixmap('Icon/full.png')
                self.icon.setPixmap(self.pixmap)
            else:
                self.pixmap = QPixmap('Icon/full_dark.png')
                self.icon.setPixmap(self.pixmap)

        elif 35 < self.dial.value() < 80:
            if config.getboolean('theme', 'dark'):
                self.pixmap = QPixmap('Icon/med.png')
                self.icon.setPixmap(self.pixmap)
            else:
                self.pixmap = QPixmap('Icon/med_dark.png')
                self.icon.setPixmap(self.pixmap)

        elif self.dial.value() < 35 and self.dial.value() < 80:
            if config.getboolean('theme', 'dark'):
                self.pixmap = QPixmap('Icon/low.png')
                self.icon.setPixmap(self.pixmap)
            else:
                self.pixmap = QPixmap('Icon/low_dark.png')
                self.icon.setPixmap(self.pixmap)

        if self.dial.value() == 0:
            if config.getboolean('theme', 'dark'):
                self.pixmap = QPixmap('Icon/mute.png')
                self.icon.setPixmap(self.pixmap)
            else:
                self.pixmap = QPixmap('Icon/mute_dark.png')
                self.icon.setPixmap(self.pixmap)

        # autosave master volume value to config.pmx
        config.set('audio', 'master_volume', str(self.dial.value()))

        with open('configs/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)


def window():
    print("initializing GUI")
    global app
    app = QApplication(sys.argv)
    win = MainWindow()
    app.setStyle('Fusion')
    win.show()
    sys.exit(app.exec_())


def change_theme():
    if config.getboolean('theme', 'dark'):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

    else:
        palette = QPalette()
        app.setPalette(palette)


window()

