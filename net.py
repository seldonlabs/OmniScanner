from requests import post, ConnectTimeout, ConnectionError, HTTPError

from monitor import monitor

INFO_SRV = "http://cmdrinfo.seldonlabs.com/req"
#INFO_SRV = "http://localhost:8000/req"


def call_srv(cmdr, system, search_name):
    """
    Calls the cmdrinfo service
    :param cmdr:
    :param system:
    :param search_name:
    :return:
    """
    try:
        r = post(INFO_SRV, data={'caller': cmdr,
                                 'mode': monitor.mode.lower(),
                                 'system': system,
                                 'cmdr': search_name}, timeout=10)
        r.raise_for_status()

        return r.json()
    except ConnectTimeout as ex:
        print(ex)
        return {'error': "Connection Timeout"}
    except HTTPError as ex:
        print(ex)
        return {'error': "Bad Request"}
    except ConnectionError as ex:
        print(ex)
        return {'error': "Connection Error"}
