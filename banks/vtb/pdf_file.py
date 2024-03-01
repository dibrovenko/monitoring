import asyncio
import os
import shutil
import sys
import uuid

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
from banks.common_func.compare_excel import excel_diff_aspose


class PdfFile:

    def __init__(self, url):
        self.url_parse = url
        self.titles = []
        self.web_links = []
        self.meta_data = []
        self.new_links = []
        self.descriptions = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):
        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        # Инициализация драйвера
        driver = webdriver.Chrome(service=s)
        driver.get(self.url_parse)
        await asyncio.sleep(10)

        try:
            # Находим кнопку по классу и кликаем на нее
            button = driver.find_element(By.CSS_SELECTOR, '.buttonstyles__Box-foundation-kit__sc-sa2uer-2.LnzIL')
            button.click()
        except:
            pass
        await asyncio.sleep(10)
        button = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="undefined"]')[1]
        button.click()
        await asyncio.sleep(20)

        # Получение HTML-кода страницы
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.quit()

        titles = soup.find_all('div', class_='documentstyles__FilenameFull-foundation-kit__sc-1n9ldij-2')
        for title in titles:
            self.titles.append(title.text.strip())

        descriptions = soup.find_all('span',
                                     class_='typographystyles__Box-foundation-kit__sc-14qzghz-0 iItZBn documentstyles__Subtitle-foundation-kit__sc-1n9ldij-5 gVRGi')
        for des in descriptions:
            self.descriptions.append(des.text)

        hrefs = soup.find_all('a', {'aria-disabled': 'false',
                                    'class': 'linkstyles__Box-foundation-kit__sc-1obkn4x-1 cWnvnt documentstyles__StyledLink-foundation-kit__sc-1n9ldij-4 eUqJKW'})
        for i, link in enumerate(hrefs):
            web_link = f"https://www.vtb.ru{link['href']}"
            self.web_links.append(web_link)
            link_new_file = await download_excel(url=web_link)
            self.new_links.append(link_new_file)
            self.meta_data.append(self.descriptions[i] + " " + str(sys.getsizeof(open(link_new_file, 'rb').read())))

    @async_exception_handler
    async def compare(self):
        await asyncio.sleep(2)
        changes_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.vtb, typechanges=TypeChanges.pdf_file, lim=8)
        change_titles_from_dp = [item.title for item in changes_from_db]
        change_meta_datas_from_dp = [item.meta_data for item in changes_from_db]

        for index, title in enumerate(self.titles):

            # сравниваем метаданными с данными из бд
            if not self.meta_data[index] in change_meta_datas_from_dp:
                # Файл совершенно новый:

                # Проверяем, содержитcя ли название схожие
                index_if_name = next((index for index, item in enumerate(change_titles_from_dp) if title in item), None)
                if index_if_name is not None:
                    apose_compare = await excel_diff_aspose(file_path1=self.new_links[index],
                                                            file_path2=changes_from_db[index_if_name].link_new_file)
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.vtb,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=self.meta_data[index],
                            link_new_file=self.new_links[index],
                            link_old_file=changes_from_db[index_if_name].link_new_file,
                            title=title,
                            description=f"{self.descriptions[index]}. "
                                        f"Появился файл с новыми метаданнами,"
                                        f" но есть файл с похожим названием: *{change_titles_from_dp[index_if_name]}* \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} \n"
                                        f"Страница, на которой сравнили файлы: {apose_compare} \n"
                                        f"Если ссылка устарела, то сравни самостоятельно здесь:"
                                        f" https://products.aspose.app/cells/ru/comparison"
                        )
                    )
                else:
                    self.changes_to_db.append(
                        Changes(
                            bank=Banks.vtb,
                            typechanges=TypeChanges.pdf_file,
                            meta_data=self.meta_data[index],
                            link_new_file=self.new_links[index],
                            title=title,
                            description=f"{self.descriptions[index]}. "
                                        f"Появился файл с новыми метаданнами \n"
                                        f"Файл был скачен отсюда: {self.web_links[index]} "
                        )
                    )

            elif not title in change_titles_from_dp:
                index_from_dp = change_meta_datas_from_dp.index(self.meta_data[index])
                apose_compare = await excel_diff_aspose(file_path1=self.new_links[index],
                                                        file_path2=changes_from_db[index_from_dp].link_new_file)
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.vtb,
                        typechanges=TypeChanges.pdf_file,
                        meta_data=self.meta_data[index],
                        link_new_file=self.new_links[index],
                        link_old_file=changes_from_db[index_from_dp].link_new_file,
                        title=title,
                        description=f"{self.descriptions[index]}. "
                                    f"Появился файл с такими же метаданнами,"
                                    f" только название у него было *{change_titles_from_dp[index_from_dp]}* \n"
                                    f"Но лучше перепроверить и посмотреть сравнение файлов тут: {apose_compare} \n"
                                    f"Если ссылка устарела, то сравни самостоятельно здесь:"
                                    f" https://products.aspose.app/cells/ru/comparison"
                                    f" Файл был скачен отсюда: {self.web_links[index]} "
                    )
                )

            else:
                try:
                    os.remove(self.new_links[index])
                except:
                    pass

        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)


#вспомгательная функция, КОСТЫЛЬ
async def download_excel(url: str) -> str:
    download_path = f'{os.getcwd()}/banks/vtb/data/test_data'
    # Удаление папки dataset, если она существует
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    # Создание папки dataset
    os.mkdir(download_path)

    # Создаем экземпляр браузера с настройками и указываем путь до драйвера
    s = Service(executable_path=chrome_driver_path)
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {'download.default_directory': download_path})
    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.get(url)
    # Ждем некоторое время для загрузки страницы
    await asyncio.sleep(3)
    driver.quit()

    # Поиск единственного файла в папке dataset и переименование его
    files = os.listdir(download_path)
    old_name = files[0]
    new_name = f'{os.getcwd()}/banks/vtb/data/{uuid.uuid4()}.xlsx'  # Здесь можно указать новое имя файла
    os.rename(os.path.join(download_path, old_name), os.path.join(download_path, new_name))
    return new_name
