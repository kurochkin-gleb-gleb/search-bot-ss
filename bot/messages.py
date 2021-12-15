import yaml

with open('bot/phrases/response_messages.yaml', encoding='utf-8') as yaml_file:
    bot_responses = yaml.safe_load(yaml_file)
