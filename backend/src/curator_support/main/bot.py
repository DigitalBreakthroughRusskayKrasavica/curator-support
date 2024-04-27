import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from curator_support.services import HelperService

from curator_support.presentation.bot.config import load_bot_config
from curator_support.presentation.bot.middlewares import DIMiddleware
from curator_support.presentation.bot.middlewares.auth import AuthMiddleware

from curator_support.database.repository import DbRepository
from curator_support.database.sa_utils import create_engine, create_session_maker
from curator_support.get_answer import BertModel

from curator_support.presentation.bot.router import router
from curator_support.presentation.bot.handlers.curators import router as curator_router


DEFAULT_CONFIG_PATH = ".configs/app.toml"
LOGGING_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
    cfg = load_bot_config(os.getenv("CURATOR_SUPPORT_CONFIG_PATH") or DEFAULT_CONFIG_PATH)

    storage = RedisStorage.from_url(cfg.redis.dsn)
    storage.key_builder = DefaultKeyBuilder(with_destiny=True)

    dp = Dispatcher(storage=storage)
    dp.include_router(curator_router)
    dp.include_router(router)

    engine = create_engine(cfg.db.uri)
    session_factory = create_session_maker(engine)

    db_repo = DbRepository(session_factory)
    
    model_facade = BertModel()
    answers = await db_repo.get_all_answers()
    model_facade.generate_embeddings(answers)

    helper_service = HelperService(db_repo, model_facade)

    dp.message.outer_middleware(AuthMiddleware(repo=db_repo, curator_secret_key=cfg.curator_auth_key))
    dp.update.outer_middleware(DIMiddleware(
        service=helper_service, 
        repo=db_repo,
    ))


    bot = Bot(token=cfg.token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
