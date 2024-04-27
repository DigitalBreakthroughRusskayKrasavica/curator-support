from aiogram import types

from aiogram.filters import Filter

from curator_support.database.repository import DbRepository
from curator_support.models import Role


class CuratorFilter(Filter):
    async def __call__(self, message: types.Message, repo: DbRepository) -> bool:
        user_id = message.chat.id
        user = await repo.get_user_by_id(user_id)

        return user.role == Role.CURATOR
