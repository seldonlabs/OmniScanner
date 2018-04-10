import os
import ConfigParser


class Config:
    _this_dir = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser.ConfigParser()

        self.config.read(os.path.join(self._this_dir, self.config_file))


class OverlayConfig(Config):
    def __init__(self):
        Config.__init__(self, "overlay.ini")

    def get_pos_attr(self, attr):
        return self.config.getint('pos', attr)

    def get_color_attr(self, attr):
        return '#{}'.format(self.config.get('colors', attr))

    def get_pad_attr(self, attr):
        return self.config.getint('pad', attr)

    def get_ttl_attr(self, attr):
        return self.config.getint('ttl', attr)