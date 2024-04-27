import asyncio

from sqlalchemy import select

from curator_support.get_answer import BertModel
from curator_support.database.repository import DbRepository

from redis.asyncio import Redis

from curator_support.models import User


class HelperService:
    def __init__(self, db_repo: DbRepository, model: BertModel):
        self.db_repo = db_repo
        self.model_facade = model
    
    async def get_answer(self, question: str) -> str:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, self.model_facade.find_best, question)

        return answer

    async def find_unassigned_curator(self, redis_connection: Redis) -> int:
        curators = await self.db_repo.get_all_curators()

        for curator_id in curators:
            item = await redis_connection.get(curator_id)
            print("Curator is busy: ", item)
            if item is None:
                return curator_id
        return 0
