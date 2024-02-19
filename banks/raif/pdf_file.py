import asyncio
import os
import uuid
import pikepdf
import requests
from fake_useragent import UserAgent

from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges


class PdfFile:

    def __init__(self, url: list):
        self.url_parse1 = url[0]
        self.url_parse2 = url[1]
        self.titles = []
        self.web_links = []
        self.new_links = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):
        headers = {"User-Agent": UserAgent().random}
        response = requests.get(self.url_parse1, headers=headers)
        response.raise_for_status()
        file_name = f'{os.getcwd()}/banks/raif/data/{uuid.uuid4()}.pdf'
        with open(file_name, "wb") as file:
            file.write(response.content)
        await asyncio.sleep(1)
        self.titles.append("Тарифы на расчетно-кассовое обслуживание для клиентов АО «Райффайзенбанк», расположенных"
                           " в следующих городах: Москва, города Московской области, Санкт-Петербург.")
        self.web_links.append(self.url_parse1)
        self.new_links.append(file_name)

        # вторая ссылка
        response = requests.get(self.url_parse2, headers=headers)
        response.raise_for_status()
        file_name = f'{os.getcwd()}/banks/raif/data/{uuid.uuid4()}.pdf'
        with open(file_name, "wb") as file:
            file.write(response.content)
        await asyncio.sleep(1)
        self.titles.append("ТАРИФНАЯ КНИГА на расчетно–кассовое обслуживание юридических лиц")
        self.web_links.append(self.url_parse2)
        self.new_links.append(file_name)


    @async_exception_handler
    async def compare(self):

        await asyncio.sleep(2)
        changes_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.raif, typechanges=TypeChanges.pdf_file, lim=4)

        change_titles_from_dp = [item.title for item in changes_from_db]
        change_meta_datas_from_dp = [item.meta_data for item in changes_from_db]

        for index, title in enumerate(self.titles):
            pdf_compare = pikepdf.Pdf.open(self.new_links[index])

            # сравниваем метаданными с данными из бд
            if not str(pdf_compare.docinfo) in change_meta_datas_from_dp:
                # Файл совершенно новый:

                # Проверяем, содержитcя ли название схожие
                index_if_name = next((index for index, item in enumerate(change_titles_from_dp) if title in item), None)
                if index_if_name is not None:

                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.raif,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            link_old_file=changes_from_db[index_if_name].link_new_file,
                            title=title,
                            description=f"Появился файл с новыми метаданнами,"
                                        f" но есть файл с похожим названием: *{change_titles_from_dp[index_if_name]}* \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} \n"
                                        f"Cоветуем сравнивать pdf файлы тут: https://tools.pdf24.org/ru/compare-pdf"
                        )
                    )
                else:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.raif,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            title=title,
                            description=f"Появился файл с новыми метаданнами \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} "
                        )
                    )

            else:
                try:
                    os.remove(self.new_links[index])
                except:
                    pass

        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)
