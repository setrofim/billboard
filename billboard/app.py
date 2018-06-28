import os
import sys
import argparse
import signal
import tempfile
import logging
import queue

from PyQt4.QtGui import QApplication

from billboard.billboard import Billboard
from billboard.display import BillboardDisplay
from billboard.server import Server
from billboard.sources.reddit import RedditSource


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--period', type=int, default=60*15,
                        help='''
                        Period for switching billboard display in seconds.
                        Defaults to 15 minutes.
                        ''')
    parser.add_argument('-d', '--working-directory',
                        help='''
                        Working directory used by billboard. If not specified,
                        a temporary directory will be created.
                        ''')
    parser.add_argument('-P', '--port', type=int, default=5555,
                        help='''
                        Port to be used by the server.
                        ''')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args(sys.argv[1:])


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    args = parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)s: %(message)s', level=level)
    app = QApplication(sys.argv)

    workdir = os.path.abspath(args.working_directory or tempfile.mktemp())
    if not os.path.isdir(workdir):
        logging.debug('Creating {}'.format(workdir))
        os.makedirs(workdir)

    # We use a queue to communicate between threads
    q = queue.Queue()

    server = Server(workdir, args.port, q)
    display = BillboardDisplay(workdir=workdir)
    sources = [RedditSource()]

    billboard = Billboard(display, sources, args.period, q)

    billboard.start()
    display.showFullScreen()
    server.start()
    app.exec_()


if __name__ == '__main__':
    main()

