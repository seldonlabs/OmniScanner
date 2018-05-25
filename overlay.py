""""
Overlay manager
"""

from config import config

import omniconfig
import omniutils as ou
from omniconfig import configuration as oc
import inara
import roa

FLUSH = " "


class OverlayManager:
    _line_template = u"{}: {}"

    def __init__(self, overlay_instance):
        self._overlay = overlay_instance

    def __send_to_socket(self, text, row, col, color, ttl, size):
        try:
            self._overlay.send_message("omniscanner_{}_{}".format(row, col), text, color, col, row, ttl, size)
        except Exception as e:
            ou.warn("Exception sending message to overlay: {}".format(e))

    def display(self, text, row, col, color, size="normal"):
        self.__send_to_socket(text, row, col, color,
                              ttl=config.get(omniconfig.TTL_CONFIG_KEY),
                              size=size)

    def version_message(self, text, color):
        self.__send_to_socket(text,
                              row=oc.get_overlay_layout("version_row"),
                              col=oc.get_overlay_layout("version_col"),
                              color=color,
                              ttl=oc.get_overlay_ttl("version_ttl"),
                              size="large")

    def service_message(self, text, color):
        self.__send_to_socket(text,
                              row=oc.get_overlay_layout("service_row"),
                              col=oc.get_overlay_layout("service_col"),
                              color=color,
                              ttl=oc.get_overlay_ttl("service_ttl"),
                              size="large")

    def flush(self):
        """
        Try to flush the overlay with empty lines
        :return:
        """
        self.display(FLUSH,
                     oc.get_overlay_layout("sub_header_row"),
                     oc.get_overlay_layout("first_col"),
                     oc.get_overlay_color("text"))
        self.display(FLUSH,
                     oc.get_overlay_layout("detail_row"),
                     oc.get_overlay_layout("first_col"),
                     oc.get_overlay_color("text"))
        self.display(FLUSH,
                     oc.get_overlay_layout("detail_row"),
                     oc.get_overlay_layout("second_col"),
                     oc.get_overlay_color("text"))

    def display_notification(self, text):
        self.display(text,
                     row=oc.get_overlay_layout("header_row"),
                     col=oc.get_overlay_layout("first_col"),
                     color=oc.get_overlay_color("notification"),
                     size="large")

    def display_error(self, text):
        self.display(text,
                     row=oc.get_overlay_layout("detail_row"),
                     col=oc.get_overlay_layout("first_col"),
                     color=oc.get_overlay_color("error"),
                     size="large")

    def display_warning(self, text, col):
        self.display(text,
                     row=oc.get_overlay_layout("detail_row"),
                     col=col,
                     color=oc.get_overlay_color("warning"),
                     size="large")

    def display_cmdr_name(self, text):
        self.display(text,
                     row=oc.get_overlay_layout("header_row"),
                     col=oc.get_overlay_layout("first_col"),
                     color=oc.get_overlay_color("cmdr_name"),
                     size="large")

    def _display_role(self, text):
        self.display(text,
                     row=oc.get_overlay_layout("sub_header_row"),
                     col=oc.get_overlay_layout("first_col"),
                     color=oc.get_overlay_color("cmdr_role"))

    def _display_section_header(self, title, col):
        self.display(title,
                     row=oc.get_overlay_layout("info_row"),
                     col=col,
                     color=oc.get_overlay_color("sect_title"),
                     size="large")

    def _display_section(self, text, col):
        self.display(text,
                     row=oc.get_overlay_layout("detail_row"),
                     col=col,
                     color=oc.get_overlay_color("text"))

    def display_info(self, pilot_name, cmdrData):
        """
        Display an entry
        :param pilot_name:
        :param cmdrData:
        :return:
        """

        # Display cmdr name
        self.display_cmdr_name(pilot_name)

        # Display section headers
        self._display_section_header("Inara", oc.get_overlay_layout("first_col"))
        self._display_section_header("ROA DB", oc.get_overlay_layout("second_col"))

        # Inara
        inara_data = inara.parse_reply_for_overlay(cmdrData['inara'])

        if inara_data:
            if 'role' in inara_data:
                self._display_role(inara_data['role'])

            lines = []

            if 'wing' in inara_data:
                for line in inara_data['wing']:
                    lines.append(line)

            for line in inara_data['base']:
                lines.append(line)

            for line in inara_data['rank']:
                lines.append(line)

            text = "\n".join(lines)

            self._display_section(text, oc.get_overlay_layout("first_col"))
        else:
            self.display_warning("No results", oc.get_overlay_layout("first_col"))

        roa_data = roa.parse_reply_for_overlay(cmdrData['roa'])

        if roa_data:
            # Remove 'Clan' if 'wing' is in already in inara
            # 'Clan' is always returned from roa.parse_reply
            # or this will not work
            if inara_data and 'wing' in inara_data:
                text = "\n".join(roa_data[1:])
            else:
                text = "\n".join(roa_data)

            self._display_section(text, oc.get_overlay_layout("second_col"))
        else:
            self.display_warning("No results", oc.get_overlay_layout("second_col"))

    def shutdown(self):
        self._overlay.send_raw({
            "command": "exit"
        })
