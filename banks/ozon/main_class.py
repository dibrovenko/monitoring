from banks.ozon.pdf_file import PdfFile


class Ozon:

    def __init__(self, ozon_configs):

        self.pdf_file = PdfFile(url=ozon_configs['pdf_file'])

    async def job(self):

        await self.pdf_file.parse()
        await self.pdf_file.compare()



