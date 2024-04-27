from sentence_transformers import SentenceTransformer

import pandas
import json
import sys
from PIL import Image
import torch
from scipy.spatial import distance



class BertModel:
    def __init__(self):
        self.model = SentenceTransformer('cointegrated/rubert-tiny2')
        self.other_embs = {}

    def generate_embeddings(self, sentences: str) -> None:
        self.other_embs.clear()
        for row in sentences:
            other_emb = self.model.encode([row])[0]
            self.other_embs[row] = other_emb 

    def find_best(self, sentence: str): 
        emb = self.model.encode([sentence])[0]

        distances = {}         
        for row, other_emb in self.other_embs.items():
            dist = distance.cosine(emb, other_emb)
            distances[row] = dist
        
        dists = sorted(list(distances.items()), key=lambda a: a[1])[:10] 
        return dists[0][0]
