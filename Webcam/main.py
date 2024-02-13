import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Webcam Application")
        self.setMinimumSize(700, 480)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setPixmap(QPixmap())  # Set an initial blank pixmap

        self.camera_combobox = QComboBox(self)
        self.camera_combobox.currentIndexChanged.connect(self.change_camera)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_webcam)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_webcam)
        self.stop_button.setEnabled(False)

        self.grayscale_checkbox = QCheckBox("Grayscale", self)
        self.grayscale_checkbox.stateChanged.connect(self.toggle_grayscale)
        self.grayscale_checkbox.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.grayscale_checkbox)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.camera_combobox)
        control_layout.addLayout(button_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.video_label)

        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.camera = None
        self.grayscale = False

        self.refresh_camera_list()

    def refresh_camera_list(self):
        self.camera_combobox.clear()
        num_cameras = 5  # Adjust this number based on the maximum number of cameras expected
        for i in range(num_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_combobox.addItem(f"Camera {i}")
            cap.release()

    def start_webcam(self):
        index = self.camera_combobox.currentIndex()
        self.camera = cv2.VideoCapture(index)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.grayscale_checkbox.setEnabled(True)
        self.timer.start(30)

    def stop_webcam(self):
        if self.camera is not None:
            self.camera.release()
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.grayscale_checkbox.setEnabled(False)
            self.video_label.clear()

    def toggle_grayscale(self):
        self.grayscale = self.grayscale_checkbox.isChecked()

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            if self.grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)  # Flip horizontally
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio))

    def change_camera(self, index):
        if self.camera is not None:
            self.camera.release()
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.grayscale_checkbox.setEnabled(False)
            self.video_label.clear()
        self.start_webcam()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamApp()
    window.show()
    sys.exit(app.exec_())
