"""
OmniScanner by Seldonlabs
"""
import sys
import plug
import Tkinter as tk
import myNotebook as nb

from config import config

import util
import net
from cache import Cache
from overlay import OverlayManager, TTL_CONFIG_KEY, TTL_VALUE_DEFAULT
from roa import DISABLE_ED_TIME_KEY

APP_LONGNAME = "OmniScanner"
APP_VERSION = "0.2.1"

this = sys.modules[__name__]

_cache = None
_overlay = None

_flag_status = 0
_hardpoints_deployed = False

TTL_LABEL = "Overlay duration (in seconds)"
TTL_FIELD = tk.StringVar(value=config.get(TTL_CONFIG_KEY))

DISABLE_ED_TIME_LABEL = "Disable Elite time"
DISABLE_ED_TIME_FIELD = tk.IntVar(value=config.get(DISABLE_ED_TIME_KEY))

DISABLE_SERVICE_MSG_KEY = "OmniScannerDisableSrvMsgs"
DISABLE_SERVICE_MSG_LABEL = "Disable Service messages"
DISABLE_SERVICE_MSG_FIELD = tk.IntVar(value=config.get(DISABLE_SERVICE_MSG_KEY))


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

    DISABLE_ED_TIME_FIELD.set(config.getint(DISABLE_ED_TIME_KEY))
    DISABLE_SERVICE_MSG_FIELD.set(config.getint(DISABLE_SERVICE_MSG_KEY))

    this.latest_ver = util.get_latest_version()
    this.is_latest_ver = util.is_latest_version(APP_VERSION, this.latest_ver)

    print("{} {} loaded!".format(APP_LONGNAME, APP_VERSION))


def plugin_app(parent):
   """
   Create a pair of TK widgets for the EDMC main window
   """
   latest_ver = util.get_latest_version()

   label = tk.Label(parent, text="Omni:")
   this.status = tk.Label(parent, anchor=tk.W, text="", fg="white")

   return (label, this.status)


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

    nb.Label(frame, text=DISABLE_ED_TIME_LABEL) \
        .grid(padx=PADX, pady=PADY, row=ROW2, sticky=tk.W)
    nb.Checkbutton(frame, text='Use normal UTC time instead of Elite 330x time', variable=DISABLE_ED_TIME_FIELD) \
        .grid(padx=PADX, pady=PADY, row=ROW2, column=1, sticky=tk.W)

    nb.Label(frame, text=DISABLE_SERVICE_MSG_LABEL) \
        .grid(padx=PADX, pady=PADY, row=ROW3, sticky=tk.W)
    nb.Checkbutton(frame, text='Disable activation/deactivation messages', variable=DISABLE_SERVICE_MSG_FIELD) \
        .grid(padx=PADX, pady=PADY, row=ROW3, column=1, sticky=tk.W)

    return frame


def prefs_changed():
    """
    Handle plugin preferences
    """
    config.set(TTL_CONFIG_KEY, TTL_FIELD.get())
    config.set(DISABLE_ED_TIME_KEY, DISABLE_ED_TIME_FIELD.get())
    config.set(DISABLE_SERVICE_MSG_KEY, DISABLE_SERVICE_MSG_FIELD.get())


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
    global _hardpoints_deployed
    global _flag_status

    if not is_beta:
        flags = entry['Flags']
        _is_in_SC = flags & plug.FlagsSupercruise

        if not _is_in_SC:
            _hardpoints_deployed = flags & plug.FlagsHardpointsDeployed
            if _hardpoints_deployed:
                if _flag_status + 64 == flags and not config.getint(DISABLE_SERVICE_MSG_KEY):
                    _overlay.service_message('{} deactivated'.format(APP_LONGNAME), "#ff0000")
                _flag_status = flags
            else:
                if _flag_status - 64 == flags and not config.getint(DISABLE_SERVICE_MSG_KEY):
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

    if not util.is_mode():
        this.status["text"] = "disabled in Solo/Private."
        this.status["fg"] = "red"
    elif util.is_mode() == 'no-instance':
        this.status["text"] = "No ED process"
        this.status["fg"] = "red"
    elif not this.is_latest_ver:
        this.status["text"] = "v{} available".format(this.latest_ver)
        this.status["fg"] = "yellow"
    else:
        this.status["text"] = "Ready"
        this.status["fg"] = "green"

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
                    _overlay.display_notification(u'Getting info for {}'.format(pilot_name_localised))

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
                        _overlay.display_error(cmdr_data['error'])
        #elif util.is_target_unlocked(entry):
         #   _overlay.flush()
