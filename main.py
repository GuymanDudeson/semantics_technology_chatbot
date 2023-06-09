from rivescript import RiveScript
import os.path
import re
import pandas as pd
import json
from datetime import date, datetime
import requests

bot = RiveScript()


def __get_content():

    def __remove_parentheses(input):
        return re.sub("[(\[].*?[)\]]", "", input)

    def __crawl_websites():
        fileContent = {"crawl_date": date.today().strftime("%d/%m/%Y"), "content": []}
        content = __crawl_wikipedia() + __crawl_statista()
        fileContent["content"] = content
        statistic_file = open("sources.json", "a+")
        statistic_file.write(json.dumps(fileContent))
        return statistic_file

    def __crawl_wikipedia():
        url = r'https://en.wikipedia.org/wiki/Casualties_of_the_Russo-Ukrainian_War'
        tables = pd.read_html(url)

        wikipedia_data = []
        for entry in tables[2].values:
            x = {"kind": __remove_parentheses(entry[0]),
                 "amount": __remove_parentheses(entry[1]),
                 "date_range": __remove_parentheses(entry[2]),
                 "source": __remove_parentheses(entry[3])}
            wikipedia_data.append(x)

        return wikipedia_data

    def __crawl_statista():
        api_key = "tXeTWh-kxYqw"
        project_token = "tyTjd3PWCqMC"

        params = {
            'api_key': f'{api_key}',
        }

        url = f'https://www.parsehub.com/api/v2/projects/{project_token}/last_ready_run/data'
        response = requests.get(url, params)
        data = json.loads(response.text)
        statista_data = [{
            "kind": "Civilian",
            "amount": __remove_parentheses(data["civilian_casualties"]),
            "date_range": __remove_parentheses(data["date_range"]),
            "source": "Statista"
        }]
        return statista_data

    try:
        openedFile = open("sources.json", "r+")
    except FileNotFoundError:
        print("No File: Crawling")
        openedFile = __crawl_websites()
    else:
        statistic_json = json.loads(openedFile.read())
        if datetime.strptime(statistic_json["crawl_date"], "%d/%m/%Y").date() < date.today():
            print("File old: Crawling")
            openedFile = __crawl_websites()
    openedFile.seek(0, 0)
    return json.loads(openedFile.read())["content"]


def __get_entries_by_topic(content):
    topic = bot.get_uservar("localuser", "scope")
    relevantContent = []

    if topic == "russian":
        relevantContent = [x for x in content if str(x["kind"]).__contains__("Russ")]
    elif topic == "ukraine":
        relevantContent = [x for x in content if str(x["kind"]).__contains__("Ukr")]
    elif topic == "civil":
        relevantContent = [x for x in content if str(x["kind"]).__contains__("Civilians")]

    return relevantContent


def __get_sources_as_options(rs, args):
    content = __get_content()
    result = "\n"
    for i, entry in enumerate(__get_entries_by_topic(content)):
        result += i.__str__() + ". " + entry["source"] + "\n"
    return result


def __get_entry(rs, args):
    index = bot.get_uservar("localuser", "sourceindex")
    content = __get_content()
    entry = __get_entries_by_topic(content)[int(index)]
    return f'\n The number of {entry["kind"]} casualties in the timespan from {entry["date_range"]} according to the {entry["source"]} is {entry["amount"]}'

__get_content()

file = os.path.dirname(__file__)
responses = os.path.join(file, 'responses')
bot.set_subroutine("get_sources_as_options", __get_sources_as_options)
bot.set_subroutine("get_entry", __get_entry)
bot.load_directory(responses)
bot.sort_replies()

while True:
    msg = str(input('You> '))

    if msg == 'shutdown':
        break
    else:
        print('Bot> ' + bot.reply('localuser', msg))
