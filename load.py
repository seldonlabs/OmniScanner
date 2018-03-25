"""
EDCmdrInfo by Seldonlabs
"""
import requests

import Tkinter as tk
import myNotebook as nb
from config import config
from monitor import monitor

from util import is_mode, is_target_locked, is_target_unlocked, is_scanned, is_command
from overlay import OverlayManager

APP_LONGNAME = "EDCommanderInfo"
APP_VERSION = "0.1.0"
INFO_SRV = "http://cmdrinfo.seldonlabs.com/req"
#INFO_SRV = "http://localhost:8000/req"

_overlay = None

TTL_LABEL = "Overlay duration (in seconds)"
TTL_VALUE_DEFAULT = 6
TTL_CONFIG_KEY = "EdCmdrInfoTimeToLive"
TTL_FIELD = tk.StringVar(value=config.get(TTL_CONFIG_KEY))

TIMEOUT = 10


def plugin_start():
    """
    Load this plugin into EDMC
    """
    global _overlay
    global PREFVAL_TTL
    _overlay = OverlayManager()

    if not TTL_FIELD.get():
        TTL_FIELD.set(str(TTL_VALUE_DEFAULT))
        config.set(TTL_CONFIG_KEY, str(TTL_VALUE_DEFAULT))

    print("{} {} loaded!".format(APP_LONGNAME, APP_VERSION))


def plugin_prefs(parent):
    """
    Handle plugin tab
    :param parent:
    :return:
    """
    PADX = 10
    PADY = 2

    ROW0 = 8
    ROW1 = 10
    ROW2 = 12
    ROW3 = 14

    BUTTONX = 12

    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text=APP_LONGNAME).grid(padx=PADX, row=ROW0, sticky=tk.W)

    nb.Label(frame, text=TTL_LABEL) \
        .grid(padx=PADX, pady=PADY, row=ROW3, sticky=tk.W)
    nb.Entry(frame, textvariable=TTL_FIELD) \
        .grid(padx=PADX, pady=PADY, row=ROW3, column=1, sticky=tk.EW)

    return frame


def prefs_changed():
    """
    Handle plugin preferences
    """
    config.set(TTL_CONFIG_KEY, TTL_FIELD.get())

    global _overlay
    _overlay.set_ttl(int(TTL_FIELD.get()))


def plugin_stop():
    """
    Close plugin
    """
    print("Closing {} version {}".format(APP_LONGNAME, APP_VERSION))


def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    hook for journal entry
    :param cmdr:
    :param is_beta:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    if not is_beta and is_mode():
        if is_target_locked(entry):
            if is_scanned(entry):
                global _overlay

                coded_pilot_name = entry['PilotName'].split(':')

                if coded_pilot_name[0] == "$cmdr_decorate":
                    # flush overlay
                    _overlay.flush()

                    search_name = coded_pilot_name[1][6:-1]

                    print('{}: looking for {}'.format(APP_LONGNAME, search_name))

                    pilot_name_localised = entry['PilotName_Localised']
                    _overlay.notify('Getting info for {}'.format(pilot_name_localised))

                    r = requests.post(INFO_SRV, data={'caller': cmdr,
                                                      'mode': monitor.mode.lower(),
                                                      'system': system,
                                                      'cmdr': search_name}, timeout=TIMEOUT)
                    r.raise_for_status()
                    reply = r.json()

                    _overlay.display_cmdr_name(pilot_name_localised)
                    _overlay.display_info(reply)
        elif is_target_unlocked(entry):
            _overlay.flush()