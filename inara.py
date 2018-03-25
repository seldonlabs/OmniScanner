"""
Inara API calls
"""

import json

labels = {
    'commanderName': 'Name',
    'preferredGameRole': 'Role',
    'preferredAllegianceName': 'Allegiance',
    'preferredPowerName': 'Power',
}

wing_labels = {
    'wingName': 'Wing',
    'wingMemberRank': 'Rank',
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


def parse_inara_reply(data):
    """
    Query the API
    :param reply:
    :return:
    """
    events = data['events']
    eventStatus = events[0]['eventStatus']

    cmdrData = None

    if eventStatus != 204:
        eventData = events[0]['eventData']
        if 'otherNamesFound' in eventData:
            print('ugh multiple results on Inara')
        else:
            cmdrData = {
                'base': {
                    labels[label]: eventData[label]
                    for label in labels if label in eventData
                },
                'rank': {
                    rank['rankName']: rank_values[rank['rankName']][rank['rankValue']]
                    for rank in eventData['commanderRanksPilot']
                }
            }

            # Wing data is not always present
            if 'commanderWing' in eventData:
                wingData = eventData['commanderWing']
                cmdrData['wing'] = {
                    wing_labels[label]: wingData[label]
                    for label in wing_labels
                }

    return cmdrData