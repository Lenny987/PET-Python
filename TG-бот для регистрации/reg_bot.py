import logging
import os
from typing import Optional, List

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.deep_linking import decode_payload
from aiogram.utils.exceptions import TelegramAPIError
from pydantic import BaseModel, ValidationError
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DB_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")
TOKEN = os.getenv("токен бота")

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
redis_pool = ConnectionPool.from_url(REDIS_URL)
storage = RedisStorage2(connection_pool=redis_pool)
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserModel(BaseModel):
    id: int
    username: Optional[str]
    full_name: str


class RegistrationForm(StatesGroup):
    name = State()
    email = State()


class DatabaseUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    name = Column(String(100))
    email = Column(String(100))
    referral_id = Column(Integer, nullable=True)


async def get_user(telegram_id: int) -> Optional[DatabaseUser]:
    async with async_session() as session:
        result = await session.execute(
            select(DatabaseUser).where(DatabaseUser.telegram_id == telegram_id)
        )
        return result.scalars().first()


@dp.message_handler(commands=["start"], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    payload = message.get_args()
    referral_id = int(decode_payload(payload)) if payload else None

    user = await get_user(message.from_user.id)
    if user:
        await message.answer("🔹 Добро пожаловать снова!")
        return

    await message.answer("👋 Добро пожаловать! Введите ваше имя:")
    await RegistrationForm.name.set()
    await state.update_data(referral_id=referral_id)


@dp.message_handler(state=RegistrationForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📧 Теперь введите ваш email:")
    await RegistrationForm.email.set()


@dp.message_handler(state=RegistrationForm.email)
async def process_email(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = message.text.strip()

    try:
        validated = UserModel(
            id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            email=email
        )
    except ValidationError:
        await message.answer("❌ Некорректный email. Попробуйте снова:")
        return

    async with async_session() as session:
        new_user = DatabaseUser(
            telegram_id=validated.id,
            name=user_data["name"],
            email=validated.email,
            referral_id=user_data.get("referral_id")
        )
        session.add(new_user)
        await session.commit()

    await message.answer("✅ Регистрация завершена!")
    await state.finish()


@dp.errors_handler(exception=TelegramAPIError)
async def api_error_handler(update: types.Update, exception: TelegramAPIError):
    logger.error(f"Telegram API error: {exception}")
    return True


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)