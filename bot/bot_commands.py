import yaml
from aiogram import Dispatcher, types


async def set_commands(dp: Dispatcher):
    with open('bot/phrases/commands.yaml', encoding='utf-8') as yaml_file:
        commands = yaml.safe_load(yaml_file)
    commands = [
        types.BotCommand(command=f'{command}', description=commands[command])
        for command in commands
    ]
    print(commands)
    await dp.bot.set_my_commands(commands)
