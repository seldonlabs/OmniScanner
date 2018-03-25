""""
OverlayManager
"""
import os
import sys

from config import config
from inara import parse_inara_reply

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


def _bool_to_str(boolVal):
    return 'YES' if boolVal else 'NO'


class OverlayManager:
    _this_dir = os.path.abspath(os.path.dirname(__file__))
    _overlay_dir = os.path.join(_this_dir, "EDMCOverlay")
    _overlay = None
    _ttl = 8

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

    def set_ttl(self, ttl):
        self._ttl = ttl

    def display(self, text, row, col, color="yellow", size="normal"):
        try:
            self._overlay.send_message("edcmdrinfo_{}_{}".format(row, col),
                                       text,
                                       color,
                                       col, row,
                                       ttl=self._ttl,
                                       size=size)
        except Exception as e:
            print('Exception sending message to overlay '.format(e))

    def flush_line(self, row, co1):
        self.display(FLUSH, DETAIL + (row * LINE_PAD), co1)

    def flush(self):
        self.display_cmdr_name(FLUSH)

        self.display_sect_title(FLUSH, COL1)
        self.display_sect_title(FLUSH, COL2)

        self.warning(FLUSH, COL1)
        self.warning(FLUSH, COL2)

        for i in range(12):
            self.flush_line(i, COL1)

        for i in range(4):
            self.flush_line(i, COL2)

    def notify(self, text):
        self.display(text, row=HEADER, color="#00ff00", col=COL1, size="large")

    def display_cmdr_name(self, text):
        self.display(text,
                     row=HEADER,
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

    def display_line_at(self, label, value, i, col):
        self.display(u'{}: {}'.format(label, value),
                     row=DETAIL + (i * LINE_PAD),
                     col=col)

    def display_info(self, reply):
        cmdr_data = parse_inara_reply(reply['inara'])
        roa_data = reply['roa']

        self.display_inara_info(cmdr_data)
        self.display_roa_info(roa_data)

    def display_inara_info(self, cmdrData):
        self.display_sect_title("Inara", COL1)

        if cmdrData:
            base = cmdrData['base']

            if 'Role' in base:
                self.display_line_at('Role', base['Role'], 1, COL1)

            if 'Allegiance' in base:
                self.display_line_at('Allegiance', base['Allegiance'], 2, COL1)

            if 'Power' in base:
                self.display_line_at('Power', base['Power'], 3, COL1)

            rank_line = 4

            for i, (label, value) in enumerate(cmdrData['rank'].items()):
                self.display_line_at(label, value, rank_line + i, COL1)

            if 'wing' in cmdrData:
                wing_line = 10

                for i, (label, value) in enumerate(cmdrData['wing'].items()):
                    self.display_line_at(label, value, wing_line + i, COL1)
        else:
            self.warning('No results', COL1)

    def display_roa_info(self, data):
        self.display_sect_title("ROA DB", COL2)

        cmdrData = data['cmdrData']

        if cmdrData:
            self.display_line_at('Clan', cmdrData['Clan'], 1, COL2)
            self.display_line_at('Combat logger', _bool_to_str(cmdrData['isClogger']), 2, COL2)

            isKOS = cmdrData['isKOS']
            self.display_line_at('KOS', _bool_to_str(isKOS), 3, COL2)

            if isKOS:
                self.display_line_at('KOS info', cmdrData['KOSdesc'], 4, COL2)
        else:
            self.warning('No results', COL2)
