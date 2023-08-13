import sys
import os
import time
import select
import paramiko
import subprocess
from Page.InputPage import Inputpage
from aip import AipSpeech
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.asr_translation import prepare_files, asr, translation
#from modules.synthetise_video import synthetise_video
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QSizePolicy, QLabel, QStackedWidget, QProgressBar,QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# 定义SSH连接信息
gauss_hostname = '202.120.38.69'
gauss_port = 5566
gauss_username = 'gyh17'
gauss_password = 'Sp1ch!ab'
fourier_hostname='wiener'
fourier_password='Sp1ch!ab'

local_course_source_path="/Users/yixinzhang/visual_sys/ssh_file/course/syn_audio.mp3"
local_image_source_path="/Users/yixinzhang/visual_sys/ssh_file/image/image_source.jpg"
local_pose_source_path="/Users/yixinzhang/visual_sys/ssh_file/pose/pose_source.mp4"

remote_course_source_path="/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_file/course/syn_audio.mp3"
remote_image_source_path="/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_file/image/image_source.jpg"
remote_pose_source_path="/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/ssh_file/pose/pose_source.mp4"


def wait_for_response(channel, length=1):
    time.sleep(3)
    ready = select.select([channel], [], [], 30.0)
    if ready[0]:
    # 如果有数据到来，则读取数据
        output = channel.recv(1024*length)
        return output
    else:
    # 如果没有数据到来，则提示超时
        print("Timeout waiting for data")

def messagebox_generate(message):
    message_box=QMessageBox()
    message_box.setText(message)
    message_box.exec_()
    
class SSHThread(QThread):
        progress_signal=pyqtSignal(int)
        finish_signal=pyqtSignal()
        
        def __init__(self):
            super().__init__()
            print("Thread started!")
            
        
        def run(self):
             # 建立SSH连接
            ssh_gauss = paramiko.SSHClient()
            ssh_gauss.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_gauss.connect(gauss_hostname, gauss_port, gauss_username, gauss_password)

            # 使用SSH连接执行命令
            stdin, stdout, stderr = ssh_gauss.exec_command('ls -l')
            print(stdout.read().decode('gb18030'))
            channel = ssh_gauss.invoke_shell()  # 建立交互式会话
            channel.send('ssh wiener\n')  # 连接到fourier
            time.sleep(10)
            print(wait_for_response(channel).decode())
            self.progress_signal.emit(10)

            channel.send(fourier_password+'\n')
            time.sleep(5)
            print(wait_for_response(channel).decode())
            self.progress_signal.emit(20)


            channel.send('nvidia-smi\n')  # 在fourier上执行nvidia-smi命令
            time.sleep(3)
            print(wait_for_response(channel,10).decode())
            self.progress_signal.emit(30)

            channel.send('ls -l\n')
            print(wait_for_response(channel).decode())
            channel.send('conda activate 3d\n')
            print(wait_for_response(channel).decode())
            self.progress_signal.emit(35)

            channel.send('cd /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved\n')
            print(wait_for_response(channel).decode())
            self.progress_signal.emit(40)

            channel.send('ls\n')
            print(wait_for_response(channel).decode())
            self.progress_signal.emit(50)

            channel.send('python /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/scripts/prepare_testing_files.py\n')
            time.sleep(8)
            print(wait_for_response(channel,10).decode())
            self.progress_signal.emit(70)

            channel.send('bash /mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/experiments/demo_vox.sh\n')
            time.sleep(50)
            print(wait_for_response(channel,20).decode())
            self.progress_signal.emit(100)
            ssh_gauss.close()
            self.finish_signal.emit()    
    
    
    



class Synpage(QWidget):
    
    
    def __init__(self):
        super().__init__()
        self.final_player=QMediaPlayer(self)
        self.final_widget=QVideoWidget(self)
        self.final_player.setVideoOutput(self.final_widget)
        self.final_widget.show()
        self.final_widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.if_load_pose=False
        self.if_load_image=False
        self.if_load_course=False
        
        
        self.progress_bar=QProgressBar(self)
        self.progress_bar.setGeometry(10, 10, 200, 25)
        
        self.upload_btn=QPushButton("Upload Files(Image, Pose, Course)",self)
        self.syn_btn=QPushButton("Synthetise Video",self)
        self.download_btn=QPushButton("Download Synthetised Video",self)
        self.play_video_btn=QPushButton("Play Synthetised Video",self)
        
        self.progress_label=QLabel("Synthesize progress:",self)
        self.percentage_label=QLabel("%",self)
        
        self.hor_layout=QHBoxLayout(self)
        self.progress_layout=QHBoxLayout(self)
        self.v2_layout=QVBoxLayout(self)
        self.v2_layout.addWidget(self.final_widget)
        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.percentage_label)
        self.final_layout=QVBoxLayout(self)
        self.final_layout.addWidget(self.upload_btn)
        self.final_layout.addWidget(self.syn_btn)
        self.final_layout.addWidget(self.download_btn)
        self.final_layout.addWidget(self.play_video_btn)
        self.final_layout.addWidget(self.progress_label)
        self.final_layout.addLayout(self.progress_layout)
        
        self.syn_btn.clicked.connect(self.syn_final_video)
        self.play_video_btn.clicked.connect(self.final_play)
        self.download_btn.clicked.connect(self.download_final_video)
        self.upload_btn.clicked.connect(self.upload_files)
        
        self.hor_layout.addLayout(self.v2_layout)
        self.hor_layout.addLayout(self.final_layout)
        
        self.setLayout(self.hor_layout)
            
        
        
    def upload_files(self):
        # 建立SSH连接
        ssh_gauss = paramiko.SSHClient()
        ssh_gauss.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_gauss.connect(gauss_hostname, gauss_port, gauss_username, gauss_password)

        # 使用SSH连接执行命令
        stdin, stdout, stderr = ssh_gauss.exec_command('ls -l')
        print(stdout.read().decode('gb18030'))
        
        sftp = ssh_gauss.open_sftp()
        sftp.put(local_course_source_path,remote_course_source_path)
        sftp.put(local_image_source_path,remote_image_source_path)
        sftp.put(local_pose_source_path,remote_pose_source_path)
        sftp.close()
        print("Files uploaded!")
        ssh_gauss.close()
        messagebox_generate("Files uploaded!")
        
    
    def final_play(self):
        mediaContent = QMediaContent(QUrl.fromLocalFile('/Users/yixinzhang/visual_sys/ssh_result/avconcat.mp4'))
        self.final_player.setMedia(mediaContent)
        self.final_player.setVideoOutput(self.final_widget)
        self.final_player.play()
        
        
    def pose_source_slot(self,filename):
        self.pose_source=filename
        self.if_load_pose=True
        
    def audio_source_slot(self,filename):
        self.audio_source=filename
        self.if_load_audio=True
        
    def image_source_slot(self,filename):
        self.image_source=filename
        self.if_load_image=True
        
    def update_progress(self,value):
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
    
    def process_finished(self):
        messagebox_generate("Synthetise complete!")
        
    def syn_final_video(self):
        self.syn_thread=SSHThread()
        self.syn_thread.progress_signal.connect(self.update_progress)
        self.syn_thread.finish_signal.connect(self.process_finished)
        self.syn_thread.start()
        

        
    
    def download_final_video(self):
        # 建立SSH连接
        ssh_gauss = paramiko.SSHClient()
        ssh_gauss.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_gauss.connect(gauss_hostname, gauss_port, gauss_username, gauss_password)

        # 使用SSH连接执行命令
        stdin, stdout, stderr = ssh_gauss.exec_command('ls -l')
        print(stdout.read().decode('gb18030'))
        
        # 建立SFTP连接
        sftp = ssh_gauss.open_sftp()

        # 下载文件
        local_result_path = '/Users/yixinzhang/visual_sys/ssh_result/avconcat.mp4'
        remote_result_path = '/mnt/xlancefs/home/gyh17/yixin_zhang/PC-AVS/improved/results/id_image_source_pose_pose_source_audio_syn_audio/avconcat.mp4'
        sftp.get(remote_result_path, local_result_path)

        # 关闭SFTP连接
        sftp.close()

        # 关闭SSH连接
        ssh_gauss.close()
        
        print("Download complete!")
        messagebox_generate("Download complete!")