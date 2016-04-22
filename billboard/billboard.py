import time
from threading import Thread
from itertools import cycle


class Billboard(Thread):

    def __init__(self, display, sources, period):
        super(Billboard, self).__init__()
        self.display = display
        self.sources = sources
        self.period = period
        self.daemon = True

    def run(self):
        for source in cycle(self.sources):
            image, text = source.next()
            if image is None and text is None:
                continue
            if image is not None:
                self.display.update_image(image)
            if text is not None:
                self.display.display_text(text)
            self.display.update_current()
            time.sleep(self.period)
