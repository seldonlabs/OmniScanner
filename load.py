"""
OmniScanner by Seldonlabs
"""
import plug
import Tkinter as tk
import myNotebook as nb

from config import config

import util
import net
from cache import Cache
from overlay import OverlayManager, TTL_CONFIG_KEY, TTL_VALUE_DEFAULT
from roa import ED_DATE_KEY, ED_DATE_VALUE

APP_LONGNAME = "OmniScanner"
APP_VERSION = "0.1.0"

_cache = None
_overlay = None

_flag_status = 0
_hardpoints_deployed = False

TTL_LABEL = "Overlay duration (in seconds)"
TTL_FIELD = tk.StringVar(value=config.get(TTL_CONFIG_KEY))

ED_DATE_LABEL = "Use Elite time"
ED_DATE_FIELD = tk.IntVar(value=config.get(ED_DATE_KEY))


def plugin_start():
    """
    Load this plugin into EDMC
    """
    global _cache
    global _overlay
    _cache = Cache()
    _overlay = OverlayManager()

    if not TTL_FIELD.get():
        TTL_FIELD.set(str(TTL_VALUE_DEFAULT))
        config.set(TTL_CONFIG_KEY, str(TTL_VALUE_DEFAULT))

    if not ED_DATE_FIELD.get():
        ED_DATE_FIELD.set(ED_DATE_VALUE)
        config.set(ED_DATE_KEY, ED_DATE_VALUE)

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
        .grid(padx=PADX, pady=PADY, row=ROW1, sticky=tk.W)
    nb.Entry(frame, textvariable=TTL_FIELD) \
        .grid(padx=PADX, pady=PADY, row=ROW1, column=1, sticky=tk.EW)

    nb.Label(frame, text=ED_DATE_LABEL) \
        .grid(padx=PADX, pady=PADY, row=ROW2, sticky=tk.W)
    nb.Checkbutton(frame, text='Use Elite time or normal UTC time', variable=ED_DATE_FIELD) \
        .grid(padx=PADX, pady=PADY, row=ROW2, column=1, sticky=tk.W)

    return frame


def prefs_changed():
    """
    Handle plugin preferences
    """
    config.set(TTL_CONFIG_KEY, TTL_FIELD.get())
    config.set(ED_DATE_KEY, ED_DATE_FIELD.get())


def plugin_stop():
    """
    Close plugin
    """
    global _cache
    _cache.close()
    print("Closing {}".format(APP_LONGNAME))


def dashboard_entry(cmdr, is_beta, entry):
    """
    Check for Status.json
    :param cmdr:
    :param is_beta:
    :param entry:
    :return:
    """
    global _overlay
    global _flag_status

    if not is_beta:
        flags = entry['Flags']
        _is_in_SC = flags & plug.FlagsSupercruise

        if not _is_in_SC:
            _hardpoints_deployed = flags & plug.FlagsHardpointsDeployed
            if _hardpoints_deployed:
                if _flag_status + 64 == flags:
                    _overlay.service_message('{} deactivated'.format(APP_LONGNAME), "#ff0000")
                _flag_status = flags
            else:
                if _flag_status - 64 == flags:
                    _overlay.service_message('{} activated'.format(APP_LONGNAME), "#00ff00")
                _flag_status = flags



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

    global _hardpoints_deployed

    if not is_beta and util.is_mode() and not _hardpoints_deployed:
        if util.is_target_locked(entry):
            if util.is_scanned(entry):
                global _cache
                global _overlay

                coded_pilot_name = entry['PilotName'].split(':')

                if coded_pilot_name[0] == "$cmdr_decorate":
                    # flush overlay
                    _overlay.flush()

                    search_name = coded_pilot_name[1][6:-1]

                    print(u'{}: looking for {}'.format(APP_LONGNAME, search_name))

                    pilot_name_localised = entry['PilotName_Localised']
                    _overlay.notify(u'Getting info for {}'.format(pilot_name_localised))

                    cache_data = _cache.check(search_name)

                    if cache_data:
                        cmdr_data = cache_data
                    else:
                        cmdr_data = net.call_srv(cmdr, system, search_name)

                    if not 'error' in cmdr_data:
                        _cache.add_to_cache(search_name, cmdr_data)

                        _overlay.display_cmdr_name(pilot_name_localised)
                        _overlay.display_info(cmdr_data)
                    else:
                        _overlay.error(cmdr_data['error'])
        #elif util.is_target_unlocked(entry):
         #   _overlay.flush()
