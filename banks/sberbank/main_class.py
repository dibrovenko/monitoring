from banks.sberbank.promotion1 import Promotion1
from banks.sberbank.news import News
from banks.sberbank.landing_page import LandingPage
from banks.sberbank.pdf_file import PdfFile



class Sberbank:

    def __init__(self, sberbank_configs):

        self.promotion1 = Promotion1(url=sberbank_configs['promotion1'])
        self.news = News(url=sberbank_configs['news'])
        self.landing_page = LandingPage(url=sberbank_configs['landing_page'])
        self.pdf_file = PdfFile(url=sberbank_configs['pdf_file'])

    async def job(self):

        await self.news.parse()
        await self.news.compare()

        await self.promotion1.parse()
        await self.promotion1.compare()

        await self.landing_page.parse()
        await self.landing_page.compare()

        await self.pdf_file.parse()
        await self.pdf_file.compare()



