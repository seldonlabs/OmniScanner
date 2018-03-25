from monitor import monitor


def is_mode():
    return monitor.mode.lower() == 'open'


def is_target_locked(entry):
    return entry['event'] == 'ShipTargeted' and entry['TargetLocked'] == True


def is_target_unlocked(entry):
    return entry['event'] == 'ShipTargeted' and entry['TargetLocked'] == False


def is_scanned(entry):
    return entry['ScanStage'] == 3


def is_command(entry):
    return entry['event'] == 'SendText'