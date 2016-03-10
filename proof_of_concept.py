#!/usr/bin/env python3
import os
import sys
import shutil
import tempfile
import logging

import praw
import requests
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QWidget, QPixmap, QLabel
from PyQt4.QtGui import QGraphicsDropShadowEffect, QColor


class ImageGetter():

    def __init__(self, reddit, subreddit='earthporn', aspect_ratio=1.6):
        self.reddit = reddit
        self.subreddit = subreddit
        self.aspect_ratio = aspect_ratio
        self._seen = set()

    def get_image(self, path):
        try:
            subs = self.reddit.get_subreddit(self.subreddit).get_new(limit=50)
            url = self._get_image_url(subs)
            while url is None or url in self._seen:
                url = self._get_image_url(subs)
            self._seen.add(url)
        except StopIteration:
            return None
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            response.raw.decode_content = True
            with open(path, 'wb') as wfh:
                shutil.copyfileobj(response.raw, wfh)
        return path

    def _get_image_url(self, subs):
        next_sub = next(subs)
        images = next_sub.preview.get('images', {})
        for image in images:
            source = image['source']
            image_aspect_ratio = source['width'] / source['height']
            if abs(self.aspect_ratio - image_aspect_ratio) < 0.2:
                return source['url']


class TextGetter():

    def __init__(self, reddit, subreddit='showerthoughts', badlist='bad-words.txt'):
        self.reddit = reddit
        self.subreddit = subreddit
        if badlist:
            with open(badlist) as fh:
                self.bad_words = fh.read().splitlines()
        else:
            self.bad_words = []
        self._seen = set()

    def get_text(self):
        try:
            subs = self.reddit.get_subreddit(self.subreddit).get_new()
            text = None
            while text is None or text in self._seen or 'r/showerthoughts' in text.lower():
                text = next(subs).title
                lower_text = text.lower()
                for bad in self.bad_words:
                    if bad in lower_text:
                        text = None
                        break
            self._seen.add(text)
            return text
        except StopIteration:
            return None


def show_billboard(imagepath, text, fontsize=42):
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(1600, 1000)
    w.setWindowTitle("Billboard")

    pix = QPixmap(imagepath)

    image_label = QLabel(w)
    image_label.resize(1600, 1000)
    image_label.setPixmap(pix.scaled(w.size(), Qt.KeepAspectRatioByExpanding))

    text_label = QLabel(w)
    text_label.resize(1600, 1000)
    text_label.setMargin(100)
    text_label.setText('"{}"'.format(text))
    text_label.setStyleSheet('''
        QLabel {{
                    font-size: {}pt;
                    color: #eeeeee;
                    text-align: center;
                }}
    '''.format(fontsize))
    text_label.setWordWrap(True)
    text_label.setAlignment(Qt.AlignCenter)

    dse = QGraphicsDropShadowEffect()
    dse.setBlurRadius(10)
    dse.setXOffset(0)
    dse.setYOffset(0)
    dse.setColor(QColor(0, 0, 0, 255))
    text_label.setGraphicsEffect(dse)

    w.show()
    app.exec_()


def main():
    reddit = praw.Reddit(user_agent='billboard')
    imagegetter = ImageGetter(reddit)
    textgetter = TextGetter(reddit)

    image_path = tempfile.mktemp()
    if not imagegetter.get_image(image_path):
        logging.error("Did not find a suitable image.")
        sys.exit(1)
    text = textgetter.get_text()
    if not text:
        logging.error("Did not find a suitable text.")
        sys.exit(1)

    show_billboard(image_path, text)
    os.unlink(image_path)


if __name__ == '__main__':
    main()
