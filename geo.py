#!/usr/bin/env python3
# coding: utf-8
'''Get the location of the computer, based on the IP address.'''

import requests
import utm as utmc

def __get_ipinfo():
    return requests.get('https://ipinfo.io/geo').json()

def latlons():
    '''Return latitude and longitude as str'''
    ipinfo = __get_ipinfo()
    lat, lon = ipinfo['loc'].split(',')
    return lat, lon

def latlonf():
    '''Return latitude and longitude as floats'''
    ipinfo = __get_ipinfo()
    lat, lon = ipinfo['loc'].split(',')
    return float(lat), float(lon)

def utmf():
    '''Return UTM coordinates as floats'''
    lat, lon = latlonf()
    utm_result = utmc.from_latlon(lat, lon)
    return utm_result[0], utm_result[1]

def utms():
    '''Return UTM coordinates as str'''
    utm_e, utm_n = utmf()
    return str(utm_e), str(utm_n)

if __name__ == '__main__':
    print(utmf())
