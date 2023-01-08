
class BaseTrainer:

    def __init__(self):
        self.ML_DIR = "data/ml"
        self.DATAFILE = "df_history.csv"
        self.database = None
        self.features = None
        self.target = None
        self.encoder = None
        self.regressor = None
        self.model = None
        self.metadata = None
        self.target_name = "diff_h_a"
        self.not_usefull_columns = [
            self.target_name,
            'home',
            'away',
            'GF',
            'GA',    
            ]
        self.numeric_columns = [
            "home_last_wins",
            "home_last_draws",
            "home_last_loses",
            "away_last_wins",
            "away_last_draws",
            "away_last_loses",
        ]
        self.categoric_columns = [
            "home_code",
            "away_code",
        ]