from datetime import datetime

from sqlalchemy import func, ForeignKey

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import BIGINT

from enum import StrEnum

from curator_support.database.base import Base


class Role(StrEnum):
    STUDENT = "user"
    CURATOR = "curator"


class User(Base):  # type: ignore[misc]
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=False
    )
    role: Mapped[Role] = mapped_column(default=Role.STUDENT)
    created_at: Mapped[datetime] = mapped_column(default=func.now())



class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer: Mapped[str] = mapped_column()


class QuestionAnswer(Base):
    __tablename__ = "question_answer"

    question: Mapped[str] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column()
    answer_class: Mapped[int] = mapped_column(ForeignKey("answers.id"))

