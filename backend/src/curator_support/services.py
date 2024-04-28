import asyncio
import os

from sqlalchemy import select

from curator_support.get_answer import BertModel
from curator_support.lms.rasa.get_answer import RasaModel
from curator_support.database.repository import DbRepository

from redis.asyncio import Redis

from curator_support.models import User


class HelperService:


    def __init__(self, db_repo: DbRepository, rubert_model: BertModel, rasa_model: RasaModel):
        self.db_repo = db_repo
        self.rubert_model = rubert_model
        self.rasa_model = rasa_model

        if not os.path.exists('current_model'):
            with open('current_model', 'w') as f:
                f.write("rubert")


    async def get_answer(self, question: str) -> str:
        loop = asyncio.get_event_loop()

        with open('current_model', 'r') as f:
            current_model = f.read().strip().rstrip()
        
        if current_model == "rubert":
            answer_class = await loop.run_in_executor(None, self.rubert_model.find_best, question)
            answer = await self.db_repo.get_answer_by_class(answer_class)
        else:
            answer = await loop.run_in_executor(None, self.rasa_model.get_answer, question)        
        return answer

    async def add_new_pair(self, question, category, answer):
        embeddings = self.model_facade.generate_embeddings([question])
        await self.db_repo.add_new_pair(question, embeddings, category, answer)

    async def find_unassigned_curator(self, redis_connection: Redis) -> int:
        curators = await self.db_repo.get_all_curators()

        for curator_id in curators:
            item = await redis_connection.get(curator_id)
            if item is None:
                return curator_id
        return 0

    async def change_role(self, user_id, role):
        await self.db_repo.change_role(user_id, role)
