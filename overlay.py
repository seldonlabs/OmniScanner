""""
OverlayManager
"""
import os
import sys

from config import config

from inara import parse_inara_reply
from roa import parse_roa_reply

TTL_CONFIG_KEY = "EdCmdrInfoTimeToLive"
TTL_VALUE_DEFAULT = 8

HEADER = 380
INFO = 420
DETAIL = 420
COL_PAD = 160
COL1 = 95
COL2 = COL1 + COL_PAD
LINE_PAD = 25
DETAIL1 = INFO + LINE_PAD
DETAIL2 = DETAIL1 + LINE_PAD
DETAIL3 = DETAIL2 + LINE_PAD
FLUSH = ' '


class OverlayManager:
    _this_dir = os.path.abspath(os.path.dirname(__file__))
    _overlay_dir = os.path.join(_this_dir, "EDMCOverlay")
    _overlay = None
    _line_template = u'{}: {}'

    def __init__(self):
        if self._overlay_dir not in sys.path:
            print("adding {} to sys.path".format(self._overlay_dir))
            sys.path.append(self._overlay_dir)

        try:
            import edmcoverlay
        except ImportError:
            print(sys.path)
            self._overlay = None
            raise Exception(str(sys.path))

        self._overlay = edmcoverlay.Overlay()

    def _send_to_socket(self, text, row, col, color, ttl, size):
        try:
            self._overlay.send_message("edcmdrinfo_{}_{}".format(row, col),
                                       text,
                                       color,
                                       col, row,
                                       ttl=ttl,
                                       size=size)
        except Exception as e:
            print('Exception sending message to overlay '.format(e))

    def display(self, text, row, col, color="yellow", size="normal"):
        self._send_to_socket(text, row, col, color, config.get(TTL_CONFIG_KEY), size)

    def service_message(self, text, color):
        self._send_to_socket(text, HEADER, COL1, color, ttl=2, size="large")

    def flush(self):
        # unnecessary (maybe)
        # self.display_cmdr_name(FLUSH)

        self.display(FLUSH, DETAIL1, COL1)
        self.display(FLUSH, DETAIL1, COL2)

        # unnecessary (maybe)
        """
        self.display_sect_title(FLUSH, COL1)
        self.display_sect_title(FLUSH, COL2)
        
        self.warning(FLUSH, COL1)
        self.warning(FLUSH, COL2)
        """

    def notify(self, text):
        self.display(text, row=HEADER, color="#00ff00", col=COL1, size="large")

    def display_cmdr_name(self, text):
        self.display(text,
                     row=HEADER,
                     col=COL1,
                     size="large")

    def error(self, text):
        self.display(text,
                     row=DETAIL1,
                     color="red",
                     col=COL1,
                     size="large")

    def warning(self, text, col):
        self.display(text,
                     row=DETAIL1,
                     color="red",
                     col=col,
                     size="large")

    def display_sect_title(self, title, col):
        self.display(title,
                     row=INFO,
                     color="#00ff00",
                     col=col,
                     size="large")

    def display_info(self, reply):
        cmdr_data = parse_inara_reply(reply['inara'])
        roa_data = parse_roa_reply(reply['roa'])

        self.display_inara_info(cmdr_data)
        self.display_roa_info(roa_data)

    def display_inara_info(self, cmdrData):
        self.display_sect_title("Inara", COL1)

        if cmdrData:
            base = cmdrData['base']

            lines = []

            for key in base:
                lines.append(self._line_template.format(key, base[key]))

            for i, (label, value) in enumerate(cmdrData['rank'].items()):
                lines.append(self._line_template.format(label, value))

            if 'wing' in cmdrData:
                for i, (label, value) in enumerate(cmdrData['wing'].items()):
                    lines.append(self._line_template.format(label, value))

            text = '\n'.join(lines)

            self.display(text, row=DETAIL1, col=COL1)
        else:
            self.warning('No results', COL1)

    def display_roa_info(self, data):
        self.display_sect_title("ROA DB", COL2)

        if data:
            lines = []

            for label in data:
                lines.append(self._line_template.format(label, data[label]))

            text = '\n'.join(lines)

            self.display(text, row=DETAIL1, col=COL2)
        else:
            self.warning('No results', COL2)
