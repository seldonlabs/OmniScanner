import requests

from monitor import monitor

REPO_URL = "https://api.github.com/repos/seldonlabs/OmniScanner/tags"


def is_mode():
    return monitor.mode.lower() == 'open' if monitor.mode else 'no-instance'


def is_target_locked(entry):
    return entry['event'] == 'ShipTargeted' and entry['TargetLocked'] == True


def is_target_unlocked(entry):
    return entry['event'] == 'ShipTargeted' and entry['TargetLocked'] == False


def is_scanned(entry):
    return entry['ScanStage'] == 3


def is_command(entry):
    return entry['event'] == 'SendText'


def get_latest_version():
    r = requests.get(REPO_URL)
    r.raise_for_status()

    tags = r.json()

    return tags[0]['name']


def parse_version_number(version_number):
    return map(int, version_number.split('.', 2))


def is_latest_version(current_version, latest_version):
    current = parse_version_number(current_version)
    latest = parse_version_number(latest_version)

    if current[0] < latest[0]:
        return False

    if current[1] < latest[1]:
        return False

    if current[2] < latest[2]:
        return False

    return True
