from banks.tochka.main_class import Tochka
from banks.config import bank_configs
from banks.tochka.test import test_all as tochka_test


async def execute_once_daily():
    tochka = Tochka(tochka_configs=bank_configs['tochka'])
    await tochka.job()

    # Удаление объекта tochka
    del tochka


async def test_execute_once_daily():
    await tochka_test()