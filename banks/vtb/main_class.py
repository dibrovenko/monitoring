from banks.vtb.pdf_file import PdfFile



class Vtb:

    def __init__(self, vtb_configs):

        self.pdf_file = PdfFile(url=vtb_configs['pdf_file'])

    async def job(self):
        await self.pdf_file.parse()
        await self.pdf_file.compare()



