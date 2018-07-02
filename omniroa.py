"""
ROA parsers
"""

import re
import textwrap
from datetime import datetime

from config import config
import omniconfig as oc

ED_TIME_DIFF = 1286
rgx = 'Date\(([0-9]+)\+.*\)'


def _format_bool(boolVal):
    return 'YES' if boolVal else 'NO'


def _format_epoch(date):
    m = re.search(rgx, date)

    secs = int(m.group(1)) / 1000

    time = datetime.utcfromtimestamp(secs)

    year = time.year + ED_TIME_DIFF if not config.getint(oc.DISABLE_ED_TIME_KEY) else time.year
    month = time.month
    day = time.day

    return "{}-{}-{}".format(year, month, day)


def parse_reply_for_gui(reply):
    cmdrData = reply['cmdrData']
    parsed_data = None

    if cmdrData:
        if 'Clan' in cmdrData:
            parsed_data = []

            if cmdrData['Clan'] != "inara unknown":
                parsed_data.append({
                    'text': cmdrData['Clan'].decode('unicode-escape')
                })

            parsed_data.append({
                'text': "{}: {}".format("Last update", _format_epoch(cmdrData['lastUPD']))
            })

            if cmdrData['isClogger']:
                parsed_data.append({
                    'text': "Combat Logger",
                    'tag': "cl"
                })

            if cmdrData['isKOS']:
                parsed_data.append({
                    'text': "Kill on Sight by ROA",
                    'tag': "kos"
                })

                if 'KOSdesc' in cmdrData:
                    parsed_data.append({
                        'text': cmdrData['KOSdesc'].decode('unicode-escape')
                    })

    return parsed_data


def parse_reply_for_overlay(reply):
    data = reply['cmdrData']
    line_template = u"{}: {}"
    lines = None

    if data:
        lines = []

        if 'Clan' in data:
            lines.append(u'{}'.format(data['Clan']))

        if 'lastUPD' in data:
            lines.append(line_template.format('Last update', _format_epoch(data['lastUPD'])))

        if 'isClogger' in data:
            lines.append(line_template.format('Combat logger', _format_bool(data['isClogger'])))

        if 'isKOS' in data:
            lines.append(line_template.format('Kill on Sight', _format_bool(data['isKOS'])))
            if data['isKOS']:
                lines.append(u'\n{}: \n{}'.format('Reason for KOS', textwrap.fill(data['KOSdesc'], 20)))

    return lines
