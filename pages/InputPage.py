import sys
import os
import subprocess
from moviepy.editor import AudioFileClip
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from PyQt5.QtCore import QUrl, Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QSizePolicy, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class Inputpage(QWidget):
    courseSignal=pyqtSignal(str)
    poseSignal=pyqtSignal(str)
    imageSignal=pyqtSignal(str)
    def __init__(self):
        super().__init__()
        
        self.playbtn1=QPushButton('Play source video', self)
        self.playbtn2=QPushButton('Play pose source', self)
        self.choosebtn = QPushButton('Choose course video', self)
        self.posebtn=QPushButton('Choose pose source',self)
        
        self.video1 = QVideoWidget(self)
        self.video2 = QVideoWidget(self)
        
        self.player1 = QMediaPlayer(self)
        self.player1.setVideoOutput(self.video1)
        #self.player1.setMedia(QMediaContent(QUrl.fromLocalFile("/Users/yixinzhang/data/target.mp4")))
        self.player2=QMediaPlayer(self)
        self.player2.setVideoOutput(self.video2)
        #self.player2.setMedia(QMediaContent(QUrl.fromLocalFile("/Users/yixinzhang/data/Pose_Source.mp4")))
        self.picbtn=QPushButton('Load image',self)
        
        self.im_dis=QLabel(self)
        self.im_area=QPixmap()
        
        self.playbtn1.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.playbtn2.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.picbtn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.posebtn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.choosebtn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.video1.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.video2.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.picbtn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.im_dis.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        
        self.mainpagelayout=QHBoxLayout(self)
        self.courselayout=QVBoxLayout(self)
        self.imagelayout=QVBoxLayout(self)
        self.poselayout=QVBoxLayout(self)
        
        
        self.courselayout.addWidget(self.video1)
        self.courselayout.addWidget(self.choosebtn)
        self.courselayout.addWidget(self.playbtn1)
        
        self.imagelayout.addWidget(self.im_dis)
        self.imagelayout.addWidget(self.picbtn)
        
        self.poselayout.addWidget(self.video2)
        self.poselayout.addWidget(self.posebtn)
        self.poselayout.addWidget(self.playbtn2)
        
        self.mainpagelayout.addLayout(self.courselayout)
        self.mainpagelayout.addLayout(self.imagelayout)
        self.mainpagelayout.addLayout(self.poselayout)
        
        self.choosebtn.clicked.connect(self.choose_video)
        self.picbtn.clicked.connect(self.choose_image)
        self.posebtn.clicked.connect(self.choose_pose)
        self.playbtn1.clicked.connect(self.play1)
        self.playbtn2.clicked.connect(self.play2)
        
        self.courseSignal.connect(self.sendCourseSignal)
        self.poseSignal.connect(self.sendPoseSignal)
        self.imageSignal.connect(self.sendImageSignal)
        
        self.setLayout(self.mainpagelayout)
        
    def play1(self):
        self.player1.play()
    
    def play2(self):
        self.player2.play()
        
    def choose_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Image Files (*.jpg *.jpeg *.bmp)')
        file_dialog.selectNameFilter('Image Files (*.jpg *.jpeg *.bmp)')
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.image_path = file_dialog.selectedFiles()[0]
            self.im_area.load(self.image_path)
            self.im_dis.setPixmap(self.im_area)
            self.imageSignal.emit(self.image_path)
        
            path = os.path.join(current_dir, "ssh_file/image")
            os.makedirs(path, exist_ok=True)
        
            with open(os.path.join(path, 'image_source.jpg'), 'wb') as f:
                with open(self.image_path, 'rb') as image_file:
                    f.write(image_file.read())
        


    def choose_video(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Video Files (*.mp4 *.avi *.mov)')
        file_dialog.selectNameFilter('Video Files (*.mp4 *.avi *.mov)')
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.video_path = file_dialog.selectedFiles()[0]
            self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.video_clip=AudioFileClip(self.video_path)
            print(Path.cwd())
        
            self.audio_clip_path = str(Path.cwd() / "extract_audio" / "extract.wav")
        
            self.video_clip.write_audiofile(self.audio_clip_path)
        
            self.courseSignal.emit(self.audio_clip_path)
        
            course_dir = os.path.join(current_dir, "ssh_file/course")
            os.makedirs(course_dir, exist_ok=True)
            with open(os.path.join(course_dir, 'course_source.wav'), 'wb') as f:
                with open(self.audio_clip_path, 'rb') as audio_file:
                    f.write(audio_file.read())
                
    def choose_pose(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Video Files (*.mp4 *.avi *.mov)')
        file_dialog.selectNameFilter('Video Files (*.mp4 *.avi *.mov)')
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.pose_path = file_dialog.selectedFiles()[0]
            self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(self.pose_path)))
            self.poseSignal.emit(self.pose_path)
        
            pose_dir = os.path.join(current_dir, "ssh_file/pose")
            os.makedirs(pose_dir, exist_ok=True)
            with open(os.path.join(pose_dir, 'pose_source.mp4'), 'wb') as f:
                f.write(open(self.pose_path, 'rb').read())
            
        
    def sendCourseSignal(self,coursePath):
        print(coursePath)
        
    def sendPoseSignal(self,posePath):
        print(posePath)
        
    def sendImageSignal(self,imagePath):
        print(imagePath)
        
        
    

        

    
