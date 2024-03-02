import asyncio
from xvfbwrapper import Xvfb

from banks.tochka.main_class import Tochka
from banks.alfa.main_class import Alfa
from banks.sberbank.main_class import Sberbank
from banks.vtb.main_class import Vtb
from banks.raif.main_class import Raif
from banks.modul.main_class import Modul
from banks.mts.main_class import Mts
from banks.ozon.main_class import Ozon
from banks.open.main_class import Open

from banks.config import bank_configs

from banks.tochka.test import test_all as tochka_test
from banks.alfa.test import test_all as alfa_test
from banks.sberbank.test import test_all as sberbank_test
from banks.vtb.test import test_all as vtb_test
from banks.raif.test import test_all as raif_test
from banks.mts.test import test_all as mts_test

from db.core import AsyncORM


async def execute_once_daily():

    vdisplay = Xvfb()
    vdisplay.start()

    tochka = Tochka(tochka_configs=bank_configs['tochka'])
    await tochka.job()
    del tochka

    alfa = Alfa(alfa_configs=bank_configs['alfa'])
    await alfa.job()

    sberbank = Sberbank(sberbank_configs=bank_configs['sberbank'])
    await sberbank.job()

    vtb = Vtb(vtb_configs=bank_configs['vtb'])
    await vtb.job()

    raif = Raif(raif_configs=bank_configs['raif'])
    await raif.job()

    modul = Modul(modul_configs=bank_configs['modul'])
    await modul.job()

    mts = Mts(mts_configs=bank_configs['mts'])
    await mts.job()

    ozon = Ozon(ozon_configs=bank_configs['ozon'])
    await ozon.job()

    open = Open(open_configs=bank_configs['open'])
    await open.job()

    vdisplay.stop()


async def test_execute_once_daily():
    await AsyncORM.update_date()
    await asyncio.sleep(5)

    await tochka_test()

    await alfa_test()

    await sberbank_test()

    await vtb_test()

    await raif_test()

    await mts_test()
    pass