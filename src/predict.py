from src.content_generator.table_creator import TableCreator
from src.ml_model.predictor import Predictor
from src.providers.fixture import Fixture

if __name__ == "__main__":
    fixture = Fixture()
    predictor = Predictor()
    table_creator = TableCreator()

    fixture.get_fixture()
    fixture.save()

    predictor.execute()

    table_creator.execute()
