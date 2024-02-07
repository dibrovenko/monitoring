import asyncio
import os
import uuid
import requests
import pikepdf

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges
from banks.common_func.screenshots import screenshot_page
from banks.config import chrome_driver_path


class Promotion1:

    def __init__(self, url):
        self.url_parse = url
        self.titles = []
        self.descriptions = []
        self.new_links = []
        self.meta_datas = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):
        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        # Инициализация веб-драйвера и открываем страницу
        driver = webdriver.Chrome(service=s)
        driver.get(self.url_parse)
        await asyncio.sleep(5)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        driver.quit()

        # Finding all the <a> tags within <div> tags with class "aHfBM"
        links = soup.find_all("div", class_="aHfBM")

        # Extracting and printing the links and corresponding sizes
        for link in links:
            anchor_tag = link.find("a")
            if anchor_tag:
                href = anchor_tag.get("href")
                text = anchor_tag.get_text()

                # Download PDF and extract metadata
                pdf_filename = href.split("/")[-1]
                response = requests.get(href)
                with open(pdf_filename, 'wb') as f:
                    f.write(response.content)

                await asyncio.sleep(1)
                try:
                    pdf_compare = pikepdf.Pdf.open(pdf_filename)
                    meta_data = str(pdf_compare.docinfo)
                    self.titles.append(text)
                    self.new_links.append(href)
                    self.meta_datas.append(meta_data)
                except:
                    pass
                finally:
                    os.remove(pdf_filename)

    @async_exception_handler
    async def compare(self):
        await asyncio.sleep(2)
        changes_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.alfa, typechanges=TypeChanges.promotion1, lim=50)
        change_titles_from_dp = [item.title for item in changes_from_db]
        change_meta_datas_from_dp = [item.meta_data for item in changes_from_db]

        for index, title in enumerate(self.titles):
            # сравниваем метаданными с данными из бд
            if not self.meta_datas[index] in change_meta_datas_from_dp:

                # Download PDF
                pdf_download_path = f'{os.getcwd()}/banks/alfa/data/{str(uuid.uuid4())[:8]}.pdf'
                with open(pdf_download_path, 'wb') as f:
                    f.write(requests.get(self.new_links[index]).content)

                # Проверяем, содержитcя ли название схожие
                index_if_name = next((index for index, item in enumerate(change_titles_from_dp) if title in item), None)
                if index_if_name is not None:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.alfa,
                            typechanges=TypeChanges.promotion1,
                            meta_data=self.meta_datas[index],
                            link_new_file=pdf_download_path,
                            link_old_file=changes_from_db[index_if_name].link_new_file,
                            title=title,
                            description=f"Появилася акция с новыми метаданнами, подробнее тут: {self.new_links[index]}\n"
                                        f"Однако, существует акция с схожим названием:"
                                        f" {change_titles_from_dp[index_if_name]} \n"
                                        f"Cоветуем сравнивать pdf файлы тут: https://tools.pdf24.org/ru/compare-pdf"
                        )
                    )
                else:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.alfa,
                            typechanges=TypeChanges.promotion1,
                            meta_data=self.meta_datas[index],
                            link_new_file=pdf_download_path,
                            title=title,
                            description=f"Появилася акция с новыми метаданнами, подробнее тут: {self.new_links[index]}"
                        )
                    )

            elif not title in change_titles_from_dp:

                # Download PDF
                pdf_download_path = f'{os.getcwd()}/banks/alfa/data/{str(uuid.uuid4())[:8]}.pdf'
                with open(pdf_download_path, 'wb') as f:
                    f.write(requests.get(self.new_links[index]).content)

                index_from_dp = change_meta_datas_from_dp.index(self.meta_datas[index])
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.alfa,
                        typechanges=TypeChanges.promotion1,
                        meta_data=self.meta_datas[index],
                        link_new_file=pdf_download_path,
                        link_old_file=changes_from_db[index_from_dp].link_old_file,
                        title=title,
                        description=f"Появилась акция с аналогичными метаданными,"
                                    f" только название у нее было {change_titles_from_dp[index_from_dp]} \n"
                                    f"Но лучше перепроверить и  сравнивать pdf файлы"
                                    f" тут: https://tools.pdf24.org/ru/compare-pdf,"
                                    f" подробнее про акцию тут: {self.new_links[index]}\n"
                    )
                )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)