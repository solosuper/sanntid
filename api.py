#!/usr/bin/env python3
# coding: utf-8
'''
Make calls to the ruter API.
https://reisapi.ruter.no/help
'''

import pendulum
import requests
import geo
#from ruter_sanntid import geo

class APIError(Exception):
    """An API Error Exception"""

class Avgang:
    '''Store data related to a departure.'''
    def __init__(self, linjenr, navn, tid, plattform, avvik=None):
        # pylint: disable=R0913
        self.linjenr = linjenr
        self.navn = navn
        self.tid = pendulum.parse(tid).format('HH:mm')
        self.plattform = plattform
        if avvik is not None:
            self.avvik = list()
            for dev in avvik:
                self.avvik.append(dev['Header'])

    def __repr__(self):
        return "Avgang()"

    def __str__(self):
        return '{:>4s} {:20s} {}'.format(
            self.linjenr,
            self.navn,
            self.tid,
        )

class Stoppested:
    '''Store data related to a stoppested'''
    def __init__(self, stop_id, name, district):
        self.stop_id = stop_id
        self.name = name
        self.district = district

    def __repr__(self):
        return 'r: ' + self.name + ' ('+self.district+')'

    def __str__(self):
        return self.name + ' ('+self.district+')'

def fetch_realtime(stop_id):
    '''Retrieve realtime data at stop_id'''
    url = "http://reisapi.ruter.no/StopVisit/GetDepartures/" + str(stop_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise APIError('GET /tasks/ {}'.format(resp.status_code))

    avganger = list()
    for entry in resp.json():
        mvj = entry['MonitoredVehicleJourney']
        pln = mvj['PublishedLineName']
        name = mvj['DestinationName']
        edt = mvj['MonitoredCall']['ExpectedDepartureTime']
        plt = mvj['MonitoredCall']['DeparturePlatformName']
        dev = entry['Extensions']['Deviations']

        avganger.append(Avgang(pln, name, edt, plt, dev))
    return avganger

def by_platform(stop_id):
    '''Retrieve realtime data at stop_id. Sort departures by platform'''
    avganger = fetch_realtime(stop_id)
    plt = set()
    for avgang in avganger:
        plt.add(avgang.plattform)
    out = dict.fromkeys(plt, list())
    for platform in sorted(plt):
        out[platform] = list(filter(lambda x, curr=platform: x.plattform == curr, avganger))
    return out

def search(needle):
    '''Search for stoppesteder near the location of the device'''
    east, north = geo.utms()
    url = "http://reisapi.ruter.no/Place/GetPlaces/" + str(needle) \
            + "?location=(x="+east+",y="+north+")&counties=Oslo&counties=Akershus"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise APIError('GET /tasks/ {}'.format(resp.status_code))

    result = list()
    for entry in filter(lambda e: e['PlaceType'] == 'Stop', resp.json()):
        # d = {k: entry[k] for k in entry.keys() & {'District', 'Name', 'ID'}}
        result.append(Stoppested(entry['ID'], entry['Name'], entry['District']))
    return result

if __name__ == '__main__':
    #for d in distrikter():
    #    print(d)
    #for s in stoppesteder("Oslo"):
    #    print(s)
    #for s in search("mortensrud"):
    #    print(s)
    #    # for x in fetch_realtime(s['ID']):
    #    #    print(' ', x)
    #    print('----')
    #ID = s['ID']
    #

    #avganger = by_platform(3010950)
    ENTRIES = by_platform(3010953)
    #for k,v in avganger.items():
    #    print('{}{:=^20}'.format('Plattform ' + k,''))
    #    for x in v:
    #        print(x)
    L = list()
    for pltf, deps in ENTRIES.items():
        L.append('{}{:=^20}'.format('Plattform ' + pltf, ''))
        for avgang1 in deps:
            L.append(str(avgang1))
            for v in avgang1.avvik:
                L.append('{:4s} {}'.format('', v))
        L.append('')
    print(L)
