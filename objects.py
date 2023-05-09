import pandas as pd
import json
from datetime import date, datetime


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
return json.loads(openedFile.read())["crawl_date"]


