from banks.raif.pdf_file import PdfFile


class Raif:

    def __init__(self, raif_configs):

        self.pdf_file = PdfFile(url=raif_configs['pdf_file'])

    async def job(self):

        await self.pdf_file.parse()
        await self.pdf_file.compare()



