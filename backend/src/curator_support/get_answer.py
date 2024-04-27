import csv

from sentence_transformers import SentenceTransformer

from scipy.spatial import distance

from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker


class BertModel:
    def __init__(self, db_uri: str):
        print(db_uri)
        self.model = SentenceTransformer('cointegrated/rubert-tiny2')
        self.session_factory = sessionmaker(create_engine(db_uri.replace('asyncpg', 'psycopg2')))

    def generate_embeddings(self, sentences: list[str]) -> list[float]:
        embs = self.model.encode(sentences)[0]
        return embs.tolist()

    def add_new(self, answer: str):
        emb = self.generate_embeddings([answer])

        with self.session_factory() as session:
            session.execute(text(
                "INSERT INTO answers (answer, embedding) VALUES (:a, :e) RETURNING id"
            ), {'a': answer, 'e': emb})
            session.commit()

    def find_best(self, sentence: str): 
        emb = self.model.encode([sentence])[0]

        with self.session_factory() as session:
            questions = session.execute(text(
                "SELECT question, embedding, answer_class FROM question_answer"
            )).all()

        distances = {}
        for question, embedding, answer_class in questions:
            dist = distance.cosine(emb, embedding)
            distances[question] = (dist, answer_class)

        dists = sorted(list(distances.items()), key=lambda a: a[1][0])[:10]
        return int(dists[0][1][1])
