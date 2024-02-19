from banks.open.pdf_file import PdfFile


class Open:

    def __init__(self, open_configs):

        self.pdf_file = PdfFile(url=open_configs['pdf_file'])

    async def job(self):

        await self.pdf_file.parse()
        await self.pdf_file.compare()



