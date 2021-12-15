import json

import requests

from config import HIMERA_KEY

url = 'https://api.himera-search.info/v2.1/'


def view(query_id):
    data = {
        'key': HIMERA_KEY,
        't': 'view',
        'query_id': query_id,
    }
    response = requests.post(url, data)
    return json.loads(response.content.decode().replace('\\', '\\\\'))
    # return response.json()


def search_by_inn(inn):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'inn': inn,
    }
    response = requests.post(url, data)
    return response.json()


def search_by_snils(snils):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'snils': snils,
    }
    response = requests.post(url, data)
    return response.json()


def search_by_passport(passport):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'passport': passport,
    }
    response = requests.post(url, data)
    return response.json()


def search_by_name(lastname, firstname, middlename, day, month, year):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'lastname': lastname,
        'firstname': firstname,
        'middlename': middlename,
        'day': day,
        'month': month,
        'year': year,
    }
    for key in data:
        if data[key] is None:
            del data[key]
    response = requests.post(url, data)
    return response.json()


def get_limit():
    data = {
        'key': HIMERA_KEY,
        't': 'limit',
    }
    response = requests.post(url, data)
    return response.json()
