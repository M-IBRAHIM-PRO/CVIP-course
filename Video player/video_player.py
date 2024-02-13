import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout, QSlider, QAction, QMenu
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.video_frame = cv2.VideoCapture()
        self.timer = QTimer(self)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setToolTip("Browse video")
        self.browse_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton()
        self.pause_button.setToolTip("Play / Pause ")
        self.pause_button.setIcon(QIcon("pause_icon.png"))
        self.pause_button.clicked.connect(self.pause_video)

        self.skip_backward_button = QPushButton("-5s")
        self.skip_backward_button.clicked.connect(self.skip_backward)

        self.skip_forward_button = QPushButton("+5s")
        self.skip_forward_button.clicked.connect(self.skip_forward)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.speed_slider.setFixedWidth(100)  # Set fixed width for the slider

        self.speed_label = QLabel("Speed")
        self.speed_label.setToolTip("Adjust playback speed")
        self.speed_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)

        self.control_layout = QHBoxLayout()
        self.layout.addLayout(self.control_layout)

        self.control_layout.addWidget(self.browse_button)
        self.control_layout.addStretch(1)
        self.control_layout.addWidget(self.skip_backward_button)
        self.control_layout.addWidget(self.pause_button)
        self.control_layout.addWidget(self.skip_forward_button)
        self.control_layout.addStretch(1)  # Add a stretchable space to push the slider to the right
        self.control_layout.addWidget(self.speed_label)
        self.control_layout.addWidget(self.speed_slider)

        self.create_menu()

        # self.play_video()

    def create_menu(self):
        menu_bar = self.menuBar()
        filters_menu = menu_bar.addMenu("Apply Filters")

        grayscale_action = QAction("Grayscale", self)
        grayscale_action.triggered.connect(lambda: self.apply_filter("grayscale"))
        filters_menu.addAction(grayscale_action)

        colored_action = QAction("Colored", self)
        colored_action.triggered.connect(lambda: self.apply_filter("colored"))
        filters_menu.addAction(colored_action)

    def apply_filter(self, filter_type):
        if filter_type == "grayscale":
            self.convert_to_grayscale = True
        elif filter_type == "colored":
            self.convert_to_grayscale = False

    def play_video(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if filepath:
            self.video_frame.open(filepath)
            self.timer.timeout.connect(self.next_frame)
            self.timer.start(33)  # Update every 33 milliseconds (30 fps)

    def next_frame(self):
        ret, frame = self.video_frame.read()
        if ret:
            if hasattr(self, 'convert_to_grayscale') and self.convert_to_grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888))
            self.video_label.setPixmap(image)
        else:
            self.timer.stop()

    def pause_video(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(33)

    def skip_backward(self):
        current_position = self.video_frame.get(cv2.CAP_PROP_POS_MSEC)
        self.video_frame.set(cv2.CAP_PROP_POS_MSEC, max(0, current_position - 5000))  # Subtract 5 seconds (5000 milliseconds)

    def skip_forward(self):
        current_position = self.video_frame.get(cv2.CAP_PROP_POS_MSEC)
        self.video_frame.set(cv2.CAP_PROP_POS_MSEC, current_position + 5000)  # Add 5 seconds (5000 milliseconds)

    def change_speed(self, value):
        speed = value / 50.0  # Map slider value to speed (1x to 2x)
        self.timer.setInterval(int(33 / speed))  # Adjust timer interval based on speed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
