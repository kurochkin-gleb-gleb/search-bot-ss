import yaml
from aiogram import types

with open('bot/phrases/reply_keyboards.yaml', encoding='utf-8') as yaml_file:
    reply_keyboard_texts = yaml.safe_load(yaml_file)

menu = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
menu.add(*reply_keyboard_texts['menu'].values())

cancel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
cancel.add(*reply_keyboard_texts['cancel'])
