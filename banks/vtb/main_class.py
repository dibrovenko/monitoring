from banks.vtb.pdf_file import PdfFile
from banks.vtb.news import News
from banks.vtb.landing_page import LandingPage
from banks.vtb.pdf_file_from_langing_page import PdfFile_from_langing_page



class Vtb:

    def __init__(self, vtb_configs):

        self.pdf_file = PdfFile(url=vtb_configs['pdf_file'])
        self.news = News(url=vtb_configs['news'])
        self.landing_page = LandingPage(url=vtb_configs['landing_page'])
        self.pdf_file_from_langing_page = PdfFile_from_langing_page(url=vtb_configs['pdf_file_from_landing_page'])

    async def job(self):
        await self.pdf_file.parse()
        await self.pdf_file.compare()

        await self.news.parse()
        await self.news.compare()

        await self.landing_page.parse()
        await self.landing_page.compare()

        await self.pdf_file_from_langing_page.parse()
        await self.pdf_file_from_langing_page.compare()



