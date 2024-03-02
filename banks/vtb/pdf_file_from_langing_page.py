import asyncio
import os
import uuid

import pikepdf
import requests
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges
from banks.config import chrome_driver_path


class PdfFile_from_langing_page:

    def __init__(self, url):
        self.url_parse = url
        self.titles = []
        self.web_links = []
        self.new_links = []
        self.changes_to_db = []

    #@async_exception_handler
    async def parse(self):

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options, service=s)

        driver.get(self.url_parse)
        # Получение HTML-кода страницы после загрузки
        await asyncio.sleep(10)
        url_pdf = driver.find_element(By.XPATH, '//*[@id="2"]/div/div/div/div[4]/div/a').get_attribute("href")
        driver.quit()

        headers = {"User-Agent": UserAgent().random}
        response = requests.get(url_pdf, headers=headers)
        response.raise_for_status()

        filename = os.path.join(os.getcwd(), f'banks/vtb/data/{str(uuid.uuid4())[:15]}.pdf')
        with open(filename, "wb") as file:
            file.write(response.content)
        self.titles.append("Полные условия пакетов услуг и дополнительных опций")
        self.web_links.append(url_pdf)
        self.new_links.append(filename)

    #@async_exception_handler
    async def compare(self):
        await asyncio.sleep(2)
        changes_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.vtb, typechanges=TypeChanges.pdf_file, lim=12)
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
                            bank=Banks.vtb,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            link_old_file=changes_from_db[index_if_name].link_new_file,
                            title=title,
                            description=f"Появился файл с новыми метаданнами,"
                                        f" но есть файл с похожим названием: {change_titles_from_dp[index_if_name]} \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} \n"
                                        f"Cоветуем сравнивать pdf файлы тут: https://tools.pdf24.org/ru/compare-pdf"
                        )
                    )
                else:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.vtb,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            title=title,
                            description=f"Появился файл с новыми метаданнами \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} "
                        )
                    )

            elif not title in change_titles_from_dp:
                index_from_dp = change_meta_datas_from_dp.index(str(pdf_compare.docinfo))
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.vtb,
                        typechanges=TypeChanges.pdf_file,
                        meta_data=str(pdf_compare.docinfo),
                        link_new_file=self.new_links[index],
                        link_old_file=changes_from_db[index_from_dp].link_new_file,
                        title=title,
                        description=f"Появился файл с такими же метаданнами,"
                                    f" только название у него было {change_titles_from_dp[index_from_dp]} \n"
                                    f"Но лучше перепроверить и  сравнивать pdf файлы"
                                    f" тут: https://tools.pdf24.org/ru/compare-pdf \n"
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
