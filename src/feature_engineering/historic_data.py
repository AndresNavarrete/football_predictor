from datetime import datetime

import duckdb
import pandas as pd
import json


class Processor:
    def __init__(self):
        self.PREMIER_PATH = "data/results_premier/results.csv"
        self.ML_PATH = "data/ml"
        self.con = duckdb.connect()
        self.records = list()
        self.df = None
        self.categories_to_export = None
        self.useful_columns = [
            "season",
            "team",
            "opponent",
            "datetime",
            "veneau",
            "GF",
            "GA",
            "result",
        ]

    def execute(self):
        self.load_raw_data()
        self.serialize_data()
        self.add_streak_columns()
        self.add_categorical_columns()
        self.clean_data()
        self.export_data()

    def load_raw_data(self):
        self.df = pd.read_csv(self.PREMIER_PATH, encoding="ISO-8859-1")

    def serialize_data(self):
        self.df.apply(lambda row: self.add_records_from_row(row), axis=1)
        self.df = pd.DataFrame(self.records)[self.useful_columns]

    def add_records_from_row(self, row):
        home = self.get_home_record(row)
        away = self.get_away_record(row)
        self.records.extend([home, away])

    def get_home_record(self, row):
        return {
            "season": row.Season,
            "team": row.HomeTeam,
            "opponent": row.AwayTeam,
            "datetime": self.get_datetime(row.DateTime),
            "veneau": "home",
            "GF": row.FTHG,
            "GA": row.FTAG,
            "result": self.get_match_result(row.FTHG, row.FTAG),
        }

    def get_datetime(self, date_raw):
        date_str = date_raw.strip("Z").replace("T", " ")
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def get_match_result(self, GF, GA):
        if GF == GA:
            return "D"
        if GA > GF:
            return "L"
        else:
            return "W"

    def get_away_record(self, row):
        return {
            "season": row.Season,
            "team": row.AwayTeam,
            "opponent": row.HomeTeam,
            "datetime": self.get_datetime(row.DateTime),
            "veneau": "away",
            "GF": row.FTAG,
            "GA": row.FTHG,
            "result": self.get_match_result(row.FTAG, row.FTHG),
        }

    def add_streak_columns(self):
        df_matches = self.df
        query = """
            WITH matches AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY season, team ORDER BY datetime) AS match_number_home,
                ROW_NUMBER() OVER (PARTITION BY season, opponent ORDER BY datetime) AS match_number_away
            FROM df_matches
            ORDER BY season, datetime)
            SELECT
                m.*,
                (SELECT COUNT(*) FROM matches WHERE season = m.season AND team = m.team AND result = 'W' AND match_number_home > m.match_number_home - 6 AND match_number_home < m.match_number_home) AS home_last_wins,
                (SELECT COUNT(*) FROM matches WHERE season = m.season AND team = m.team AND result = 'L' AND match_number_home > m.match_number_home - 6 AND match_number_home < m.match_number_home) AS home_last_loses,
                (SELECT COUNT(*) FROM matches WHERE season = m.season AND team = m.team AND result = 'D' AND match_number_home > m.match_number_home - 6 AND match_number_home < m.match_number_home) AS home_last_draws,
                (SELECT COUNT(*) FROM matches WHERE season = m.season AND opponent = m.opponent AND result = 'W' AND match_number_away > m.match_number_away - 6 AND match_number_away < m.match_number_away) AS away_last_wins,
                (SELECT COUNT(*) FROM matches WHERE season = m.season AND opponent = m.opponent AND result = 'L' AND match_number_away > m.match_number_away - 6 AND match_number_away < m.match_number_away) AS away_last_loses,
                (SELECT COUNT(*) FROM matches WHERE season = m.season AND opponent = m.opponent AND result = 'D' AND match_number_away > m.match_number_away - 6 AND match_number_away < m.match_number_away) AS away_last_draws            
            FROM matches m
            ORDER BY season, datetime;
        """
        self.df = self.con.execute(query).df()

    def add_categorical_columns(self):
        self.df["home_code"] = self.df.team.astype("category").cat.codes
        self.df["away_code"] = self.df.opponent.astype("category").cat.codes
        self.save_categories()

    def save_categories(self):
        teams_cat = self.df.team.astype('category')
        teams_cat_dictionary = dict(enumerate(teams_cat.cat.categories))
        self.categories_to_export = {'team_codes': teams_cat_dictionary}
    
    def export_catgories(self):
        path = f"{self.ML_PATH}/model_categories.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.categories_to_export, f, ensure_ascii=False, indent=4)

    def clean_data(self):
        df_matches = self.df
        query = """
            select 
                team as home,
                opponent as away,
                home_code,
                away_code,
                home_last_wins,
                home_last_draws,
                home_last_loses,
                away_last_wins,
                away_last_draws,
                away_last_loses,
                GF,
                GA
            from df_matches
            where 
                GF < 10 and 
                GA < 10
            """
        self.df = self.con.execute(query).df()

    def export_data(self):
        self.export_catgories()
        self.df.to_csv(f"{self.ML_PATH}/df_history.csv", index=False)


if __name__ == "__main__":
    processor = Processor()
    processor.execute()
