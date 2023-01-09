import json
import operator as op

import joblib
import pandas as pd

from src.feature_engineering.standings import Standings


class Predictor:
    def __init__(self):
        self.ML_DIR = "data/ml"

        self.model = None
        self.categories = None
        self.future_matches = None
        self.standings = None

    def execute(self):
        self.load_model()
        self.load_categories()
        self.set_standing()
        self.set_future_matches()
        self.forecast_rest_of_season()
        self.standings.export_table()

    def load_model(self):
        path = f"{self.ML_DIR}/trained_model.pkl"
        self.model = joblib.load(path)

    def load_categories(self):
        path = f"{self.ML_DIR}/model_categories.json"
        with open(path) as f:
            self.categories = json.load(f)

    def set_standing(self):
        self.standings = Standings()
        self.standings.execute()

    def set_future_matches(self):
        self.future_matches = self.standings.database.query("played == False")

    def forecast_rest_of_season(self):
        for _, row in self.future_matches.iterrows():
            home = row.home
            away = row.away
            data_parsed = self.parse_match_row(row)
            prediction = self.model.predict(data_parsed)[0]
            self.manage_prediction(prediction, home, away)

    def get_next_match(self):
        row = self.future_matches.iloc[10]
        return self.parse_match_row(row)

    def parse_match_row(self, row):
        home = row.home
        away = row.away
        parsed_data = {
            "home_code": self.get_team_code(home),
            "away_code": self.get_team_code(away),
            "home_last_wins": self.get_last_results(home, "W"),
            "home_last_draws": self.get_last_results(home, "D"),
            "home_last_loses": self.get_last_results(home, "L"),
            "away_last_wins": self.get_last_results(away, "W"),
            "away_last_draws": self.get_last_results(away, "D"),
            "away_last_loses": self.get_last_results(away, "L"),
        }
        return pd.DataFrame([parsed_data])

    def get_last_results(self, team, result):
        streak_lenght = 5
        team_streak = self.standings.teams[team]["streak"]
        last_matches = team_streak[-streak_lenght:]
        return op.countOf(last_matches, result)

    def get_team_code(self, team):
        for code, team_name in self.categories["team_codes"].items():
            if team_name == team:
                return code
        return -1

    def manage_prediction(self, prediction, home, away):
        if prediction >= 1:
            self.standings.add_winning_home_results(home, away)
        elif prediction <= -1:
            self.standings.add_losing_home_results(home, away)
        else:
            self.standings.add_draw_results(home, away)


if __name__ == "__main__":
    predictor = Predictor()
    predictor.execute()
