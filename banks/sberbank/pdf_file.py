import asyncio
import os

import pikepdf

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges
from banks.config import chrome_driver_path
from banks.common_func.pdf_download import selenium_pdf_down


class PdfFile:

    def __init__(self, url: list):
        self.url_parse_main = url[0]
        self.url_parse_dop = url[1]
        self.titles = []
        self.web_links = []
        self.new_links = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):

        link_new_file = await selenium_pdf_down(
            url=self.url_parse_main, download_path=f'{os.getcwd()}/banks/sberbank/data')
        self.titles.append("Основной файл с тарифами РКО")
        self.web_links.append(self.url_parse_main)
        self.new_links.append(link_new_file)

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options, service=s)

        driver.get(self.url_parse_dop)
        await asyncio.sleep(6)

        cities = ["Московская область", "Санкт-Петербург", "Москва"]
        for city in cities:
            # Находим кнопку "Сменить" в блоке с классом "tariffs-rko__region-info"
            change_button = driver.find_element(By.XPATH,
                                                "//div[@class='tariffs-rko__region-info']//button[contains(text(), 'Сменить')]")
            # Кликаем на кнопку "Сменить"
            change_button.click()
            await asyncio.sleep(4)

            # Находим кнопку "Санкт-Петербург" по тексту
            button = driver.find_element(By.XPATH, f"//span[text()='{city}']")
            button.click()
            await asyncio.sleep(4)

            block = driver.find_element(By.CLASS_NAME, "tariffs-rko").find_element(By.CLASS_NAME, "tariffs")
            button = block.find_element(By.XPATH, './div/div/div[1]/a')
            file_link = button.get_attribute("href")

            self.titles.append(f"Сбербанк на территории '{city}'")
            self.web_links.append(file_link)
        driver.quit()

        for index, city in enumerate(cities):
            link_new_file = await selenium_pdf_down(
                url=self.web_links[index+1], download_path=f'{os.getcwd()}/banks/sberbank/data')
            self.new_links.append(link_new_file)


    @async_exception_handler
    async def compare(self):
        await asyncio.sleep(2)
        changes_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.sberbank, typechanges=TypeChanges.pdf_file, lim=30)
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
                            bank=Banks.sberbank,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            link_old_file=changes_from_db[index_if_name].link_new_file,
                            title=title,
                            description=f"Появился файл с новыми метаданнами, "
                                        f" но есть файл с похожим названием: *{change_titles_from_dp[index_if_name]}* \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} \n"
                                        f"Cоветуем сравнивать pdf файлы тут: https://tools.pdf24.org/ru/compare-pdf"
                        )
                    )
                else:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.sberbank,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=str(pdf_compare.docinfo),
                            link_new_file=self.new_links[index],
                            title=title,
                            description=f"Появился файл с новыми метаданнами"
                                        f"Файл был скачен отсюда: {self.web_links[index]} \n"
                        )
                    )

            elif not title in change_titles_from_dp:
                index_from_dp = change_meta_datas_from_dp.index(str(pdf_compare.docinfo))
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.sberbank,
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
