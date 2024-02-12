import asyncio

from banks.tochka.main_class import Tochka
from banks.alfa.main_class import Alfa
from banks.sberbank.main_class import Sberbank
from banks.vtb.main_class import Vtb
from banks.config import bank_configs
from banks.tochka.test import test_all as tochka_test
from banks.alfa.test import test_all as alfa_test
from banks.sberbank.test import test_all as sberbank_test
from banks.vtb.test import test_all as vtb_test
from db.core import AsyncORM


async def execute_once_daily():

    tochka = Tochka(tochka_configs=bank_configs['tochka'])
    await tochka.job()

    alfa = Alfa(alfa_configs=bank_configs['alfa'])
    await alfa.job()

    sberbank = Sberbank(sberbank_configs=bank_configs['sberbank'])
    await sberbank.job()

    vtb = Vtb(vtb_configs=bank_configs['vtb'])
    await vtb.job()
    # Удаление объекта tochka
    del tochka


async def test_execute_once_daily():
    await AsyncORM.update_date()
    await asyncio.sleep(5)
    await tochka_test()
    await alfa_test()
    await sberbank_test()
    await vtb_test()