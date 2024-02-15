import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QComboBox, QCheckBox, QInputDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import os
import numpy as np
import matplotlib.pyplot as plt
import io

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.original_image = None
        self.filtered_image = None
        self.original_histogram_label = QLabel(self)
        self.filtered_histogram_label = QLabel(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Filter App')
        self.setGeometry(100, 100, 800, 600)

        self.original_label = QLabel(self)
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setStyleSheet("border: 2px solid black;")
        self.filtered_label = QLabel(self)
        self.filtered_label.setAlignment(Qt.AlignCenter)
        self.filtered_label.setStyleSheet("border: 2px solid black;")

        self.load_button = QPushButton('Load Image', self)
        self.load_button.clicked.connect(self.load_image)

        self.filter_button = QPushButton('Apply Filter', self)
        self.filter_button.clicked.connect(self.apply_filter)

        self.filter_combo = QComboBox(self)
        self.filter_combo.addItem("Original Image")
        self.filter_combo.addItem("Grayscale")
        self.filter_combo.addItem("Edge Detection")
        self.filter_combo.addItem("Negative")
        self.filter_combo.addItem("Log Transformation")
        self.filter_combo.addItem("Gamma Correction")
        self.filter_combo.setFixedWidth(150)

        self.histogram_checkbox = QCheckBox('Show Histogram', self)
        self.histogram_checkbox.stateChanged.connect(self.toggle_histogram)

        hbox = QHBoxLayout()
        hbox.addWidget(self.original_label)
        hbox.addWidget(self.original_histogram_label)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.filtered_label)
        hbox2.addWidget(self.filtered_histogram_label)

        vbox = QVBoxLayout()
        vbox.addWidget(self.histogram_checkbox)
        vbox.addWidget(self.filter_combo)
        vbox.addWidget(self.load_button)
        vbox.addWidget(self.filter_button)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

    def load_image(self):
        pictures_path = os.path.join(os.path.expanduser("~"), "Pictures")
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image', pictures_path, 'Image Files (*.png *.jpg *.jpeg *.bmp)')

        if file_name:
            self.original_image = cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.display_image(self.original_image, self.original_label)

    def apply_filter(self):
        if self.original_image is None:
            return
        else:
            selected_filter = self.filter_combo.currentText()
            if selected_filter == "Original Image":
                self.filtered_image = self.original_image
            elif selected_filter == "Grayscale":
                self.filtered_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            elif selected_filter == "Edge Detection":
                self.filtered_image = cv2.Canny(self.original_image, 100, 200)
            elif selected_filter == "Negative":
                grayscale_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
                self.filtered_image = 255 - grayscale_img
            elif selected_filter == "Log Transformation":
                c, ok = QInputDialog.getDouble(self, 'Log Transformation', 'Enter the value of c (1-255):')
                if ok:
                    grayscale_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
                    grayscale_img = np.clip(grayscale_img, 0, 255)
                    self.filtered_image = c * np.log1p(grayscale_img + 1e-6)
            elif selected_filter == "Gamma Correction":
                gamma, ok = QInputDialog.getDouble(self, 'Gamma Correction', 'Enter the value of gamma:')
                if ok:
                    lookup_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in np.arange(0, 256)]).astype("uint8")
                    gamma_corrected_image = cv2.LUT(self.original_image, lookup_table)
                    self.filtered_image = gamma_corrected_image
                else:
                    self.filtered_image = self.original_image

            self.display_image(self.filtered_image, self.filtered_label)
            if self.histogram_checkbox.isChecked():
                self.display_histogram(self.original_image, self.original_histogram_label)
                self.display_histogram(self.filtered_image, self.filtered_histogram_label)

    def toggle_histogram(self, state):
        if state == Qt.Checked:
            self.display_histogram(self.original_image, self.original_histogram_label)
            self.display_histogram(self.filtered_image, self.filtered_histogram_label)
        else:
            self.original_histogram_label.clear()
            self.filtered_histogram_label.clear()

    def display_histogram(self, image, label):
        if image is None:
            return
        BGR_format= cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        gray_image = cv2.cvtColor(BGR_format, cv2.COLOR_BGR2GRAY)
        # Calculate histogram
        histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

        # Plot histogram with dark colors
        plt.figure(figsize=(4, 3))
        plt.title('Histogram')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.plot(histogram, color='black')
        plt.xlim([0, 256])  # Set x-axis range to [0, 255]
        plt.grid(True, color='black', linestyle='--', linewidth=0.5)  # Dark gridlines

        # Render the plot
        plt.tight_layout()
        plt.draw()

        # Save histogram plot to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Convert image to QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())

        # Set pixmap to label
        label.setPixmap(pixmap)



    def display_image(self, image, label):
        if len(image.shape) == 3:  # Color image
            height, width, _ = image.shape
        else:  # Grayscale image
            height, width = image.shape

        # Get the size of the label
        label_width = label.width()
        label_height = label.height()

        # Calculate scaling factors
        scale_width = label_width / width
        scale_height = label_height / height

        # Choose the smaller scaling factor to fit the image into the label
        scale_factor = min(scale_width, scale_height)

        # Resize the image
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        if len(image.shape) == 3:  # Color image
            resized_image = cv2.resize(image, (new_width, new_height))
            bytes_per_line = 3 * new_width
            q_img = QImage(resized_image.data, new_width, new_height, bytes_per_line, QImage.Format_RGB888)
        else:  # Grayscale image
            resized_image = cv2.resize(image, (new_width, new_height))
            bytes_per_line = new_width
            q_img = QImage(resized_image.data, new_width, new_height, bytes_per_line, QImage.Format_Grayscale8)

        q_pix_map = QPixmap.fromImage(q_img)
        label.setPixmap(q_pix_map)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec_())
