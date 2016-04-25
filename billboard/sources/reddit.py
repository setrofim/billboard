import os
import sys
import shutil
import tempfile
import logging
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import praw

import requests

from billboard.utils import DroppingSet


IMG_MAX_SIZE = 2000


class ImageGetter:

    def __init__(self, reddit, subreddit='earthporn', aspect_ratio=1.6):
        self.reddit = reddit
        self.subreddit = subreddit
        self.aspect_ratio = aspect_ratio
        self._seen = DroppingSet(50)

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
        preview = getattr(next_sub, 'preview', None)
        if not preview:
            return None
        images = preview.get('images', {})
        for image in images:
            source = image['source']
            image_aspect_ratio = source['width'] / source['height']
            if int(source['width']) > IMG_MAX_SIZE or int(source['height']) > IMG_MAX_SIZE:
                continue
            if abs(self.aspect_ratio - image_aspect_ratio) < 0.2:
                return source['url']


class TextGetter:

    def __init__(self, reddit, subreddit='showerthoughts', badlist='bad-words.txt'):
        self.reddit = reddit
        self.subreddit = subreddit
        if badlist:
            with open(badlist) as fh:
                self.bad_words = fh.read().splitlines()
        else:
            self.bad_words = []
        self._seen = DroppingSet(50)

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


class RedditSource:

    def __init__(self):
        self.reddit = praw.Reddit(user_agent='billboard')
        self.imagegetter = ImageGetter(self.reddit)
        badlist = os.path.join(os.path.dirname(__file__), 'bad-words.txt')
        self.textgetter = TextGetter(self.reddit, badlist=badlist)
        self.image_path = tempfile.mktemp()
        self.logger = logging.getLogger('reddit')

    def next(self):
        if not self.imagegetter.get_image(self.image_path):
            self.logger.error("Did not find a suitable image.")
        text = self.textgetter.get_text()
        if not text:
            self.logger.error("Did not find a suitable text.")
        return self.image_path, text
