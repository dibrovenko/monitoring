from banks.mts.pdf_file import PdfFile


class Mts:

    def __init__(self, mts_configs):

        self.pdf_file = PdfFile(url=mts_configs['pdf_file'])

    async def job(self):

        await self.pdf_file.parse()
        await self.pdf_file.compare()



