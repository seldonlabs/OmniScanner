"""
EDMC Gui
"""

import Tkinter as tk
from ttkHyperlinkLabel import HyperlinkLabel

from config import config
from theme import theme

from omniconfig import configuration
from cache import cacheDatabase
import inara
import roa


class OmniContainer(tk.Frame):
    """
    Container
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, name="omni_container", pady=5, *args, **kwargs)
        self.pack()
        theme.register(self)


class OmniLabelFrame(tk.LabelFrame):
    """
    Label frame
    """
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, name="omni_label_frame", text="OmniScanner", *args, **kwargs)
        self.pack()
        theme.register(self)


class OmniFrame(tk.Frame):
    """
    General frame config
    """
    def __init__(self, parent, name, *args, **kwargs):
        tk.Frame.__init__(self, parent, name=name, *args, **kwargs)
        self.pack(anchor=tk.NW)
        theme.register(self)


class OmniLabel(tk.Label):
    """
    General label config
    """
    def __init__(self, parent, name, text, *args, **kwargs):
        tk.Label.__init__(self, parent, name=name, text=text, *args, **kwargs)
        self.pack(anchor=tk.W, side=tk.LEFT)
        theme.register(self)


class OmniStatus(OmniLabel):
    """
    Manage gui status
    """
    def __init__(self, parent, *args, **kwargs):
        OmniLabel.__init__(self, parent, name="omni_status", text="Off", *args, **kwargs)

    def set_color(self, color):
        self['fg'] = color

    def set_text(self, text):
        self['text'] = text

    def set_ready(self):
        self['fg'] = "green"
        self['text'] = "Ready"

    def set_querying_msg(self, pilot_name):
        self['fg'] = "orange"
        self['text'] = u"Checking {}".format(pilot_name)

    def set_disabled_on_solo_pvt(self):
        self['fg'] = "red"
        self['text'] = "Disabled in Solo/Private group."

    def set_disabled_on_hp(self):
        self['fg'] = "yellow"
        self['text'] = "Disabled, hardpoints deployed!"

    def set_new_version_message(self, ver):
        self['fg'] = "yellow"
        self['text'] = "New version {} available!".format(ver)

    def set_error(self, errorMsg):
        self['fg'] = "red"
        self['text'] = errorMsg


class OmniCredits(OmniFrame):
    def __init__(self, parent):
        OmniFrame.__init__(self, parent, name="credits")

        self.__label = OmniLabel(self, name="credits_lbl", text="Made by")
        self.__link = HyperlinkLabel(self, text="SeldonLabs", url='https://github.com/seldonlabs/OmniScanner', underline=True)
        theme.register(self.__link)
        self.__link.pack(anchor=tk.NW, side=tk.LEFT)


class OmniLog(tk.OptionMenu):
    def __init__(self, parent, log, **kwargs):
        self._log = log

        self.val = tk.StringVar()
        init_val = log['history'][0]
        self.val.set(init_val)

        tk.OptionMenu.__init__(self, parent, self.val, init_val, *self._log['history'][1:],
                               command=self.__on_option_change, **kwargs)
        self.config(highlightthickness=0)
        self.pack(anchor=tk.W, side=tk.LEFT)
        theme.register(self)

    def __on_option_change(self, event):
        """
        Callback for selection change
        :param event:
        :return:
        """
        self._out.set_output(self._log['log'][event])

    def update_selection_list(self, log):
        """
        Update the selection list
        :param log:
        :return:
        """
        self._log = log
        menu = self["menu"]
        menu.delete(0, "end")

        for i in range(0, len(log['history'])):
            menu.add_command(label=log['history'][i],
                             command=tk._setit(self.val, log['history'][i], self.__on_option_change))

    def set_output_widget(self, out):
        self._out = out


class OmniOutput(tk.Text):
    def __init__(self, parent, *args, **kwargs):
        tk.Text.__init__(self, parent, *args, **kwargs)
        self.pack(padx=2)
        theme.register(self)

        # configure widget from ini
        self.configure(width=configuration.get_gui_layout("width"),
                       height=configuration.get_gui_layout("height"),
                       font=(configuration.get_gui_style("font"),
                             configuration.get_gui_style("size")))
        # set tags from ini
        colors = configuration.get_gui_colors()
        for color_name in colors:
            self.tag_config(color_name, foreground="#{}".format(colors[color_name]))

    def __get_themed_tag(self, tag, theme_id):
        """
        Get a text tag based in the active EDMC theme
        :param tag:
        :param theme_id:
        :return:
        """
        return ("{}_default" if theme_id == 0 else "{}_dark").format(tag)

    def set_output(self, cmdrData):
        """
        Set text output
        :param cmdrData:
        :return:
        """
        self.delete(1.0, tk.END)

        # get EDMC theme id
        theme_id = config.getint('theme')

        # Inara
        inara_data = inara.parse_reply_for_gui(cmdrData['inara'])

        # header
        self.insert(tk.INSERT, "-=Inara=-\n", self.__get_themed_tag("inara_title", theme_id))

        if inara_data:
            info_lines = []
            for line in inara_data:
                # add ranks
                if 'tag' in line:
                    self.insert(tk.INSERT,
                                "[{}]".format(line['text']),
                                self.__get_themed_tag(line['tag'], theme_id))
                # add the rest
                else:
                    info_lines.append(line['text'])

            # print info if lines are appended
            if len(info_lines) > 0:
                self.insert(tk.INSERT, "\n" + "\n".join(info_lines))
        else:
            self.insert(tk.INSERT, "No results", "no_results")

        # Roa
        roa_data = roa.parse_reply_for_gui(cmdrData['roa'])

        # header
        self.insert(tk.INSERT, "\n\n-=ROA=-\n", self.__get_themed_tag("roa_title", theme_id))

        if roa_data:
            for line in roa_data:
                # add KOS and CL lines
                if 'tag' in line:
                    self.insert(tk.INSERT, line['text'] + "\n", line['tag'])
                # add the rest
                else:
                    self.insert(tk.INSERT, line['text'] + "\n")
        else:
            self.insert(tk.INSERT, "No results", "no_results")


class Gui:
    def init_gui(self, parent):
        """
        Init OmniScanner GUI
        :param parent:
        :return:
        """
        # init scan log
        self.__scans = cacheDatabase.get_scans(configuration.get_general("log_len"))

        # container
        container = OmniContainer(parent)

        # label frame
        main_frame = OmniLabelFrame(container)

        # status
        status_frame = OmniFrame(main_frame, name="omni_status")
        OmniLabel(status_frame, "status_label", "Status:")
        self.status = OmniStatus(status_frame)

        # History log
        log_frame = OmniFrame(main_frame, name="omni_log")
        log_frame.configure(pady=4)
        OmniLabel(log_frame, "log_label", "History:")

        # Select box
        self.__omni_log = OmniLog(log_frame, self.__scans)

        # Output
        output_frame = OmniFrame(main_frame, name="omni_output")
        self.__output = OmniOutput(output_frame)

        # TODO: this is ugly, but fuck Tkinter, really...
        self.__omni_log.set_output_widget(self.__output)

        OmniCredits(main_frame)

        # Show last entry on init
        self._show_latest_entry()

        return container

    def update_log(self):
        # update history
        self.__scans = cacheDatabase.get_scans(configuration.get_general("log_len"))
        self.__omni_log.update_selection_list(self.__scans)
        self.__omni_log.val.set(self.__scans['history'][0])

        # show last entry on output
        self._show_latest_entry()

    def _show_latest_entry(self):
        """
        Convenience method for showing last entry on log
        :return:
        """
        latest_entry = self.__scans['history'][0]
        self.__output.set_output(self.__scans['log'][latest_entry])
