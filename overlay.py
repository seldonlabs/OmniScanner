""""
OverlayManager
"""
import os
import sys
import textwrap

from config import config

import inara
import roa

TTL_CONFIG_KEY = "OmniScannerTTL"
TTL_VALUE_DEFAULT = 8

HEADER = 380
SUB_HEADER = 400
INFO = 420
DETAIL = 420

COL_PAD = 150
COL1 = 95
COL2 = COL1 + COL_PAD

LINE_PAD = 25
DETAIL1 = INFO + LINE_PAD
DETAIL2 = DETAIL1 + LINE_PAD
DETAIL3 = DETAIL2 + LINE_PAD

FLUSH = ' '

RED = "#ff0000"
GREEN = "#00ff00"
BLU = "#0000ff"

DEFAULT_COLOR = "yellow"

roa_template = [ 'Clan', 'Last update', 'Combat Logger', 'on KOS', 'Reason for KOS' ]

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
            self._overlay.send_message("omniscanner_{}_{}".format(row, col),
                                       text,
                                       color,
                                       col, row,
                                       ttl=ttl,
                                       size=size)
        except Exception as e:
            print('Exception sending message to overlay '.format(e))

    def display(self, text, row, col, color=DEFAULT_COLOR, size="normal"):
        self._send_to_socket(text,
                             row,
                             col,
                             color,
                             config.get(TTL_CONFIG_KEY),
                             size)

    def service_message(self, text, color):
        self._send_to_socket(text,
                             HEADER,
                             COL1,
                             color,
                             ttl=2,
                             size="large")

    def flush(self):
        # unnecessary (maybe)
        # self.display_cmdr_name(FLUSH)

        self.display(FLUSH, SUB_HEADER, COL1)
        self.display(FLUSH, DETAIL1, COL1)
        self.display(FLUSH, DETAIL1, COL2)

        # unnecessary (maybe)
        """
        self.display_sect_title(FLUSH, COL1)
        self.display_sect_title(FLUSH, COL2)
        
        self.display_warning(FLUSH, COL1)
        self.display_warning(FLUSH, COL2)
        """

    def display_notification(self, text):
        self.display(text,
                     row=HEADER,
                     color=GREEN,
                     col=COL1,
                     size="large")

    def display_error(self, text):
        self.display(text,
                     row=DETAIL1,
                     color=RED,
                     col=COL1,
                     size="large")

    def display_warning(self, text, col):
        self.display(text,
                     row=DETAIL1,
                     color=RED,
                     col=col,
                     size="large")

    def display_cmdr_name(self, text):
        self.display(text,
                     row=HEADER,
                     col=COL1,
                     size="large")

    def display_role(self, text):
        self.display(text,
                     row=SUB_HEADER,
                     col=COL1)

    def display_section_title(self, title, col):
        self.display(title,
                     row=INFO,
                     color=GREEN,
                     col=col,
                     size="large")

    def display_info(self, reply):
        inara_data = inara.parse_reply(reply['inara'])
        roa_data = roa.parse_reply(reply['roa'])

        self.display_section_title("Inara", COL1)
        self.display_section_title("ROA DB", COL2)

        if inara_data:
            if 'role' in inara_data:
                self.display_role(inara_data['role'])

            text = '\n'.join(self._format_inara_data(inara_data))

            self.display(text,
                         row=DETAIL1,
                         col=COL1)
        else:
            self.display_warning('No results', COL1)

        if roa_data:
            formatted_data = self._format_roa_data(roa_data)

            # Remove 'Clan' if 'wing' is in already in inara
            # 'Clan' is always returned from roa.parse_reply
            # or this will not work
            if inara_data and 'wing' in inara_data:
                text = '\n'.join(formatted_data[1:])
            else:
                text = '\n'.join(formatted_data)

            self.display(text,
                         row=DETAIL1,
                         col=COL2)
        else:
            self.display_warning('No results', COL2)

    def _format_inara_data(self, data):
        lines = []

        if 'wing' in data:
            for i, (label, value) in enumerate(data['wing'].items()):
                lines.append(self._line_template.format(label, value))

        for key in data['base']:
            lines.append(self._line_template.format(key, data['base'][key]))

        for i, (label, value) in enumerate(data['rank'].items()):
            lines.append(self._line_template.format(label, value))

        return lines

    def _format_roa_data(self, data):
        lines = []

        for label in roa_template:
            if label in data:
                if label == "Reason for KOS":
                    lines.append('\n{}: \n{}'.format(label, textwrap.fill(data[label], 20)))
                else:
                    lines.append(self._line_template.format(label, data[label]))

        return lines
