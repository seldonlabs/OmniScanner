""""
OverlayManager
"""
import os
import sys
import textwrap

from config import config
from omniconfig import OverlayConfig

import inara
import roa

TTL_CONFIG_KEY = "OmniScannerTTL"
TTL_VALUE_DEFAULT = 8

FLUSH = ' '

roa_template = [ 'Clan', 'Last update', 'Combat Logger', 'on KOS', 'Reason for KOS' ]

class OverlayManager:
    _this_dir = os.path.abspath(os.path.dirname(__file__))
    _overlay_dir = os.path.join(_this_dir, "EDMCOverlay")
    _line_template = u'{}: {}'

    def __init__(self):
        self.config = OverlayConfig()

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
            self._overlay.send_message("omniscanner_{}_{}".format(row, col), text, color, col, row, ttl, size)
        except Exception as e:
            print('Exception sending message to overlay '.format(e))

    def display(self, text, row, col, color, size="normal"):
        self._send_to_socket(text, row, col, color,
                             ttl=config.get(TTL_CONFIG_KEY),
                             size=size)

    def version_message(self, text, color):
        self._send_to_socket(text,
                             row=self.config.get_pos_attr('version_row'),
                             col=self.config.get_pos_attr('version_col'),
                             color=color,
                             ttl=self.config.get_ttl_attr('version_ttl'),
                             size="large")

    def service_message(self, text, color):
        self._send_to_socket(text,
                             row=self.config.get_pos_attr('service_row'),
                             col=self.config.get_pos_attr('service_col'),
                             color=color,
                             ttl=self.config.get_ttl_attr('service_ttl'),
                             size="large")

    def flush(self):
        self.display(FLUSH, self.config.get_pos_attr('sub_header_row'), self.config.get_pos_attr('first_col'), self.config.get_color_attr('text'))
        self.display(FLUSH, self.config.get_pos_attr('detail_row'), self.config.get_pos_attr('first_col'), self.config.get_color_attr('text'))
        self.display(FLUSH, self.config.get_pos_attr('detail_row'), self.config.get_pos_attr('second_col'), self.config.get_color_attr('text'))

    def display_notification(self, text):
        self.display(text,
                     row=self.config.get_pos_attr('header_row'),
                     col=self.config.get_pos_attr('first_col'),
                     color=self.config.get_color_attr('notification'),
                     size="large")

    def display_error(self, text):
        self.display(text,
                     row=self.config.get_pos_attr('detail_row'),
                     col=self.config.get_pos_attr('first_col'),
                     color=self.config.get_color_attr('error'),
                     size="large")

    def display_warning(self, text, col):
        self.display(text,
                     row=self.config.get_pos_attr('detail_row'),
                     col=col,
                     color=self.config.get_color_attr('warning'),
                     size="large")

    def display_cmdr_name(self, text):
        self.display(text,
                     row=self.config.get_pos_attr('header_row'),
                     col=self.config.get_pos_attr('first_col'),
                     color=self.config.get_color_attr('cmdr_name'),
                     size="large")

    def display_role(self, text):
        self.display(text,
                     row=self.config.get_pos_attr('sub_header_row'),
                     col=self.config.get_pos_attr('first_col'),
                     color=self.config.get_color_attr('cmdr_role'))

    def display_section_title(self, title, col):
        self.display(title,
                     row=self.config.get_pos_attr('info_row'),
                     col=col,
                     color=self.config.get_color_attr('sect_title'),
                     size="large")

    def display_section(self, text, col):
        self.display(text,
                     row=self.config.get_pos_attr('detail_row'),
                     col=col,
                     color=self.config.get_color_attr('text'))

    def display_info(self, reply):
        inara_data = inara.parse_reply(reply['inara'])
        roa_data = roa.parse_reply(reply['roa'])

        self.display_section_title("Inara", self.config.get_pos_attr('first_col'))
        self.display_section_title("ROA DB", self.config.get_pos_attr('second_col'))

        if inara_data:
            if 'role' in inara_data:
                self.display_role(inara_data['role'])

            text = '\n'.join(self._format_inara_data(inara_data))

            self.display_section(text, self.config.get_pos_attr('first_col'))
        else:
            self.display_warning('No results', self.config.get_pos_attr('first_col'))

        if roa_data:
            formatted_data = self._format_roa_data(roa_data)

            # Remove 'Clan' if 'wing' is in already in inara
            # 'Clan' is always returned from roa.parse_reply
            # or this will not work
            if inara_data and 'wing' in inara_data:
                text = '\n'.join(formatted_data[1:])
            else:
                text = '\n'.join(formatted_data)

            self.display_section(text, self.config.get_pos_attr('second_col'))
        else:
            self.display_warning('No results', self.config.get_pos_attr('second_col'))

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
