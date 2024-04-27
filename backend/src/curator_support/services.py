import asyncio

from curator_support.get_answer import BertModel
from curator_support.database.repository import DbRepository


class HelperService:
    def __init__(self, db_repo: DbRepository, model: BertModel):
        self.db_repo = db_repo
        self.model_facade = model
    
    async def get_answer(self, question: str) -> str:
        answers = await self.db_repo.get_all_answers()

        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, self.model_facade.find_best, question)

        return answer

