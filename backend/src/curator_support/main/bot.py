import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from curator_support.presentation.bot.config import load_bot_config
from curator_support.presentation.bot.middlewares import DIMiddleware

DEFAULT_CONFIG_PATH = ".configs/app.toml"
LOGGING_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
    cfg = load_bot_config(os.getenv("CURATOR_SUPPORT_CONFIG_PATH") or DEFAULT_CONFIG_PATH)

    # storage = RedisStorage.from_url(cfg.redis.dsn)
    # storage.key_builder = DefaultKeyBuilder(with_destiny=True)

    # dp = Dispatcher(storage=storage)
    dp = Dispatcher()

    # engine = create_async_engine(cfg.db.uri, future=True, echo=True)
    # session_factory = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DIMiddleware())

    bot = Bot(token=cfg.token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
