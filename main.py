from rivescript import RiveScript
import os.path
import pandas as pd
import json
from datetime import date, datetime

bot = RiveScript()


def __get_content():
    def __crawl_wikipedia():
        url = r'https://en.wikipedia.org/wiki/Casualties_of_the_Russo-Ukrainian_War'
        tables = pd.read_html(url)

        wikipedia_source = {"crawl_date": date.today().strftime("%d/%m/%Y"), "content": []}
        wikipedia_data = []
        for entry in tables[2].values:
            x = {"kind": entry[0], "amount": entry[1], "date_range": entry[2], "source": entry[3]}
            wikipedia_data.append(x)

        wikipedia_source["content"] = wikipedia_data

        wikipedia_file = open("wikipedia_source.json", "w")
        wikipedia_file.write(json.dumps(wikipedia_source))
        return wikipedia_file

    try:
        openedFile = open("wikipedia_source.json", "r")
    except FileNotFoundError:
        print("No File: Crawling")
        openedFile = __crawl_wikipedia()
    else:
        wikipedia_json = json.loads(openedFile.read())
        if datetime.strptime(wikipedia_json["crawl_date"], "%d/%m/%Y").date() < date.today():
            print("File old: Crawling")
            openedFile = __crawl_wikipedia()
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


file = os.path.dirname(__file__)
responses = os.path.join(file, 'responses')
bot.set_subroutine("get_sources_as_options", __get_sources_as_options)
bot.set_subroutine("get_entry", __get_entry)
bot.load_directory(responses)
bot.sort_replies()

while True:
    msg = str(input('You> '))

    if msg == 'q':
        break
    else:
        print('Bot>' + bot.reply('localuser', msg))
