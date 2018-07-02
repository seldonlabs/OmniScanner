"""
Inara parsers
"""

import omniutils as ou

gui_ranks = [
    'combat',
    'trade',
    'exploration'
]

gui_wing = [
    'wingMemberRank',
    'wingName'
]

base_labels = {
    'preferredAllegianceName': 'Allegiance',
    'preferredPowerName': 'Power'
}

wing_labels = {
    'wingName': 'Wing',
    'wingMemberRank': 'Rank'
}

rank_values = {
    'combat': {
        0: 'Harmless',
        1: 'Mostly Harmless',
        2: 'Novice',
        3: 'Competent',
        4: 'Expert',
        5: 'Master',
        6: 'Dangerous',
        7: 'Deadly',
        8: 'Elite',
    },
    'trade': {
        0: 'Penniless',
        1: 'Mostly Penniless',
        2: 'Peddler',
        3: 'Dealer',
        4: 'Merchant',
        5: 'Broker',
        6: 'Entrepreneur',
        7: 'Tycoon',
        8: 'Elite',
    },
    'exploration': {
        0: 'Aimless',
        1: 'Mostly Aimless',
        2: 'Scout',
        3: 'Surveyor',
        4: 'Trailblazer',
        5: 'Pathfinder',
        6: 'Ranger',
        7: 'Pioneer',
        8: 'Elite',
    },
    'cqc': {
        0: 'Helpless',
        1: 'Mostly Helpless',
        2: 'Amateur',
        3: 'Semi Professional',
        4: 'Professional',
        5: 'Champion',
        6: 'Hero',
        7: 'Legend',
        8: 'Elite',
    },
    'empire': {
        0: 'None',
        1: 'Outsider',
        2: 'Serf',
        3: 'Master',
        4: 'Squire',
        5: 'Knight',
        6: 'Lord',
        7: 'Baron',
        8: 'Viscount',
        9: 'Count',
        10: 'Earl',
        11: 'Marquis',
        12: 'Duke',
        13: 'Prince',
        14: 'King'
    },
    'federation': {
        0: 'None',
        1: 'Recruit',
        2: 'Cadet',
        3: 'Midshipman',
        4: 'Petty Officer',
        5: 'Chief Petty Officer',
        6: 'Warrant Officer',
        7: 'Ensign',
        8: 'Lieutenant',
        9: 'Lt Commander',
        10: 'Post Commander',
        11: 'Post Captain',
        12: 'Rear Admiral',
        13: 'Vice Admiral',
        14: 'Admiral'
    }
}


def is_good_response(reply):
    """
    Check if the Inara response is solid
    :param reply:
    :return:
    """
    events = reply['events']

    if events[0]['eventStatus'] != 204:
        if 'otherNamesFound' in events[0]['eventData']:
            ou.notify("Ugh multiple results on Inara...")
            return False

        return True

    return False


def parse_reply_for_gui(reply):
    """
    Parse Inara reply for the GUI
    :param reply:
    :return:
    """
    parsed_data = None

    if is_good_response(reply):
        eventData = reply['events'][0]['eventData']
        parsed_data = []

        # give role a custom key
        if 'preferredGameRole' in eventData:
            if eventData['preferredGameRole']:
                parsed_data.append({
                    'text': eventData['preferredGameRole'],
                })

        for rank in eventData['commanderRanksPilot']:
            if rank['rankName'] in gui_ranks:
                rank_name = rank['rankName']
                rank_val = rank_values[rank_name][rank['rankValue']]
                parsed_data.append({
                    'text': rank_val,
                    'tag': rank_name,
                    'len': len(rank_val)
                })

        for label in base_labels:
            if label in eventData:
                if eventData[label]:
                    parsed_data.append({
                        'text': u"{}: {}".format(base_labels[label], eventData[label]),
                    })

        # Wing data is not always present
        if 'commanderWing' in eventData:
            wingData = eventData['commanderWing']
            parsed_data.append({
                'text': u" of ".join([wingData[label] for label in gui_wing]),
            })

    return parsed_data


def parse_reply_for_overlay(reply):
    """
    Parse Inara reply for the Overlay
    :param reply:
    :return:
    """
    line_template = u"{}: {}"
    cmdrData = None

    if is_good_response(reply):
        eventData = reply['events'][0]['eventData']

        cmdrData = {}

        # give role a custom key
        if 'preferredGameRole' in eventData:
            cmdrData['role'] = eventData['preferredGameRole']

        cmdrData['base'] = [
            line_template.format(base_labels[label], eventData[label])
            for label in base_labels if label in eventData
        ]

        cmdrData['rank'] = [
            line_template.format(rank['rankName'], rank_values[rank['rankName']][rank['rankValue']])
            for rank in eventData['commanderRanksPilot']
        ]

        # Wing data is not always present
        if 'commanderWing' in eventData:
            wingData = eventData['commanderWing']
            cmdrData['wing'] = [
                line_template.format(wing_labels[label], wingData[label])
                for label in wing_labels
            ]

    return cmdrData
