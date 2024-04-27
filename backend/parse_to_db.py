import datetime
from datetime import date, timedelta
import random
import uuid
import csv

from sqlalchemy import text, Engine, create_engine, select
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
        "C:\\Users\\New\\Downloads\Telegram Desktop\\train_dataset_train_SecondPilot\\train_SecondPilot\\answer_class.csv",
        'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with session_factory() as session:
        for row in reader:
            emb = model_facade.generate_embeddings([row['Answer']])
            session.add(
                Answer(
                    id=row['answer_class'],
                    answer=row['Answer'],
                    embedding=emb
                )
            )
        try:
            session.commit()
        except IntegrityError as e:
            print(e)

with open(
        "C:\\Users\\New\\Downloads\Telegram Desktop\\train_dataset_train_SecondPilot\\train_SecondPilot\\train_data.csv",
        'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with session_factory() as session:
        for row in reader:
            session.add(
                QuestionAnswer(
                    question=row['Question'],
                    category=row['Category'],
                    answer_class=int(row['answer_class']),
                ),
            )

        session.commit()
