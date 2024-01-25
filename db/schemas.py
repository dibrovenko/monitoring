from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models import Banks, TypeChanges


class ChangesDTO(BaseModel):
    number: int
    bank: Banks
    typechanges: TypeChanges
    date: datetime


class ChangesPromotion(ChangesDTO):
    title: str | None


class ChangesFULLDTO(ChangesDTO):
    title: str | None
    meta_data: str | None
    link_new_file: str | None
    link_old_file: str | None
    link_compare_file: str | None
    description: str | None
