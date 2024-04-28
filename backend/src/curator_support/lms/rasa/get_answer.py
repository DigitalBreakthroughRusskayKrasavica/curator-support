import csv
import requests

from sqlalchemy import text

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError


url = 'http://127.0.0.1:6060/model/parse'
confidence_limit = 0.3  # уверенность, ниже которой скипаем вопрос


class RasaModel:
    def __init__(self, db_uri: str):
        self.session_factory = sessionmaker(create_engine(db_uri.replace('asyncpg', 'psycopg2')))

    def get_answer(self, question: str):
        with self.session_factory() as session:
            answers = dict(session.execute(text(
                "SELECT id, answer FROM answers"
            )).all())

        r = requests.post(
            url,
            json={
                'text': question
            }
        )

        if r.status_code != 200:
            return 'Произошла ошибка'

        if r.json()['intent']['confidence'] < confidence_limit:
            return "Не получилось найти ответ - свяжитесь с куратором"
        return f"{answers[int(r.json()['intent']['name'].split('_')[-1])]}"


def create_db_engine(db_uri: str) -> Engine:
    engine_options = {
        "echo": False,
        "pool_size": 15,
        "max_overflow": 15,
    }
    return create_engine(db_uri, **engine_options)


def create_session_maker(engine: Engine) -> sessionmaker:
    return sessionmaker(engine, autoflush=True, expire_on_commit=False)


# DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres"

# engine = create_db_engine(DB_URI)
# session_factory = create_session_maker(engine)

# md = RasaModel(session_factory)
