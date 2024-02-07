from banks.alfa.news import News
from banks.alfa.landing_page import LandingPage
from banks.alfa.promotion1 import Promotion1
from banks.alfa.pdf_file import PdfFile


class Alfa:

    def __init__(self, alfa_configs):
        self.news = News(url=alfa_configs['news'])
        self.landing_page = LandingPage(url=alfa_configs['landing_page'])
        self.promotion1 = Promotion1(url=alfa_configs['promotion1'])
        self.pdf_file = PdfFile(url=alfa_configs['pdf_file'])

    async def job(self):
        await self.news.parse()
        await self.news.compare()

        await self.landing_page.parse()
        await self.landing_page.compare()

        await self.promotion1.parse()
        await self.promotion1.compare()

        await self.pdf_file.parse()
        await self.pdf_file.compare()




