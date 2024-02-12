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
                    .filter(Changes.bank == Banks.tochka, Changes.typechanges == typechanges)
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
                        .filter(
                        Changes.bank == Banks.tochka, Changes.typechanges == typechanges, Changes.title == title_old)
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
                .filter(Changes.bank == Banks.tochka, Changes.typechanges == typechanges)
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
                .filter(Changes.bank == Banks.tochka, Changes.typechanges == typechanges)
                .order_by(Changes.date)
                .limit(1)
            )
        ).scalar()

        # Модифицируем значения в найденной записи
        if latest_record:
            latest_record.link_new_file = new_link
            await session.commit()


async def test_all():
    await update_title(typechanges=TypeChanges.news)
    await update_title(typechanges=TypeChanges.promotion1)

    await update_new_link(typechanges=TypeChanges.landing_page,
                          new_link=f'{os.getcwd()}/banks/tochka/test_landing_page.xlsx')

    await update_metadata(typechanges=TypeChanges.pdf_file,
                          new_metadata=
                          """pikepdf.Dictionary({
                          "/Author": "Нуштаева Наталья Вадимовна",
                          "/CreationDate": "D:20240109223354+05'00'",
                          "/Creator": "Microsoft® Word 2016",
                          "/ModDate": "D:20240109223354+05'00'",
                          "/Producer": "Microsoft® Word 2016"})""")
    await update_title(typechanges=TypeChanges.pdf_file, title_old="Тарифы ООО «Банк Точка» с 18.01.2024 г.",
                       title_new="test Тарифы ООО «Банк Точка» с 18.01.2024 г.")
    await update_metadata(typechanges=TypeChanges.landing_page,
                          new_metadata="""Условия и тарифы
Не платите за обслуживание, пока нет движений по счёту.
Только для клиентов, открывших все счета на одну
компанию с 18.05.24
Одна оплата
Если у вас меньше одного счёта в Точке, не нужно платить за обслуживание каждого из них: достаточно заплатить один раз
Общие лимиты
На переводы физлицам, снятие наличных и пополнение. Если нужно увеличить лимит, можно подключить Подписку+ на текущем тарифе или сменить его.
Прозрачные условия
Вы платите за обслуживание только после того, как проведёте первую операцию по любому из счетов в течение месяца
Действует на все тарифы, кроме «Корпоративного»
НОЛЬ
0 ₽ в месяц
НАЧАЛО
000 ₽ в месяц
РАЗВИТИЕ
3 000 ₽ в месяц
700 ₽ в месяц
Условия акции
ИДЕАЛЬНЫЙ
35 000 ₽ в месяц
Почему это выгодно
Кому подходит
Только для одного из счетов ИП, зарегистрированного не более 90 дней назад
С ограничениями
С ограничений
Только для компаний с выручкой от 60 000 000 ₽ в год и групп компаний до 5 участников, один из которых с такой выручкой.
Для остальных — по индивидуальному запросу.
Общие условия
Всё самое важное — бесплатно на любом тарифе
Регистрация ИП и ООО
Открытие расчётных и валютных счетов
Интернет-банк и мобильное приложение
Электронный документооборот
Любое количество платёжек юрлицам и ИП
Рассчитать выгоду

Налоговые и бюджетные платежи
Email-уведомления об операциях и пуш-уведомления для устройств на Android
Выпуск виртуальных карт
Входящие переводы и платежи по реквизитам от юридических и физических лиц
Переводы физлицам
До 150 000 ₽ в месяц бесплатно
Комиссия в 500 ₽ увеличит лимит ещё на 15 000 ₽
До 400 000 ₽ в месяц бесплатно
Комиссия в 2 100 ₽ увеличит лимит ещё на 75 000 ₽
До 1 000 000 ₽ в месяц бесплатно
Комиссия в 3 300 ₽ увеличит лимит ещё на 150 000 ₽
До 10 000 000 ₽ в месяц бесплатно
Далее по согласованию
Переводы через зарплатный проект на карты банков МТС Банк и Банк Хоум Кредит
—
Бесплатно
Бесплатно
Бесплатно
Переводы через зарплатный проект физлицам на карты других банков
—
0,65%
Бесплатно
Бесплатно
Выплаты дивидендов, возврат займов, платежи самозанятым
Входит в лимиты переводов физлицам
Входит в лимиты переводов физлицам
Бесплатно
Бесплатно
Снятие наличных
За каждые 10 000 ₽
комиссия 350 ₽
До 50 000 ₽ в месяц бесплатно
Комиссия в 1 500 ₽ увеличит лимит ещё на 50 000 ₽
До 300 000 ₽ в месяц бесплатно
Комиссия в 2 500 ₽ увеличит лимит ещё на 100 000 ₽
До 5 000 000 ₽ в месяц бесплатно
Далее по согласованию
Пополнение счёта наличными или с карты другого банка
За каждые 10 000 ₽ комиссия 80 ₽
До 100 000 ₽ в месяц бесплатно
Комиссия в 350 ₽ увеличит лимит ещё на 50 000 ₽
До 600 000 ₽ в месяц бесплатно
Комиссия в 600 ₽ увеличит лимит ещё на 100 000 ₽
До 1 000 000 ₽ в месяц бесплатно
Комиссия в 500 ₽ увеличит лимит ещё на 100 000 ₽
Выпуск и доставка пластиковых карт
Бесплатно
одна пластиковая карта на одну организацию
500 ₽
за каждую следующую карту
Бесплатно
одна пластиковая карта на одну организацию
500 ₽
за каждую следующую карту
Бесплатно
одна пластиковая карта на одну организацию
500 ₽
за каждую следующую карту
Бесплатно
одна пластиковая карта на одну организацию
500 ₽
за каждую следующую карту
Персональный менеджер
—
—
—
Смс-уведомления об операциях
200 ₽
в месяц
300 ₽
в месяц
Бесплатно
Бесплатно
Доставка документов на бумаге
1 000 ₽
По России
5 000 ₽
За границу
1 000 ₽
По России
5 000 ₽
За границу
Бесплатно
2 доставки по России
5 000 ₽
За границу
Бесплатно
По России
5 000 ₽
За границу
Программа лояльности
Кешбэк начисляется в баллах. 1 балл = 1 рубль. Подключайте кешбэк в интернет-банке и превращайте баллы в реальные деньги или товары и сертификаты от наших партнёров.
Кешбэк за уплату налогов.
Действует на ЕНП.
—
5%
Акция до 29.05.24
5%
Акция до 29.05.24
—
Кешбэк на остатки по счетам
7% годовых
при покупках по картам больше 30 000 ₽% годовых
если траты меньше
7% годовых
при покупках по картам больше 30 000 ₽
3% годовых
если траты меньше
7% годовых
при покупках по картам больше 30 000 ₽
3% годовых
если траты меньше
7% годовых
при покупках по картам больше 30 000 ₽
3% годовых
если траты меньше
Лимит начисления баллов в месяц
2 000
3 000
5 000
25 000
Базовая бухгалтерия
Бесплатно на любом тарифе
Для ИП на УСН «Доходы» без сотрудников
Рассчитает и оптимизирует сумму налогов и взносов, а ещё заранее напомнит об уплате
Сформирует декларацию, чтобы вы могли отправить её в ФНС

Учтёт валютные операции в соответствии с законодательством
Бухгалтерия «Всё включено»
19 900 ₽ в год на любом тарифе
ИП на УСН «Доходы», «Доходы минус Расходы», патенте, без сотрудников
Включает «Базовую бухгалтерию»
Поможет в сложных вопросах: профессиональный бухгалтер всегда на связи
Составит грамотный ответ на письмо или сверку для налоговой
Проверит задолженность или переплаты по налогам и взносам

Накопит средства с ваших доходов и уплатит налоги и взносы точно в срок
Учтёт комиссию Ozon, Wildberries и Яндекс Маркет при расчёте налогов
Эксперт подберёт оптимальную систему налогообложения
Обеспечит безболезненный переход из других бухгалтерских сервисов
Финансы
Фонды
Бесплатно
в неограниченном количестве
Бесплатно
в неограниченном количестве
Бесплатно
в неограниченном количестве
Бесплатно
в неограниченном количестве
Безопасность бизнеса
Бесплатно на любом тарифе
Комплаенс-аналитика
Комплаенс-ассистент

Рекомендации в платежах
ВЭД
Бесплатно на любом тарифе
Открытие счёта в иностранной валюте
Консультации по внешнеторговым контрактам и валютному законодательству РФ
Внесение изменений в сведения учётного контракта
Информирование о событиях валютного контроля и защита от штрафов
Постановка контракта на учёт

Подготовка платежа и справки о подтверждающих документах
Перевод контракта с иностранного на русский язык
Снятие контракта с учёта
Валютные инвойсы
Валютный платёж в другие банки в любой валюте кроме тенге
45 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
35 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
25 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
20 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
Валютный платёж в тенге в другие банки
50 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
45 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
40 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
35 $ США
Конвертируем сумму в рубли по курсу ЦБ на дату платежа
Спред к рынку по юаню
15 копеек
10 копеек
8 копеек
Индивидуально
Таможенное декларирование
9 000 ₽
за оформление основного (первого) листа декларации
далее 450 ₽
за оформление каждого следующего листа декларации
9 000 ₽
за оформление основного (первого) листа декларации
далее 450 ₽
за оформление каждого следующего листа декларации
9 000 ₽
за оформление основного (первого) листа декларации
далее 450 ₽
за оформление каждого следующего листа декларации
9 000 ₽
за оформление основного (первого) листа декларации
далее 450 ₽
за оформление каждого следующего листа декларации
Госзакупки
Бесплатно на любом тарифе
Открытие специального счёта для участия в госзакупках

Вернём до 2% годовых от суммы остатка по спецсчёту. Зачисляем ежемесячно.
Ведение специального счёта
Бесплатно
Бесплатно
Бесплатно
Бесплатно
Регистрация в ЕРУЗ
2 000 ₽
1 200 ₽
Акция до 31.03
2 000 ₽
1 200 ₽
Акция до 31.03
2 000 ₽
1 200 ₽
Акция до 31.03
2 000 ₽
1 200 ₽
Акция до 31.03
Розница
Бесплатно на любом тарифе
Предоставление (выкуп или рассрочка) и настройка терминала
Регистрация в процессинговом центре

Загрузка ключей и лицензий
Доставка терминала
Онлайн-зачисления по торговому эквайрингу
500 ₽ в месяц
500 ₽ в месяц
350 ₽ в месяц
Бесплатно
Терминал
16 000 ₽ единоразово
или 1 600 ₽ в месяц
16 000 ₽ единоразово
или 1 600 ₽ в месяц
16 000 ₽ единоразово
или 1 600 ₽ в месяц
16 000 ₽ единоразово
или 1 600 ₽ в месяц
Подключение терминала клиента
2 500 ₽
2 500 ₽
2 500 ₽
2 500 ₽
Ставки по торговому эквайрингу
Фаст-фуд
2,5%
от суммы каждой операции
2,3%
от суммы каждой операции
1,4%
от суммы каждой операции
Индивидуально
Супермаркеты и бакалейные магазины
2,5%
от суммы каждой операции
2,3%
от суммы каждой операции
1,7%
от суммы каждой операции
Индивидуально
Турагентства
2,5%
от суммы каждой операции
2,3%
от суммы каждой операции
1,7%
от суммы каждой операции
Индивидуально
Прочие торговые точки
2,5%
от суммы каждой операции
2,3%
от суммы каждой операции
2,1%
от суммы каждой операции
Индивидуально
Комиссия за приём платежей через QR-код
Максимальная сумма транзакции — 1 000 000 ₽
Государственные платежи
0%
от суммы каждой операции
0%
от суммы каждой операции
0%
от суммы каждой операции
0%
от суммы каждой операции
Медицинские услуги, образование, ЖКХ, транспорт, связь, почта, благотворительность
0,4%
от суммы каждой операции
0,4%
от суммы каждой операции
0,4%
от суммы каждой операции
0,4%
от суммы каждой операции
Товары повседневного спроса, лекарства, БАДы
0,4%
от суммы каждой операции
0,4%
от суммы каждой операции
0,4%
от суммы каждой операции
0,4%
от суммы каждой операции
Прочие товары и услуги
0,7%
от суммы каждой операции
0,7%
от суммы каждой операции
0,7%
от суммы каждой операции
0,7%
от суммы каждой операции
Подключить
Подключить
Подключить
Подключить""")
