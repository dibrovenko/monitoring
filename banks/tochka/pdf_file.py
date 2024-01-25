import asyncio
import os

import pikepdf

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges
from banks.config import chrome_driver_path
from banks.common_func.pdf_download import selenium_pdf_down


class PdfFile:
    titles = []
    web_links = []
    new_links = []
    descriptions = []
    changes_to_db = []

    def __init__(self, url):
        self.url_parse = url

    @async_exception_handler
    async def parse(self):

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        # Инициализация драйвера
        driver = webdriver.Chrome(service=s)
        driver.get(self.url_parse)
        await asyncio.sleep(3)
        # Получение HTML-кода страницы после загрузки
        html = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html, 'html.parser')
        # Находим все блоки с файлами
        file_blocks = soup.find_all('div', class_='files-list-item_fileIcon__9jTfz')

        # Перебираем блоки и извлекаем названия и ссылки
        for block in file_blocks:
            file_type = block.find_previous('p', class_='h5 mb-4').text
            file_name = block.find_next('span', class_='files-list-item_fileName__nJ_El').text
            file_link = block.find_next('a')['href']

            # скачиваем pdf и сохраняем
            link_new_file = await selenium_pdf_down(
                url=f"https://tochka.com{file_link}",
                download_path=f'{os.getcwd()}/banks/tochka/data'
            )
            self.titles.append(file_name)
            self.descriptions.append(file_type)
            self.web_links.append(f"https://tochka.com{file_link}")
            self.new_links.append(link_new_file)
            """self.file_data[file_type].append({'name': file_name,
                                              'web_link': f"https://tochka.com{file_link}",
                                              'link_new_file': link_new_file})"""
        print(self.titles)
        print(self.descriptions)

    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.tochka, typechanges=TypeChanges.pdf_file, lim=8)
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
                            bank=Banks.tochka,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            link_old_file=changes_from_db[index_if_name].link_old_file,
                            title=title,
                            description=f"Тип этого файла: {self.descriptions[index]}. "
                                        f"Появился файл с новыми метаданнами,"
                                        f" но есть файл с похожим названием: {change_titles_from_dp[index_if_name]} \n"
                                        f"Cоветуем сравнивать pdf файлы тут: https://tools.pdf24.org/ru/compare-pdf"
                        )
                    )
                else:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.tochka,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            title=title,
                            description=f"Тип этого файла: {self.descriptions[index]}. "
                                        f"Появился файл с новыми метаданнами"
                        )
                    )

            elif not title in change_titles_from_dp:
                index_from_dp = change_meta_datas_from_dp.index(str(pdf_compare.docinfo))
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.tochka,
                        typechanges=TypeChanges.pdf_file,
                        meta_data=str(pdf_compare.docinfo),
                        link_new_file=self.new_links[index],
                        link_old_file=changes_from_db[index_from_dp].link_old_file,
                        title=title,
                        description=f"Тип этого файла: {self.descriptions[index]}. "
                                    f"Появился файл с такими же метаданнами,"
                                    f" только название у него было {change_titles_from_dp[index_from_dp]} \n"
                                    f"Но лучше перепроверить и  сравнивать pdf файлы"
                                    f" тут: https://tools.pdf24.org/ru/compare-pdf"
                    )
                )

            else:
                try:
                    os.remove(self.new_links[index])
                except:
                    pass

        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)
