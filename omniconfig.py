"""
Configuration
"""

import os
import ConfigParser
import Tkinter as tk

from config import config

DISABLE_ED_TIME_KEY = "OmniScannerDisableEDTime"
DISABLE_ED_TIME_FIELD = tk.IntVar(value=config.get(DISABLE_ED_TIME_KEY))

ENABLE_OVERLAY_KEY = "OmniScannerEnableOverlay"
ENABLE_OVERLAY_FIELD = tk.IntVar(value=config.get(ENABLE_OVERLAY_KEY))

TTL_CONFIG_KEY = "OmniScannerTTL"
TTL_VALUE_DEFAULT = 4
TTL_FIELD = tk.StringVar(value=config.get(TTL_CONFIG_KEY))

DISABLE_SERVICE_MSG_KEY = "OmniScannerDisableSrvMsgs"
DISABLE_SERVICE_MSG_FIELD = tk.IntVar(value=config.get(DISABLE_SERVICE_MSG_KEY))


class Config:
    _this_dir = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, config_file):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read(os.path.join(self._this_dir, config_file))

    def get_url(self, url_name):
        r = self.conf.get("general", url_name)
        return "".join([chr((-100) + int(r[i:i + 3]) - 10) for i in range(0, len(r), 3)])

    def get_general(self, attr):
        return self.conf.get("general", attr)

    def get_gui_layout(self, attr):
        return self.conf.getint("gui-layout", attr)

    def get_gui_style(self, attr):
        return self.conf.get("gui-style", attr)

    def get_gui_colors(self):
        return dict(self.conf.items("gui-colors"))

    def get_overlay_layout(self, attr):
        return self.conf.getint('overlay-layout', attr)

    def get_overlay_color(self, attr):
        return '#{}'.format(self.conf.get('overlay-colors', attr))

    def get_overlay_pad(self, attr):
        return self.conf.getint('overlay-pad', attr)

    def get_overlay_ttl(self, attr):
        return self.conf.getint('overlay-ttl', attr)


configuration = Config("omniscanner.ini")
