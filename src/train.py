from src.feature_engineering.historic_data import Processor
from src.ml_model.trainer import Trainer

if __name__ == "__main__":
    processor = Processor()
    processor.execute()

    trainer = Trainer()
    trainer.execute()
