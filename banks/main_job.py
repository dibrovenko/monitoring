from .tochka.main_class import Tochka
from .config import bank_configs


async def execute_once_daily():
    tochka = Tochka(tochka_configs=bank_configs['tochka'])
    await tochka.job()
