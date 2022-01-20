import json
import re

import requests
from aiohttp.client_exceptions import ClientOSError

from config import HIMERA_KEY

url = 'https://api.himera-search.info/v2.1/'


async def view(query_id, session, var):
    data = {
        'key': HIMERA_KEY,
        't': 'view',
        'query_id': query_id,
    }
    try:
        async with session.post(url, data=data) as response:
            response_json = re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'', await response.text())
            return json.loads(response_json), var
    except json.decoder.JSONDecodeError:
        return {'status': 'ok', 'query': []}, var
    except ClientOSError:
        return {'status': 'ok', 'query': []}, var


async def search_by_inn(inn, session):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'inn': inn,
    }
    async with session.post(url, data=data) as response:
        return await response.json(), inn


async def search_by_snils(snils, session):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'snils': snils,
    }
    async with session.post(url, data=data) as response:
        return await response.json(), snils


async def search_by_passport(passport, session):
    data = {
        'key': HIMERA_KEY,
        't': 'search',
        'passport': passport,
    }
    async with session.post(url, data=data) as response:
        return await response.json(), passport


async def search_by_name(lastname, firstname, middlename, day, month, year, session, full_name):
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
    deleted = [key for key in data if data[key] is None]
    for key in deleted:
        del data[key]
    async with session.post(url, data=data) as response:
        return await response.json(), full_name


def get_limit():
    data = {
        'key': HIMERA_KEY,
        't': 'limit',
    }
    response = requests.post(url, data)
    return response.json()
