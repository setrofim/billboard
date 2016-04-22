import os
import logging

from PyQt4.QtCore import Qt, QObject, SIGNAL
from PyQt4.QtGui import (QMainWindow, QWidget, QPixmap, QLabel,
                         QGraphicsDropShadowEffect, QColor,
                         QDesktopWidget)


class BillboardDisplay(QMainWindow):

    def __init__(self, parent=None, workdir=None, fontsize=42):
        super(BillboardDisplay, self).__init__(parent)
        self.workdir = workdir
        self.logger = logging.getLogger('display')
        self.logger.info('Working directory: {}'.format(self.workdir))
        self.current_display = os.path.join(self.workdir, 'current.jpg')
        desktop = QDesktopWidget()
        self.display = QWidget(self)
        size  = desktop.availableGeometry(desktop.primaryScreen());
        self.display.resize(size.width(), size.height())
        self.display.setWindowTitle("Billboard")

        self.image_label = QLabel(self.display)
        self.image_label.resize(size.width(), size.height())

        self.text_label = QLabel(self.display)
        self.text_label.resize(size.width(), size.height())
        self.text_label.setMargin(100)
        self.text_label.setStyleSheet('''
            QLabel {{
                        font-size: {}pt;
                        font-weight: bold;
                        color: #eeeeee;
                        text-align: center;
                    }}
        '''.format(fontsize))
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignCenter)

        dse = QGraphicsDropShadowEffect()
        dse.setBlurRadius(0)
        dse.setXOffset(5)
        dse.setYOffset(5)
        dse.setColor(QColor(0, 0, 0, 255))
        self.text_label.setGraphicsEffect(dse)
        QObject.connect(self, SIGNAL("updateimage"),
                        self.display_image)
        QObject.connect(self, SIGNAL("updatecurrent"),
                        self.take_screenshot)

    def update_image(self, imagepath):
        self.emit(SIGNAL("updateimage"), imagepath)

    def update_current(self):
        self.emit(SIGNAL("updatecurrent"), self.current_display)

    def display(self, imagepath, text):
        self.display_text(text)
        self.display_image(imagepath)
        self.showFullScreen()

    def display_image(self, imagepath):
        pix = QPixmap(imagepath)
        self.image_label.setPixmap(pix.scaled(self.display.size(),
                                              Qt.KeepAspectRatioByExpanding))

    def display_text(self, text):
        self.text_label.setText('"{}"'.format(text))

    def take_screenshot(self, path):
        pixmap = QPixmap(QPixmap.grabWidget(self.display))
        pixmap.save(path)
        self.logger.debug('Saving {}'.format(path))

