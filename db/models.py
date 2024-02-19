import datetime
import enum
from typing import Annotated
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, 256]
created_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL")
)]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"),
        onupdate=datetime.datetime.utcnow(),
    )]


class Banks(enum.Enum):
    sberbank = "sberbank"
    alfa = "alfa"
    tochka = "tochka"
    vtb = "vtb"
    raif = "raif"
    modul = "modul"
    mts = "mts"
    ozon = "ozon"
    open = "open"


class TypeChanges(enum.Enum):
    news = "news"
    promotion1 = "promotion1"
    landing_page = "landing_page"
    pdf_file = "pdf_file"


class Changes(Base):
    __tablename__ = "changes"

    number: Mapped[intpk]
    bank: Mapped[Banks]
    typechanges: Mapped[TypeChanges]
    meta_data: Mapped[str | None]
    link_new_file: Mapped[str | None]
    link_old_file: Mapped[str | None]
    link_compare_file: Mapped[str | None]
    title: Mapped[str | None]
    description: Mapped[str | None]
    date: Mapped[created_at]


class Notification(enum.Enum):
    daily = "daily"
    weekly = "weekly"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    id_bot: Mapped[str_256 | None]
    username: Mapped[str]
    notification: Mapped[Notification]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]