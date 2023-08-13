import sys
import os, time
import subprocess
from Page.InputPage import Inputpage
from aip import AipSpeech
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.asr_translation import prepare_files, asr, translation
#from modules.synthetise_video import synthetise_video

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QSizePolicy, QLabel, QStackedWidget,QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

APP_ID='31180875'
API_KEY='2nnktWvBHaBa3drUiLqrELLB'
SECRET_KEY='sGSTdQj8KVr17uGZG2TVcCGMVe31Eejd'

def messagebox_generate(message):
    message_box=QMessageBox()
    message_box.setText(message)
    message_box.exec_()


class Processpage(QWidget):
    synthetised_audio_signal=pyqtSignal(str)
    def __init__(self):
        
        super().__init__()
        
        
        self.asr_res=QLabel(self)
        self.translation_res=QLabel(self)
        self.asr_btn=QPushButton("ASR",self)
        self.tran_btn=QPushButton("Translate",self)
        self.pron_btn=QPushButton("Synthetise audio",self)
        self.play_btn=QPushButton("Play audio",self)
        self.load_audio=False
        self.audio_player=QMediaPlayer(self)
        self.audio_widget=QVideoWidget(self)
        self.audio_player.setVideoOutput(self.audio_widget)
        self.audio_widget.show()
        
        
        self.main_layout=QHBoxLayout(self)
        self.asr_layout=QVBoxLayout(self)
        self.trans_layout=QVBoxLayout(self)
        self.pron_layout=QVBoxLayout(self)
        
        self.asr_res.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.asr_res.setWordWrap(True)
        self.asr_layout.addWidget(self.asr_res)
        self.asr_layout.addWidget(self.asr_btn)
        
        self.translation_res.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.translation_res.setWordWrap(True)
        self.trans_layout.addWidget(self.translation_res)
        self.trans_layout.addWidget(self.tran_btn)
        
        self.audio_widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.pron_btn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.play_btn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.pron_layout.addWidget(self.audio_widget)
        self.pron_layout.addWidget(self.pron_btn)
        self.pron_layout.addWidget(self.play_btn)
        
        self.main_layout.addLayout(self.asr_layout)
        self.main_layout.addLayout(self.trans_layout)
        self.main_layout.addLayout(self.pron_layout)
        
        
        self.play_btn.clicked.connect(self.play_audio)
        self.pron_btn.clicked.connect(self.synthetise_pron)
        self.asr_btn.clicked.connect(self.asr_audio)
        self.tran_btn.clicked.connect(self.trans_audio)
        
        
        self.setLayout(self.main_layout)
        
    def audio_slot(self,filename):
        #self.audio_slot_path="/Users/yixinzhang/visual_sys/extract_audio/extract.wav"
        self.audio_slot_path=filename
        print(self.audio_slot_path)
        self.load_audio=True
    
    
    def play_audio(self):
        #file_path="/Users/yixinzhang/visual_sys/syn_audio/syn_audio.mp3"
        #url=QUrl.fromLocalFile(file_path)
        if self.load_audio==True:
            url=QUrl.fromLocalFile(self.syn_res_path)
        self.audio_player.setMedia(QMediaContent(url))
        self.audio_player.play()
        
    def delete_last_line(taskidname):
        with open('/Users/yixinzhang/visual_sys/taskIds.txt', 'r') as f:
            lines = f.readlines()
        lines.pop()
        with open('/Users/yixinzhang/visual_sys/taskIds.txt', 'w') as f:
            f.writelines(lines)


    def asr_audio(self,filename):
        #filename="/Users/yixinzhang/data/merge3.wav"
        
        filename=self.audio_slot_path
        print(filename)
        self.delete_last_line()
        prepare_files(filename)
        time.sleep(10)
        res=asr(filename)
        print(res)
        self.asr_res.setText(res)
        messagebox_generate("ASR complete!\n"+"result:\n"+res)
        return res
        
        
        
        
    def trans_audio(self):
        trans_res=translation(str(self.asr_res.text()))
        self.translation_res.setText(trans_res)
        return trans_res
        
        
        
    def synthetise_pron(self):
        client=AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        print(self.translation_res.text())
        result=client.synthesis(self.translation_res.text(), 'en',1,{
            'vol':5,
            'spd':5,
            'pit':9,
            'per':4,#女0 男1 萝莉4 逍遥3
        })
        print("synthetising!")
        time.sleep(10)
        if not isinstance(result, dict):
            self.syn_res_path='/Users/yixinzhang/visual_sys/ssh_file/course/syn_audio.mp3'
            with open(self.syn_res_path,'wb') as fle:
                fle.write(result)
                self.load_audio=True
                self.synthetised_audio_signal.emit(self.syn_res_path)
        message_box=QMessageBox()
        message_box.setText('语音合成完成！')
        message_box.exec_()
        
        
        
        
        