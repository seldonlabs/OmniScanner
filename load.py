"""
OmniScanner by SeldonLabs
"""

import Tkinter as tk

import myNotebook as nb
import plug
from config import config

import omniutils as ou
import omniconfig as oc
from omnicache import cacheDatabase
from omnigui import Gui
from omnioverlay import OverlayManager

APP_LONGNAME = "OmniScanner"
APP_VERSION = "0.4.0"

_gui = None
_enable_overlay = False
_overlay = None
_latest_ver = 0
_is_latest_ver = False
_flag_status = 0
_hardpoints_deployed = False
_padx = 10
_pady = 2


def plugin_start():
    """
    Load this plugin into EDMC
    """
    global _gui
    global _enable_overlay
    global _overlay
    global _latest_ver
    global _is_latest_ver

    _gui = Gui()

    # checking for overlay
    _enable_overlay = config.getint(oc.ENABLE_OVERLAY_KEY)

    # enable EDMCOverlay
    if _enable_overlay:
        try:
            import edmcoverlay
            _overlay = OverlayManager(edmcoverlay.Overlay())
            ou.notify("Overlay is on.")
        except ImportError:
            ou.warn("Overlay is enabled but EDMCOverlay plugin not installed!")

    # set gui options
    if not oc.TTL_FIELD.get():
        oc.TTL_FIELD.set(str(oc.TTL_VALUE_DEFAULT))
        config.set(oc.TTL_CONFIG_KEY, str(oc.TTL_VALUE_DEFAULT))

    oc.ENABLE_OVERLAY_FIELD.set(_enable_overlay)
    oc.DISABLE_ED_TIME_FIELD.set(config.getint(oc.DISABLE_ED_TIME_KEY))
    oc.DISABLE_SERVICE_MSG_FIELD.set(config.getint(oc.DISABLE_SERVICE_MSG_KEY))

    try:
        _latest_ver = ou.get_latest_version()
        _is_latest_ver = ou.is_latest_version(APP_VERSION, _latest_ver)
    except Exception as ex:
        ou.warn(ex)
        # Set latest version anyway on error
        _is_latest_ver = True

    ou.notify("version {} loaded!".format(APP_VERSION))


def plugin_app(parent):
    """
    Create a pair of TK widgets for the EDMC main window
    :param parent:
    :return:
    """
    return _gui.init_gui(parent)


def plugin_prefs(parent):
    """
    Handle plugin tab
    :param parent:
    :return:
    """
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text="Scanner Options", fg="blue")\
        .grid(padx=_padx, row=0, sticky=tk.W)

    nb.Label(frame, text="Disable Elite time") \
        .grid(padx=_padx, pady=_pady, row=1, sticky=tk.W)
    nb.Checkbutton(frame, text="Use normal UTC time instead of Elite 330x time.",
                   variable=oc.DISABLE_ED_TIME_FIELD) \
        .grid(padx=_padx, pady=_pady, row=1, column=1, sticky=tk.W)

    nb.Label(frame, text="Overlay Options (You have to install EDMCOverlay)", fg="blue")\
        .grid(padx=_padx, row=5, sticky=tk.W)

    nb.Label(frame, text="Use Overlay") \
        .grid(padx=_padx, pady=_pady, row=6, sticky=tk.W)
    nb.Checkbutton(frame, text="Use EDMCOverlay (you need to restart EDMC).",
                   variable=oc.ENABLE_OVERLAY_FIELD) \
        .grid(padx=_padx, pady=_pady, row=6, column=1, sticky=tk.W)

    nb.Label(frame, text="Overlay duration (in seconds)") \
        .grid(padx=_padx, pady=_pady, row=7, sticky=tk.W)
    nb.Entry(frame, textvariable=oc.TTL_FIELD) \
        .grid(padx=_padx, pady=_pady, row=7, column=1, sticky=tk.EW)

    nb.Label(frame, text="Disable service messages") \
        .grid(padx=_padx, pady=_pady, row=8, sticky=tk.W)
    nb.Checkbutton(frame, text="Disable activation/deactivation messages (Overlay only).",
                   variable=oc.DISABLE_SERVICE_MSG_FIELD) \
        .grid(padx=_padx, pady=_pady, row=8, column=1, sticky=tk.W)

    return frame


def prefs_changed():
    """
    Handle plugin preferences
    """
    config.set(oc.DISABLE_ED_TIME_KEY, oc.DISABLE_ED_TIME_FIELD.get())
    config.set(oc.ENABLE_OVERLAY_KEY, oc.ENABLE_OVERLAY_FIELD.get())
    config.set(oc.TTL_CONFIG_KEY, oc.TTL_FIELD.get())
    config.set(oc.DISABLE_SERVICE_MSG_KEY, oc.DISABLE_SERVICE_MSG_FIELD.get())


def plugin_stop():
    """
    Close plugin
    """
    cacheDatabase.close()

    if _overlay:
        _overlay.shutdown()

    ou.notify("shutting down")


def dashboard_entry(cmdr, is_beta, entry):
    """
    Check for Status.json
    :param cmdr:
    :param is_beta:
    :param entry:
    :return:
    """
    global _hardpoints_deployed
    global _flag_status

    # only if overlay is on
    if not is_beta and _enable_overlay:
        flags = entry['Flags']
        _is_in_SC = flags & plug.FlagsSupercruise

        # not in SC
        if not _is_in_SC:
            _hardpoints_deployed = flags & plug.FlagsHardpointsDeployed
            if _hardpoints_deployed:
                if _flag_status + 64 == flags and not config.getint(oc.DISABLE_SERVICE_MSG_KEY):
                    _overlay.service_message("{} disabled".format(APP_LONGNAME), "#ff0000")
                    status_update()
                _flag_status = flags
            else:
                if _flag_status - 64 == flags and not config.getint(oc.DISABLE_SERVICE_MSG_KEY):
                    _overlay.service_message("{} enabled".format(APP_LONGNAME), "#00ff00")
                    status_update()
                _flag_status = flags


def status_update():
    """
    Update EDMC panel entry for OmniScanner
    :return:
    """
    if not _is_latest_ver:
        _gui.status.set_new_version_message(_latest_ver)
    elif _hardpoints_deployed:
        _gui.status.set_disabled_on_hp()
    else:
        if not ou.is_mode():
            _gui.status.set_disabled_on_solo_pvt()
        else:
            _gui.status.set_ready()


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
    if not is_beta:
        status_update()

        if ou.is_mode() and not _hardpoints_deployed:
            if ou.is_target_locked(entry):
                if ou.is_scanned(entry):
                    coded_pilot_name = entry['PilotName'].split(':')

                    if coded_pilot_name[0] == "$cmdr_decorate":
                        search_name = coded_pilot_name[1][6:-1]

                        pilot_name_localised = entry['PilotName_Localised']

                        # log message
                        ou.notify(u"Looking for {}".format(pilot_name_localised))

                        # gui update
                        _gui.status.set_querying_msg(pilot_name_localised)

                        # overlay update
                        if _overlay:
                            _overlay.display_notification("Getting info for {}".format(pilot_name_localised))

                        # get data from cache
                        cache_data = cacheDatabase.check(search_name)

                        if cache_data:
                            cmdr_data = cache_data
                        else:
                            cmdr_data = ou.call_srv(APP_VERSION, cmdr, system, search_name)

                        if not 'error' in cmdr_data:
                            # Add scan to cache
                            cacheDatabase.add_to_cache(search_name, cmdr_data)

                            # Update GUI log and show result on gui
                            _gui.update_log()

                            # Show result on overlay
                            if _enable_overlay:
                                _overlay.display_info(pilot_name_localised, cmdr_data)

                            # update status again after querying message
                            status_update()
                        else:
                            # display error
                            _gui.status.set_error(cmdr_data['error'])

                            if _enable_overlay:
                                _overlay.display_error(cmdr_data['error'])
