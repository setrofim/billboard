import sys
import argparse

from PyQt4.QtGui import QApplication

from billboard.billboard import Billboard
from billboard.display import BillboardDisplay
from billboard.sources.reddit import RedditSource


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--period', type=int, default=60*15,
                        help='''
                        Period for switching billboard display in seconds.
                        Defaults to 15 minutes.
                        ''')
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_args()
    app = QApplication(sys.argv)

    display = BillboardDisplay()
    sources = [RedditSource()]

    billboard = Billboard(display, sources, args.period)

    billboard.start()
    display.show()
    app.exec_()


if __name__ == '__main__':
    main()

