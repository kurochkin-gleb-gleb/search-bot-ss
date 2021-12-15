import asyncio
import datetime
import json

import aiohttp
import openpyxl

from bot.exceptions import NotCorrectColumnType, NotExistColumn
from excel import async_himera


def parse_row(row, columns_name):
    person = dict()
    for cell, col in zip(row, columns_name):
        person[col] = cell.value
    return person


def parse_excel(sheet):
    rows = sheet.rows
    columns_name = [col.value for col in next(rows)]
    people = []
    for row in rows:
        people.append(parse_row(row, columns_name))
    return people


def load_excel(file_name):
    print(file_name)
    excel = openpyxl.load_workbook(file_name)
    sheet = excel.active
    return excel, sheet, parse_excel(sheet)


def save_excel(excel, file_name):
    *directory, new_file_name = file_name.split('/')
    new_file_name = '/'.join(directory + ['new' + new_file_name])
    excel.save(new_file_name)
    return new_file_name


async def get_number(responses, session):
    phone_numbers = {}
    while len(phone_numbers) != len(responses):
        await asyncio.sleep(10)
        tasks = []
        for query_id, var in responses:
            tasks.append(asyncio.ensure_future(async_himera.view(query_id, session, var)))
        for res_view, var in await asyncio.gather(*tasks):
            if var in phone_numbers:
                continue
            # print(var, res_view)
            if 'error' in res_view:
                phone_numbers[var] = {None: None}
            if 'status' in res_view and res_view['status'] == 'ok':
                number = {}
                if res_view['query'] is None:
                    phone_numbers[var] = {None: None}
                else:
                    for base in res_view['query']:
                        if 'ТЕЛЕФОН' in base and var.startswith(base['ИМЯ'].replace(' ', '')):
                            number[base['БАЗА']] = base['ТЕЛЕФОН']
                    phone_numbers[var] = number
                # print(var, number)
        print('Статистика:', len(phone_numbers), len(responses))
    phone_numbers[None] = {}
    return phone_numbers


async def search_by_inn(file_name):
    excel, sheet, people = load_excel(file_name)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for person in people:
            if person['ИНН'] is None:
                continue
            tasks.append(asyncio.ensure_future(async_himera.search_by_inn(person['ИНН'], session)))
        responses = []
        for response, inn in await asyncio.gather(*tasks):
            responses.append((response['query_id'], inn))
        print('1')
        inn_to_number = await get_number(responses, session)
    print(inn_to_number)

    name_to_column = {}
    for name in list(inn_to_number.values()):
        if None in name:
            continue
        for n in name:
            sheet.cell(row=1, column=sheet.max_column + 1).value = n
            name_to_column[n] = sheet.max_column
        break

    rows = sheet.rows
    columns_name = [col.value for col in next(rows)]
    for row in rows:
        person = parse_row(row, columns_name)
        for name, column in name_to_column.items():
            row[column-1].value = inn_to_number.get(person['ИНН']).get(name)

    return save_excel(excel, file_name)


async def search_by_passport(file_name):
    excel, sheet, people = load_excel(file_name)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for person in people:
            if person['Номер документа, удостоверяющего личность'] is None:
                continue
            tasks.append(asyncio.ensure_future(async_himera.search_by_passport(
                person['Номер документа, удостоверяющего личность'], session
            )))
        responses = []
        for response, passport in await asyncio.gather(*tasks):
            responses.append((response['query_id'], passport))
        print('1')
        passport_to_number = await get_number(responses, session)
    print(passport_to_number)

    name_to_column = {}
    for name in list(passport_to_number.values()):
        if None in name:
            continue
        for n in name:
            sheet.cell(row=1, column=sheet.max_column + 1).value = n
            name_to_column[n] = sheet.max_column
        break

    rows = sheet.rows
    columns_name = [col.value for col in next(rows)]
    for row in rows:
        person = parse_row(row, columns_name)
        for name, column in name_to_column.items():
            row[column-1].value = passport_to_number.get(person['Номер документа, удостоверяющего личность']).get(name)

    return save_excel(excel, file_name)


async def search_by_snils(file_name):
    excel, sheet, people = load_excel(file_name)

    if 'снилс' not in people[0]:
        raise NotExistColumn('Колонка «снилс» отсутсвует в таблице')

    async with aiohttp.ClientSession() as session:
        tasks = []
        for person in people:
            if person['снилс'] is None:
                continue
            tasks.append(asyncio.ensure_future(async_himera.search_by_snils(person['снилс'], session)))
        responses = []
        for response, snils in await asyncio.gather(*tasks):
            print(response)
            responses.append((response['query_id'], snils))
        print('1')
        snils_to_number = await get_number(responses, session)
    print(snils_to_number)

    name_to_column = {}
    for name in list(snils_to_number.values()):
        if None in name:
            continue
        for n in name:
            sheet.cell(row=1, column=sheet.max_column + 1).value = n
            name_to_column[n] = sheet.max_column
        break
    print(name_to_column)
    rows = sheet.rows
    columns_name = [col.value for col in next(rows)]
    for row in rows:
        person = parse_row(row, columns_name)
        for name, column in name_to_column.items():
            print(snils_to_number.get(person['снилс']))
            row[column-1].value = snils_to_number.get(person['снилс']).get(name)

    return save_excel(excel, file_name)


async def search_by_name(file_name):
    excel, sheet, people = load_excel(file_name)

    if type(people[0]['Дата рождения']) is not datetime.datetime:
        raise NotCorrectColumnType('У даты рождения неверный тип, должна быть дата')

    async with aiohttp.ClientSession() as session:
        tasks = []
        for person in people:
            if person.get('Дата рождения') is None:
                continue
            full_name = f"{person.get('Фамилия')}{person.get('Имя')}{person.get('Отчество')}" \
                        f"{person.get('Дата рождения').day}{person.get('Дата рождения').month}" \
                        f"{person.get('Дата рождения').year}"

            tasks.append(asyncio.ensure_future(async_himera.search_by_name(
                lastname=person.get('Фамилия'),
                firstname=person.get('Имя'),
                middlename=person.get('Отчество'),
                day=person.get('Дата рождения').day,
                month=person.get('Дата рождения').month,
                year=person.get('Дата рождения').year,
                session=session,
                full_name=full_name,
            )))
        responses = []
        for response, full_name in await asyncio.gather(*tasks):
            responses.append((response['query_id'], full_name))
        name_to_number = await get_number(responses, session)
    #     with open('aa.json', 'w', encoding='utf-8') as f:
    #         f.write(json.dumps(name_to_number))
    # print(name_to_number)

    number_columns_name = []
    for name, number in name_to_number.items():
        if None in number:
            continue
        for n in number:
            if n in number_columns_name:
                continue
            number_columns_name.append(n)
        # print(name, number)
    # print()
    # print(number_columns_name)
    number_columns_name.sort(reverse=True, key=lambda x: int(next(filter(lambda y: len(y) == 4 and y.isdigit(), x.split() + ['2000']))))
    # print(number_columns_name)
    # print()

    used = dict()
    needed_columns = set()
    rows = sheet.rows
    columns_name = [col.value for col in next(rows)]
    for row in rows:
        person = parse_row(row, columns_name)
        if person.get('Дата рождения') is None:
            continue
        full_name = f"{person.get('Фамилия')}{person.get('Имя')}{person.get('Отчество')}" \
                    f"{person.get('Дата рождения').day}{person.get('Дата рождения').month}" \
                    f"{person.get('Дата рождения').year}"

        for name in number_columns_name:
            this_number = name_to_number.get(full_name).get(name)
            if this_number in used.get(full_name, {}).values():
                continue
            if full_name not in used:
                used[full_name] = dict()
            used[full_name][name] = this_number
            needed_columns.add(name)
    number_columns_name = [
        number_column_name for number_column_name in number_columns_name if number_column_name in needed_columns
    ]

    name_to_number_list = dict()
    for name, number in name_to_number.items():
        name_to_number_list[name] = [used.get(name).get(number_column_name) for number_column_name in number_columns_name if used.get(name) is not None]
        name_to_number_list[name] = list(filter(lambda x: len(x) == 10 and x[0] == '9' and x is not None, name_to_number_list[name]))
        # print(name, number, name_to_number_list[name])
    # print()

    max_column = sheet.max_column
    # for i in range(max(map(len, name_to_number_list.values()))):
    for i in range(3):
        sheet.cell(row=1, column=sheet.max_column + 1).value = f'Телефон {i + 1}'
    rows = sheet.rows
    columns_name = [col.value for col in next(rows)]
    for row in rows:
        person = parse_row(row, columns_name)
        if person.get('Дата рождения') is None:
            continue
        full_name = f"{person.get('Фамилия')}{person.get('Имя')}{person.get('Отчество')}" \
                    f"{person.get('Дата рождения').day}{person.get('Дата рождения').month}" \
                    f"{person.get('Дата рождения').year}"

        for i, number in enumerate(name_to_number_list[full_name]):
            if i == 3:
                break
            row[max_column + i].value = number
        # for name, this_number in used[full_name]:
        #     row[name_to_column[name] - 1].value = this_number

    print('FINAL')
    return save_excel(excel, file_name)
