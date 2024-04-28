import csv

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from curator_support.get_answer import BertModel
from curator_support.models import Answer, QuestionAnswer


def create_db_engine(db_uri: str) -> Engine:
    engine_options = {
        "echo": False,
        "pool_size": 15,
        "max_overflow": 15,
    }
    return create_engine(db_uri, **engine_options)


def create_session_maker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, autoflush=True, expire_on_commit=False)


DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_db_engine(DB_URI)
session_factory = create_session_maker(engine)

model_facade = BertModel(DB_URI)

with open(
        "./src/curator_support/models/rasa/answer_class.csv",
        'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with session_factory() as session:
        for row in reader:
            session.add(
                Answer(
                    id=row['answer_class'],
                    answer=row['Answer'],
                )
            )
        try:
            session.commit()
        except IntegrityError as e:
            print(e)

with open(
        "./src/curator_support/models/rasa/train_data.csv",
        'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with session_factory() as session:
        for row in reader:
            emb = model_facade.generate_embeddings([row['Question']])
            session.add(
                QuestionAnswer(
                    question=row['Question'],
                    category=row['Category'],
                    embedding=emb,
                    answer_class=int(row['answer_class']),
                ),
            )

        session.commit()
