import pandas as pd

class Standings:

    def __init__(self):
        self.fixture_path = "data/ml/fixture.csv"

        self.database = None
        self.table_positions = None
        self.teams = dict()
    
    def execute(self):
        self.load_fixture()
        self.set_teams()
        self.fill_teams_historic_data()
    
    def load_fixture(self):
        df = pd.read_csv(self.fixture_path)
        self.database = df
    
    def set_teams(self):
        for team in list(self.database.home.unique()):
            team_data = {'points': 0, 'matches': 0 , 'streak': ''}
            self.teams[team] = team_data
    
    def fill_teams_historic_data(self):
        df = self.database[self.database.played == True].sort_values(by = 'DATE')
        for _ , row in df.iterrows():
            self.process_row(row)
    
    def process_row(self, row):
        gh = row.home_goals
        ga = row.away_goals
        home = row.home
        away = row.away
        if gh > ga:
            self.add_winning_home_results(home, away)
        elif gh == ga:
            self.add_draw_results(home, away)
        else:
            self.add_losing_home_results(home, away)

    def add_winning_home_results(self, home, away):
        self.teams[home]['points'] += 3
        self.teams[home]['streak'] += 'W'
        self.teams[home]['matches'] += 1

        self.teams[away]['points'] += 0
        self.teams[away]['streak'] += 'L'
        self.teams[away]['matches'] += 1
    
    def add_draw_results(self, home, away):
        self.teams[home]['points'] += 1
        self.teams[home]['streak'] += 'D'
        self.teams[home]['matches'] += 1

        self.teams[away]['points'] += 1
        self.teams[away]['streak'] += 'D'
        self.teams[away]['matches'] += 1
    
    def add_losing_home_results(self, home, away):
        self.teams[home]['points'] += 0
        self.teams[home]['streak'] += 'L'
        self.teams[home]['matches'] += 1

        self.teams[away]['points'] += 3
        self.teams[away]['streak'] += 'W'
        self.teams[away]['matches'] += 1

if __name__ == "__main__":
    standings = Standings()
    standings.execute()

    
    
    
