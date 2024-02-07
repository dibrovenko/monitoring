import os
from typing import List
from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text
from datetime import datetime, timedelta

from banks.common_func.except_handlers import async_exception_handler
from db.database import Base, async_engine, async_session_factory
from db.models import Users, Changes, Banks, TypeChanges
from db.schemas import ChangesDTO, ChangesFULLDTO


async def update_title(typechanges: TypeChanges.__members__,
                       title_old: str | None = None, title_new: str | None = None):
    async with async_session_factory() as session:
        if title_new is None:
            # Находим последнюю запись по дате
            latest_record: ChangesFULLDTO = (
                await session.execute(
                    select(Changes)
                    .filter(Changes.bank == Banks.alfa, Changes.typechanges == typechanges)
                    .order_by(Changes.date)
                    .limit(1)
                )
            ).scalar()
            # Модифицируем значения в найденной записи
            if latest_record:
                latest_record.title = "Измененная запись"
                await session.commit()
        else:
            latest_record: ChangesFULLDTO = (
                await session.execute(
                    select(Changes)
                        .filter(Changes.bank == Banks.alfa, Changes.typechanges == typechanges, Changes.title == title_old)
                )
            ).scalar()
            # Модифицируем значения в найденной записи
            if latest_record:
                latest_record.title = title_new
                await session.commit()


async def update_metadata(typechanges: TypeChanges.__members__, new_metadata: str):
    async with async_session_factory() as session:
        # Находим последнюю запись по дате
        latest_record: ChangesFULLDTO = (
            await session.execute(
                select(Changes)
                .filter(Changes.bank == Banks.alfa, Changes.typechanges == typechanges)
                .order_by(Changes.date)
                .limit(1)
            )
        ).scalar()
        # Модифицируем значения в найденной записи
        if latest_record:
            latest_record.meta_data = new_metadata
            await session.commit()


async def update_new_link(typechanges: TypeChanges.__members__, new_link: str):
    async with async_session_factory() as session:
        # Находим последнюю запись по дате
        latest_record: ChangesFULLDTO = (
            await session.execute(
                select(Changes)
                .filter(Changes.bank == Banks.alfa, Changes.typechanges == typechanges)
                .order_by(Changes.date)
                .limit(1)
            )
        ).scalar()

        # Модифицируем значения в найденной записи
        if latest_record:
            latest_record.link_new_file = new_link
            await session.commit()


async def test_all():
    await update_title(typechanges=TypeChanges.news, title_old="Альфа-Банк повысит ставку по накопительному счету с 1 января",
                       title_new="Измененная новость")

    await update_title(typechanges=TypeChanges.promotion1, title_old="Правила проведения Акции «Твоя выгода» для юридических лиц и индивидуальных предпринимателей клиентов Банка сегмента «Малый и микробизнес»",
                       title_new="Измененная акция")
    await update_metadata(typechanges=TypeChanges.promotion1,
                          new_metadata=
                          """pikepdf.Dictionary({
                          "/Author": "Нуштаева Наталья Вадимовна",
                          "/CreationDate": "D:20240109223354+05'00'",
                          "/Creator": "Microsoft® Word 2016",
                          "/ModDate": "D:20240109223354+05'00'",
                          "/Producer": "Microsoft® Word 2016"})""")

    await update_metadata(typechanges=TypeChanges.pdf_file,
                          new_metadata=
                          """pikepdf.Dictionary({
                          "/Author": "Нуштаева Наталья Вадимовна",
                          "/CreationDate": "D:20240109223354+05'00'",
                          "/Creator": "Microsoft® Word 2016",
                          "/ModDate": "D:20240109223354+05'00'",
                          "/Producer": "Microsoft® Word 2016"})""")
    await update_title(typechanges=TypeChanges.pdf_file, title_old="Высокие обороты || Действующий тариф",
                       title_new="Высокие обороты || Архивный тариф")

    await update_new_link(typechanges=TypeChanges.landing_page,
                          new_link=f'{os.getcwd()}/banks/alfa/test_landing_page.xlsx')
    await update_metadata(typechanges=TypeChanges.landing_page,
                          new_metadata="""Малый бизнес и ИП
Сравнение тарифов для бизнеса
Добавить тариф
Простой
Для обслуживания без лишних условий
Открыть счёт
Ноль за обслуживание
Для начинающего или сезонного бизнеса
Открыть счёт
Уверенное начало
Для постоянного бизнеса с небольшими оборотами
Открыть счёт
Быстрое развитие
Для активно развивающегося бизнеса
Открыть счёт
Активные расчёты
Для частых расчётов с контрагентами
Открыть счёт
Высокие обороты
Для максимального комфорта
Открыть счёт
ОБСЛУЖИВАНИЕ И ПЕРЕВОДЫ
Обслуживание счёта
1% — от поступлений до 750 000 ₽
2% — до 2 млн ₽
3% — свыше 2 млн ₽
0 ₽
690 ₽
1 690 ₽
4 990 ₽
6 690 ₽
Обслуживание при оплате за год
–
–
6 900 ₽
(3 месяца — в подарок)
16 900 ₽
36 900 ₽
(2 месяца — в подарок)
60 200 ₽
(3 месяца — в подарок)
Переводы на счета юрлиц и ИП
0 ₽
0 ₽ — первые 3 перевода,
далее — 99 ₽ за перевод
0 ₽ — первые 10 переводов,
далее — 79 ₽ за перевод
0 ₽ — первые 25 переводов,
далее — 59 ₽ за перевод
0 ₽ — первые 50 переводов,
далее — 39 ₽ за перевод
0 ₽ — первые 200 переводов,
далее — 19 ₽ за перевод
Переводы юрлицам и ИП внутри банка
1000 ₽
0 ₽
0 ₽
0 ₽
0 ₽
0 ₽
Переводы на счета физлиц
Внутрибанковские переводы
0% — до 1 млн ₽
2,5% — от 1 млн ₽
Платежи в другие банки
0% — до 1 млн ₽
2,8% — от 1 млн ₽
Внутрибанковские переводы
2%  + 99₽
Платежи в другие банки
2,3% + 99₽
Внутрибанковские переводы
1,7%  + 79₽
Платежи в другие банки
2% + 79₽
Внутрибанковские переводы
0% — до 100 000 ₽
1,5% + 59₽ — от 100 000 ₽
Платежи в другие банки
0% — до 100 000₽
1,8% + 59₽ — от 100 000₽
Внутрибанковские переводы
0% — до 200 000 ₽
1,3% — от 200 000 ₽
Платежи в другие банки
0% — до 200 000 ₽
1,6% — от 200 000 ₽
Внутрибанковские переводы
0% — до 400 000 ₽
1% — от 400 000 ₽
Платежи в другие банки
0% — до 400 000 ₽
1,3% — от 400 000 ₽
Переводы со счёта ИП на личный счёт в Альфа-Банке
0% — до 2 млн ₽
2,5% — свыше 2 млн ₽
0% — до 100 000 ₽
2% + 99 ₽ — свыше 100 000 ₽
0% — до 300 000 ₽
1,7% + 79 ₽ — свыше 300 000 ₽
0% — до 300 000 ₽
1,5% + 59 ₽ — свыше 300 000 ₽
0% — до 600 000 ₽
1,3% — свыше 600 000 ₽
0% — до 600 000 ₽
1% — свыше 600 000 ₽
Платежи по бумажным поручениям
0,1%
(минимум 400 ₽)
0,1%
(минимум 400 ₽)
0,1%
(минимум 400 ₽)
0,1%
(минимум 400 ₽)
0,1%
(минимум 400 ₽)
0,1%
(минимум 400 ₽)
Налоговые и бюджетные платежи
0 ₽
0 ₽
0 ₽
0 ₽
0 ₽
0 ₽
КАРТЫ И НАЛИЧНЫЕ
Обслуживание карты Альфа-Бизнес
первая карта:
0 ₽ — 6 месяцев,
далее — 199 ₽ в месяц
следующие: 199 ₽ в месяц
первая карта:
0 ₽ — 6 месяцев,
далее — 299 ₽ в месяц
следующие: 299 ₽ в месяц
первая карта:
0 ₽ — 6 месяцев,
далее — 299 ₽ в месяц
следующие: 299 ₽ в месяц
первая карта:
0 ₽ — 12 месяцев,
далее — 299 ₽ в месяц
следующие: 299 ₽ в месяц
первая карта:
0 ₽ — 12 месяцев,
далее — 299 ₽ в месяц
следующие: 299 ₽ в месяц
первая карта:
0 ₽ — 12 месяцев,
далее — 299 ₽ в месяц
следующие: 299 ₽ в месяц
Обслуживание карты Альфа-Бизнес Премиум
699 ₽ в месяц
699 ₽ в месяц
699 ₽ в месяц
699 ₽ в месяц
699 ₽ в месяц
699 ₽ в месяц
Снятие наличных с карты
0% — до 1 млн ₽
3% — свыше 1 млн ₽
3%, но не менее 129 ₽
3%, минимум 229 ₽
0% — до 100 000 ₽
2,2% — свыше 100 000 ₽
0% — до 200 000 ₽
2,1% — от 200 000 ₽, но не менее 179 ₽
0% — до 400 000 ₽
2% — свыше 400 000 ₽
Снятие наличных в кассе банка
0% — до 1 млн ₽
3,3% — свыше 1 млн ₽
3,3%, но не менее 6 600 ₽
3,3%, минимум 6 600 ₽
0% — до 100 000 ₽
3,2% — свыше 100 000 ₽
минимум 9 400 ₽
0% — до 200 000 ₽
3,1% — от 200 000 ₽, но не менее 279 ₽
минимум 6 200 ₽
0% — до 400 000 ₽
3% — свыше 400 000 ₽
минимум 6 000 ₽
Внесение наличных по карте
1%
0% — до 100 000 ₽
0,3% — свыше 100 000 ₽
0% — до 150 000 ₽
0,3% — свыше 150 000 ₽
0% — до 500 000 ₽
0,2% — свыше 500 000 ₽
0% — до 1 млн ₽
0,1% — свыше 1 млн ₽
0% — до 2 млн ₽
0,1% — свыше 2 млн ₽
Внесение наличных в кассе банка
1%
0,5%
(минимум 1 500 ₽)
0,4%
(минимум 1 200 ₽)
0,3%
(минимум 900 ₽)
0,3%
(минимум 900 ₽)
0,15%
(минимум 900 ₽)
РАБОТА С ВАЛЮТОЙ
Обслуживание счёта в евро
–
–
1 990 ₽ — при среднем остатке до 100 000 €
0,1% — свыше 100 000 €
1 990 ₽ — при среднем остатке до 100 000 €
0,1% — свыше 100 000 €
1 990 ₽ — при среднем остатке до 100 000 €
0,05% — свыше 100 000 €
1 990 ₽ — при среднем остатке до 100 000 €
0,1% — свыше 100 000 €
Обслуживание счёта в других валютах
–
–
3 990 ₽
6 990 ₽
990 ₽
990 ₽
Переводы на счета юрлиц и ИП
–
–
0,25%
(минимум 45 $ или €,
максимум 225 $ или €)
0,25%
(минимум 45 $ или €,
максимум 225 $ или €)
0,12%
(минимум 25 $ или €,
максимум 200 $ или €)
0,15%
(минимум 37 $ и 28 €,
максимум 200 $ и 150 €)
Переводы юрлицам и ИП внутри банка
–
–
0 ₽
0 ₽
0 ₽
0 ₽ — первые 200 переводов
19 ₽ — все последующие переводы
Снятие наличных
–
–
5,3% — до 30 000 $ или €
4,4 % — свыше 30 000 $ или €
3,3% — до 30 000 $ или €
4,4% — свыше 30 000 $ или €
3,3% — до 30 000 $ или €
4,4% — свыше 30 000 $ или €
3,3% — до 30 000 $ или €
4% — свыше 30 000 $ или €
Внесение наличных
–
–
0,55%
0,55%
0,55%
0,55%
Покупка и продажа валюты
–
–
0,8% — до 100 000 $ или €
0,7% — до 500 000 $ или €
0,5% — до 1 млн $ или €
0,4 % — свыше 1 млн $ или €
0,6% — до 100 000 $ или €
0,5% — до 500 000 $ или €
0,4% — до 1 млн $ или €
0,3% — свыше 1 млн $ или €
0,4% — до 100 000 $ или €
0,3% — до 500 000 $ или €
0,2% — до 1 млн $ или €
0,1% — свыше 1 млн $ или €
0,4% — до 100 000 $ или €
0,3% — до 500 000 $ или €
0,2% — до 1 млн $ или €
0,1% — свыше 1 млн $ или €
Валютный контроль
0 ₽(не предусмотрено)
0,15% — от суммы перевода
(минимум 600 ₽)
0,15% + НДС — от суммы перевода
(минимум 600 ₽)
0,15% + НДС — от суммы перевода
(минимум 600 ₽)
0,12% + НДС — от суммы перевода
(минимум 500 ₽)
0,14% + НДС — от суммы перевода
(минимум 600 ₽)
Валютный контроль при рублёвых переводах нерезидентами РФ
0 ₽(не предусмотрено)
0,05% + НДС — от суммы перевода
(минимум 150 ₽, максимум 3000 ₽)
0,05% 
0,05%
0,05%
0,05%
Принятие на учёт контракта или кредитного договора
0 ₽(не предусмотрено)
3300 ₽ — для срочных контрактов
1200 ₽ — для несрочных
(НДС включён)
3300 ₽ — для срочных контрактов
1200 ₽ — для несрочных
(НДС включён)
3300 ₽ — для срочных контрактов
1200 ₽ — для несрочных
(НДС включён)
0 ₽

1200 ₽ — для несрочных
(НДС включён)
ДРУГИЕ УСЛУГИ
Заверение карточек с образцами подписей и оттиска печати
0 ₽
0 ₽ — за первую карточку
600 ₽ — за каждую следующую
0 ₽ — за первую карточку
600 ₽ — за каждую следующую
0 ₽ — за первую карточку
600 ₽ — за каждую следующую
0 ₽ — за первую карточку
600 ₽ — за каждую следующую
0 ₽ — за первую карточку
600 ₽ — за каждую следующую
Оформление чековой книжки
0 ₽
0 ₽
0 ₽
3 000 ₽
0 ₽
0 ₽
Смс об операциях по счёту
99 ₽ — за первый номер
199 ₽ — за второй номер
299 ₽ — за третий номер
99 ₽ — за первый номер
199 ₽ — за второй номер
299 ₽ — за третий номер
99 ₽ — за первый номер
199 ₽ — за второй номер
299 ₽ — за третий номер
99 ₽ — за первый номер
199 ₽ — за второй номер
299 ₽ — за третий номер
99 ₽ — за первый номер
199 ₽ — за второй номер
299 ₽ — за третий номер
99 ₽ — за первый номер
199 ₽ — за второй номер
299 ₽ — за третий номер
Смс об операциях по карте Альфа‑Бизнес
99 ₽ — за каждую карту
99 ₽ — за каждую карту
0 ₽ — за первую карту
99 ₽ — за каждую следующую
99 ₽ — за каждую карту
99 ₽ — за каждую карту
99 ₽ — за каждую карту
Смс об операциях по карте Альфа‑Бизнес Премиум
0 ₽ — за каждую карту
0 ₽ — за каждую карту
0 ₽ — за каждую карту
0 ₽ — за каждую карту
0 ₽ — за каждую карту
0 ₽ — за каждую карту
Сервис «Индикатор риска»
0 ₽ — первые 2 месяца,
далее — 240 ₽ в месяц
(НДС включён)
0 ₽ — первые 2 месяца,
далее — 240 ₽ в месяц
(НДС включён)
0 ₽ — первые 2 месяца,
далее — 240 ₽ в месяц
(НДС включён)
240 ₽ в месяц
(НДС включён)
0 ₽ — первые 2 месяца,
далее — 240 ₽ в месяц
(НДС включён)
0 ₽ — первые 2 месяца,
далее — 240 ₽ в месяц
(НДС включён)""")