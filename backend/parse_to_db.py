import datetime
from datetime import date, timedelta
import random
import uuid
import csv

from sqlalchemy import text, Engine, create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

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


engine = create_db_engine("postgresql://postgres:postgres@localhost:5432/postgres")
session_factory = create_session_maker(engine)


with open("/home/akiko/Downloads/Telegram Desktop/train_dataset_train_SecondPilot/train_SecondPilot/answer_class.csv", 'r') as f:
    reader = csv.DictReader(f)
    with session_factory() as session:
        for row in reader:
            session.add(Answer(id=row['answer_class'], answer=row['Answer']))
        try:
            session.commit()
        except IntegrityError:
            pass

with open("/home/akiko/Downloads/Telegram Desktop/train_dataset_train_SecondPilot/train_SecondPilot/train_data.csv", 'r') as f:
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


