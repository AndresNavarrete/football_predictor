import json

import duckdb
import pandas as pd
import requests


class Fixture:
    def __init__(self):
        self.url = "https://fixturedownload.com/feed/json/epl-2022"
        self.con = duckdb.connect()
        self.fixture = None
        self.names_translator = {
            "Man Utd": "Man United",
            "Spurs": "Tottenham",
            "Nottingham Forest": """Nott'm Forest""",
        }

    def get_fixture(self):
        raw_data = self.download_data()
        self.serialize_data(raw_data)
        self.fix_club_names()
        return self.fixture

    def download_data(self):
        response = requests.request("GET", self.url)
        return pd.DataFrame(json.loads(response.text))

    def serialize_data(self, raw_data):
        query_path = 'src/sql/serialize_data.sql' 
        query = self.load_query(query_path)
        self.fixture = self.con.execute(query).df()
    
    def load_query(self, query_path):
        return open(query_path, "r").read()

    def fix_club_names(self):
        replacement = {
            "home": self.names_translator,
            "away": self.names_translator,
        }
        return self.fixture.replace(replacement)

    def save(self):
        path = "data/ml/fixture.csv"
        self.fixture.to_csv(path)


if __name__ == "__main__":
    fixture = Fixture()
    fixture.get_fixture()
    fixture.save()
