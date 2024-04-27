from sentence_transformers import SentenceTransformer

from scipy.spatial import distance

from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker


class BertModel:
    def __init__(self, db_uri: str):
        self.model = SentenceTransformer('cointegrated/rubert-tiny2')
        self.session_factory = sessionmaker(create_engine(db_uri.replace('asyncpg', 'psycopg2')))

    def generate_embeddings(self, sentences: list[str]) -> list[float]:
        embs = self.model.encode(sentences)[0]
        return embs.tolist()

    def add_new(self, sentence: str):
        emb = self.model.encode([sentence])[0]

        with self.session_factory() as session:
            answer_id = session.execute(text(
                "INSERT INTO answers (answer, embedding) VALUES (:a) RETURNING id"
            ), {'a': sentence}).scalars().all()
            session.commit()

    def find_best(self, sentence: str): 
        emb = self.model.encode([sentence])[0]

        with self.session_factory() as session:
            other_embs = session.execute(text(
                "SELECT answer, embedding FROM answers"
            )).all()

        distances = {}
        for row, other_emb in other_embs:
            dist = distance.cosine(emb, other_emb)
            distances[row] = dist
        
        dists = sorted(list(distances.items()), key=lambda a: a[1])[:10] 
        return dists[0][0]
