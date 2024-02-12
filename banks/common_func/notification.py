from pydantic import BaseModel
from typing import List, Type

from db.core import AsyncORM
from db.schemas import ChangesDTO, ChangesFULLDTO


class File(BaseModel):
    name_file: str
    file_link: str | None


class Data_notification(BaseModel):
    text: str
    bank: str
    file: List[File | None]


class List_notification(BaseModel):
    list_notification: List[Data_notification]


async def notification_text_daily() -> List_notification:
    changes_from_db: List[ChangesFULLDTO] = await AsyncORM.select_changes_for_daily_notification()
    data = []
    for change in changes_from_db:
        data.append(Data_notification(
            text=f"`{change.number}`\n"
                 f"**Банк:** {str(change.bank)[6:]}\n"
                 f"**Тип изменения:** {str(change.typechanges)[12:]}\n"
                 f"**Заголовок:** {change.title}\n"
                 f"**Описание:** {change.description}\n"
                 f">*При открытии ссылки, необходимо удалить 'https://www.tinkoff.ru/' из начала ссылки - костыль,"
                 f" time не дает отправлять обычные ссылки ботам. Если ссылка все равно не открывается, возможно она "
                 f"заблокирована. В таком случае, откройте ее на нерабочем устройстве.*",
            bank=str(change.bank)[6:],
            file=[
                File(name_file="new",
                     file_link=change.link_new_file.rsplit('/', 1)[-1] if isinstance(change.link_new_file,
                                                                                     str) else None),
                File(name_file="old",
                     file_link=change.link_old_file.rsplit('/', 1)[-1] if isinstance(change.link_old_file,
                                                                                     str) else None),
                File(name_file="сompare",
                     file_link=change.link_compare_file.rsplit('/', 1)[-1] if isinstance(change.link_compare_file,
                                                                                         str) else None)
            ]
        ))
        output_string = (
            f"Номер: {change.number}\n"
            f"Банк: {str(change.bank)[6:]}\n"
            f"Тип изменения: {str(change.typechanges)[12:]}\n"
            f"Заголовок: {change.title}\n"
            f"Описание: {change.description}\n"
            f"Date: {change.date}\n"
            f"Meta Data: {change.meta_data}\n"
            f"Link to New File: {change.link_new_file}\n"
            f"Link to Old File: {change.link_old_file}\n"
            f"Link to Compare File: {change.link_compare_file}\n"
        )
    list_notification = List_notification(list_notification=data)
    return list_notification
