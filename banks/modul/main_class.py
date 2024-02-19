from banks.modul.pdf_file import PdfFile


class Modul:

    def __init__(self, modul_configs):

        self.pdf_file = PdfFile(url=modul_configs['pdf_file'])

    async def job(self):

        await self.pdf_file.parse()
        await self.pdf_file.compare()



