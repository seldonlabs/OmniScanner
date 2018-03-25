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


roa_labels = {
    'Clan': 'Member of',
    'isClogger': 'Combat Logger',
    'isKOS': 'on KOS',
    'KOSdesc': 'KOS reason'
}


def _bool_to_str(boolVal):
    return 'YES' if boolVal else 'NO'


class OverlayManager:
    _this_dir = os.path.abspath(os.path.dirname(__file__))
    _overlay_dir = os.path.join(_this_dir, "EDMCOverlay")
    _overlay = None
    _line_template = u'{}: {}'
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

    def flush(self):
        # unnecessary (maybe)
        #self.display_cmdr_name(FLUSH)

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
        roa_data = reply['roa']

        self.display_inara_info(cmdr_data)
        self.display_roa_info(roa_data)


    def display_inara_info(self, cmdrData):
        self.display_sect_title("Inara", COL1)

        if cmdrData:
            base = cmdrData['base']

            data = []

            for key in base:
                data.append(self._line_template.format(key, base[key]))

            for i, (label, value) in enumerate(cmdrData['rank'].items()):
                data.append(self._line_template.format(label, value))

            if 'wing' in cmdrData:
                for i, (label, value) in enumerate(cmdrData['wing'].items()):
                    data.append(self._line_template.format(label, value))

            text = '\n'.join(data)

            self.display(text, row=DETAIL1, col=COL1)
        else:
            self.warning('No results', COL1)

    def display_roa_info(self, data):
        self.display_sect_title("ROA DB", COL2)

        cmdrData = data['cmdrData']

        if cmdrData:

            data = []

            for key in cmdrData:
                if key == 'onKOS' or key == 'isClogger':
                    data.append(self._line_template.format(roa_labels[key], _bool_to_str(cmdrData[key])))
                else:
                    data.append(self._line_template.format(roa_labels[key], cmdrData[key]))

            text = '\n'.join(data)

            self.display(text, row=DETAIL1, col=COL2)
        else:
            self.warning('No results', COL2)
