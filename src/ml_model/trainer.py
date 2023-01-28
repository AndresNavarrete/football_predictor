import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.ml_model.base_trainer import BaseTrainer


class Trainer(BaseTrainer):
    def __init__(self):
        super().__init__()
        self.model_name = "RandomForestClassifier"

    def execute(self):
        self.load_database()
        self.split_database()
        self.set_encoder()
        self.set_model()
        self.train_model()
        self.generate_metadata()
        self.save_model()
        self.save_metadata()

    def load_database(self):
        path = f"{self.ML_DIR}/{self.DATAFILE}"
        df = pd.read_csv(path)
        df["diff_h_a"] = df.GF - df.GA
        df["result"] = df["diff_h_a"].apply(
            lambda row: self.get_result_from_row(row)
        )
        self.database = df

    def get_result_from_row(self, diff):
        if diff > 0:
            return 0
        if diff == 0:
            return 1
        return 2

    def split_database(self):
        self.features = self.database.drop(columns=self.not_usefull_columns)
        self.target = self.database[self.target_name]

    def set_encoder(self):
        categorical_preprocessor = OneHotEncoder(handle_unknown="ignore")
        numerical_preprocessor = StandardScaler()

        self.encoder = ColumnTransformer(
            [
                (
                    "one-hot-encoder",
                    categorical_preprocessor,
                    self.categoric_columns,
                ),
                (
                    "standard_scaler",
                    numerical_preprocessor,
                    self.numeric_columns,
                ),
            ]
        )

    def set_model(self):
        self.regressor = RandomForestClassifier(
            random_state=0, criterion="entropy"
        )
        self.model = make_pipeline(self.encoder, self.regressor)

    def train_model(self):
        self.model.fit(self.features, self.target)

    def generate_metadata(self):
        features_importance = dict()

        importances = self.regressor.feature_importances_
        for value, var in zip(importances, list(self.features)):
            features_importance[var] = value

        self.metadata = {
            "model": self.model_name,
            "features_importance": features_importance,
            "updated_at": time.time(),
        }

    def save_model(self):
        path = f"{self.ML_DIR}/trained_model.pkl"
        joblib.dump(self.model, path, compress=3)

    def save_metadata(self):
        path = f"{self.ML_DIR}/model_metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    trainer = Trainer()
    trainer.execute()
    print(trainer.metadata)
