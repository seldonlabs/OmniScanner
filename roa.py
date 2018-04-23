import re
from datetime import datetime

from config import config

DISABLE_ED_TIME_KEY = "OmniScannerDisableEDTime"
ED_TIME_DIFF = 1286

roa_labels = {
    'Clan': 'Clan',
    'isClogger': 'Combat Logger',
    'isKOS': 'on KOS',
    'KOSdesc': 'Reason for KOS',
    'lastUPD': 'Last update'
}


rgx = 'Date\(([0-9]+)\+.*\)'


def _bool_to_str(boolVal):
    return 'YES' if boolVal else 'NO'


def _parse_epoch(date):
    m = re.search(rgx, date)

    secs = int(m.group(1)) / 1000

    time = datetime.utcfromtimestamp(secs)

    year = time.year + ED_TIME_DIFF if not config.getint(DISABLE_ED_TIME_KEY) else time.year
    month = time.month
    day = time.day

    return '{}-{}-{}'.format(year, month, day)


def parse_reply(reply):
    data = None

    cmdrData = reply['cmdrData']

    if cmdrData:
        data = {}

        for key in cmdrData:
            if key == 'isKOS' or key == 'isClogger':
                data[roa_labels[key]] = _bool_to_str(cmdrData[key])
            elif key == 'lastUPD':
                data[roa_labels[key]] = _parse_epoch(cmdrData[key])
            else:
                if cmdrData[key]:
                    data[roa_labels[key]] = cmdrData[key]

    return data
