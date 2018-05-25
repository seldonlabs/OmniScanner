"""
Convenience utils
"""

from requests import get, post, ConnectTimeout, ConnectionError, HTTPError

from monitor import monitor

from omniconfig import configuration


def call_srv(ver, caller, system, cmdr):
    """
    Calls the cmdrinfo service
    :param ver:
    :param caller:
    :param system:
    :param cmdr:
    :return:
    """
    try:
        r = post(configuration.get_url("srv"),
                 data={
                     'ver': ver,
                     'mode': monitor.mode.lower(),
                     'caller': caller,
                     'system': system,
                     'cmdr': cmdr},
                 timeout=10)

        r.raise_for_status()

        return r.json()

    except ConnectTimeout:
        return {'error': "Connection Timeout"}
    except HTTPError:
        return {'error': "Bad Request"}
    except ConnectionError:
        return {'error': "Connection Error"}


def is_mode():
    """
    Check for open mode
    :return:
    """
    return monitor.mode.lower() == 'open'


def is_target_locked(entry):
    """
    Check if an event is a ShipTargeted and a TargetLocked is true
    :param entry:
    :return:
    """
    return entry['event'] == 'ShipTargeted' and entry['TargetLocked'] == True


def is_target_unlocked(entry):
    """
    Check if an event is a ShipTargeted and a TargetLocked is false
    :param entry:
    :return:
    """
    return entry['event'] == 'ShipTargeted' and entry['TargetLocked'] == False


def is_scanned(entry):
    """
    Check for a scan stage, 2 for scanning, 3 for scanned
    :param entry:
    :return:
    """
    return entry['ScanStage'] == 3


def is_command(entry):
    """
    Check if is the chat is a command
    :param entry:
    :return:
    """
    return entry['event'] == 'SendText'


def get_latest_version():
    """
    Get the latest tag version from GitHub
    :return:
    """
    try:
        r = get(configuration.get_url("ver_srv"))
        r.raise_for_status()

        tags = r.json()

        return tags[0]['name']

    except Exception:
        warn("[{}] Error getting latest version".format("get_latest_version"))


def parse_version_number(version_number):
    """
    Parse a version number
    :param version_number:
    :return:
    """
    try:
        return map(int, version_number.split('.', 2))
    except Exception as ex:
        warn("[{}] {}".format("parse_version_number", ex))


def is_latest_version(current_version, latest_version):
    """
    Check if a latest version or not
    :param current_version:
    :param latest_version:
    :return:
    """
    current = parse_version_number(current_version)
    latest = parse_version_number(latest_version)

    try:
        for i in range(0, 2):
            if current[i] < latest[i]:
                notify("Found new latest version {}".format(latest_version))
                return False

        notify("{} is the latest version".format(current_version))

        return True

    except Exception as ex:
        warn("[{}] {}".format("is_latest_version", ex))
        raise Exception("Error checking for latest version")


def notify(msg):
    """
    log message
    :param msg:
    :return:
    """
    print(u"OmniScanner: {}".format(msg))


def warn(msg):
    """
    warning log message
    :param msg:
    :return:
    """
    print(u"OmniScanner: [WARNING] {}".format(msg))
