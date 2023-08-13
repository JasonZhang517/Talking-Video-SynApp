from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Page.InputPage import Inputpage
from Page.ProcessPage import Processpage
from Page.SynPage import Synpage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建堆叠窗口
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # 创建所有页面
        self.page1 = Inputpage()
        self.page2 = Processpage()
        self.page3=Synpage()

        # 添加页面到堆叠窗口
        self.tab_widget.addTab(self.page1,"Input Page")
        self.tab_widget.addTab(self.page2,"Process Page")
        self.tab_widget.addTab(self.page3,"Synthetise Page")
        
        self.page1.courseSignal.connect(self.page2.audio_slot)
        self.page1.imageSignal.connect(self.page3.image_source_slot)
        self.page1.poseSignal.connect(self.page3.pose_source_slot)
        self.page2.synthetised_audio_signal.connect(self.page3.audio_source_slot)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
