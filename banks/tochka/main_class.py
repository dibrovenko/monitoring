from banks.tochka.news import News
from banks.tochka.pdf_file import PdfFile
from banks.tochka.promotion1 import Promotion1
from banks.tochka.landing_page import LandingPage


class Tochka:

    def __init__(self, tochka_configs):

        self.promotion1 = Promotion1(url=tochka_configs['promotion1'])
        self.news = News(url=tochka_configs['news'])
        self.landing_page = LandingPage(url=tochka_configs['landing_page'])
        self.pdf_file = PdfFile(url=tochka_configs['pdf_file'])

    async def job(self):
        await self.promotion1.parse()
        await self.promotion1.compare()

        await self.news.parse()
        await self.news.compare()

        await self.landing_page.parse()
        await self.landing_page.compare()

        await self.pdf_file.parse()
        await self.pdf_file.compare()



