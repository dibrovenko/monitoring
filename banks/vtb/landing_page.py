import asyncio
import configparser
import os
import time
import uuid
from pathlib import Path

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup

from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges
from banks.common_func.compare_excel import excel_diff
from banks.common_func.compare_text import compare_strings
from banks.config import chrome_driver_path


# Создайте экземпляр ConfigParser
config = configparser.ConfigParser()
# Прочитайте файл конфигурации
config.read('.env')
# Получите значения из файла конфигурации
SITE_URL = config.get('Settings', 'NGROK_TUNNEL_URL')


class LandingPage:

    def __init__(self, url):
        self.url_parse = url
        self.link_new_file = None
        self.change_to_db = None

    @async_exception_handler
    async def parse(self):
        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options, service=s)

        driver.get(self.url_parse)
        # Получение HTML-кода страницы
        await asyncio.sleep(15)
        driver.find_element(By.ID, "cookie-buttons").click()

        # Парсинг HTML-кода с помощью BeautifulSoup
        await asyncio.sleep(15)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        table_data = [["Пакеты услуг", "На старте", "Простой процент", "Все по делу", "Самое важное", "Все включено",
                       "Большие обороты"]]

        # заполняем первую колонку в таблице
        first_columns = []
        blocks = soup.find_all('div',
                               class_="layoutstyles__Box-table-comparison__sc-jkisi6-0 ioYWDg accordionstyles__BoxInner-table-comparison__sc-1d34irg-2 hYRSBs")
        for block in blocks:
            type = block.find('h2', {'itemprop': 'name',
                                     'class': 'typographystyles__Box-table-comparison__sc-14qzghz-0 kgetKi accordion-titlestyles__StyledHeading-table-comparison__sc-ncxzgq-1 dlSfVF'})
            columns = block.find_all('div', class_="cell-widestyles__CellBox-table-comparison__sc-1wno61a-0 qBBPH")
            for column in columns:
                first_column = f"'{type.text}' {column.text}"
                first_columns.append(first_column)

        rows = soup.find_all('div', class_="accordion-itemstyles__CellsWrapper-table-comparison__sc-ua9t90-1 iwIhDt")
        for i, row in enumerate(rows):
            data = [first_columns[i]]
            divs = row.find_all('div', recursive=False)
            for div in divs:
                match div['class'][1]:
                    case "gqGhdT":
                        data.append(div.text)
                    case "cJYLBI":
                        data.extend([div.text] * 2)
                    case "bNmhMb":
                        data.extend([div.text] * 3)
                    case "gEwACQ":
                        data.extend([div.text] * 4)
                    case _:
                        data.append(div.text)
            table_data.append(data)

        # Выбираем другие варианты тарифов для сравнения
        type_tarrifs = ["Самое важное", "На старте", "Простой процент", "Все по делу", "Все включено",
                        "Большие обороты"]
        try:
            block = driver.find_element(By.CSS_SELECTOR, '.chips-arraystyles__Box-foundation-kit__sc-ioaf20-0.gesjWs')
            for type_tarrif in type_tarrifs:
                block.find_element(By.XPATH, f"//li[contains(span/text(), '{type_tarrif}')]").click()
                await asyncio.sleep(1)
        except:
            # driver.find_element(By.CSS_SELECTOR,
            # "button.buttonstyles__Box-foundation-kit__sc-sa2uer-2.LnzIL.table-comparison-popupstyles__ButtonStyled-table-comparison__sc-1e7gpj6-0.gFsLUr").click()
            driver.find_element(By.CLASS_NAME, "buttonstyles__Box-foundation-kit__sc-sa2uer-2").click()
            await asyncio.sleep(7)
            try:
                driver.find_element(By.XPATH,
                                    '// *[ @ id = "modals-container"] / div[1] / div / div[2] / div / div / div[2] / div[5]').click()
                await asyncio.sleep(1)
                driver.find_element(By.XPATH,
                                    '// *[ @ id = "modals-container"] / div[1] / div / div[2] / div / div / div[2] / div[6]').click()
                await asyncio.sleep(1)
                driver.find_element(By.XPATH,
                                    '// *[ @ id = "modals-container"] / div[1] / div / div[2] / div / div / div[3] / button').click()
            except:
                driver.find_element(By.XPATH,
                                    '// *[ @ id = "modals-container"] / div[2] / div / div[2] / div / div / div[2] / div[5]').click()
                await asyncio.sleep(1)
                driver.find_element(By.XPATH,
                                    '//*[@id="modals-container"]/div[2]/div/div[2]/div/div/div[2]/div[6]').click()
                await asyncio.sleep(1)
                driver.find_element(By.XPATH,
                                    '//*[@id="modals-container"]/div[2]/div/div[2]/div/div/div[3]/button').click()

        # еще раз проходим по новым тарифам
        await asyncio.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all('div', class_="accordion-itemstyles__CellsWrapper-table-comparison__sc-ua9t90-1 iwIhDt")
        for i, row in enumerate(rows):
            data = []
            divs = row.find_all('div', recursive=False)
            for div in divs:
                match div['class'][1]:
                    case "gqGhdT":
                        data.append(div.text)
                    case "cJYLBI":
                        data.extend([div.text] * 2)
                    case "bNmhMb":
                        data.extend([div.text] * 3)
                    case "gEwACQ":
                        data.extend([div.text] * 4)
                    case _:
                        data.append(div.text)
            table_data[i + 1].extend(data)

        # Create DataFrame
        df = pd.DataFrame(table_data)

        # Save to Excel
        self.link_new_file = os.path.join(os.getcwd(), f'banks/vtb/data/{str(uuid.uuid4())[:15]}.xlsx')
        df.to_excel(self.link_new_file, index=False, header=False)
        driver.quit()

    @async_exception_handler
    async def compare(self):
        change_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.vtb, typechanges=TypeChanges.landing_page, lim=1)
        # проверяем есть ли записи в бд
        if change_from_db:
            excel_diff_dict = excel_diff(
                path_OLD=Path(change_from_db[0].link_new_file),
                path_NEW=Path(self.link_new_file),
                path_to_save=f'{os.getcwd()}/banks/vtb/data')
            # нашли изменения
            if not excel_diff_dict["Bool_Change"]:

                # сохраняем в базу изменения
                self.change_to_db = Changes(
                    bank=Banks.vtb,
                    typechanges=TypeChanges.landing_page,
                    link_new_file=self.link_new_file,
                    link_old_file=change_from_db[0].link_new_file,
                    link_compare_file=excel_diff_dict["compare_path"],
                    title=None,
                    description=f"Сначала смотрим excel файлы,"
                                f" если недостаточно переходим по ссылке и там загружаем файлы для сравнения: https://products.aspose.app/cells/comparison"
                                f" \nСообщение от функции, которая сравнивает excel файлы: *{excel_diff_dict['description']}.*"
                                f"\nСтраница откуда парсим информацию: {self.url_parse}"
                )
                await AsyncORM.insert_change(class_change=self.change_to_db)

            else:
                os.remove(self.link_new_file)
                os.remove(excel_diff_dict["compare_path"])

        else:
            self.change_to_db = Changes(
                        bank=Banks.vtb,
                        typechanges=TypeChanges.landing_page,
                        link_new_file=self.link_new_file,
                        title="Первая запись в базу",
                        description=None
                    )
            await AsyncORM.insert_change(class_change=self.change_to_db)
