import asyncio
import configparser
import os
import time
import uuid
from pathlib import Path

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from openpyxl import Workbook

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
        self.meta_data = None
        self.change_to_db = None

    @async_exception_handler
    async def parse(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["0.0", "Тариф 1", "Тариф 2", "Тариф 3", "Тариф 4", "Тариф 5", "Тариф 6"])

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        # Инициализация веб-драйвера и открываем страницу
        driver = webdriver.Chrome(service=s)
        driver.get(self.url_parse)
        await asyncio.sleep(3)

        # Нахождение элемента по классу "b2soE a2soE"
        first_compare = driver.find_element(By.CSS_SELECTOR, "div.b2soE.a2soE")
        # Получение текста из найденного элемента
        self.meta_data = first_compare.text

        # Получение HTML-кода страницы
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Находим все элементы <a> внутри тегов <p>, которые содержат названия тарифов
        tariff_names = soup.find("div", class_="g3wxl").find_all("a", class_="a1cAc g1cAc c1cAc")
        excel_row = ["Добавить тариф"]
        # Выводим найденные названия тарифов
        for tariff in tariff_names:
            excel_row.append(tariff.text)
        ws.append(excel_row)

        # Находим все поддивы с классом "m2soE"
        divs_with_class_m2soE = soup.find("div", class_="m2soE")
        rows = divs_with_class_m2soE.find_all("div", class_="d3E_0")
        unic_first_column = []
        for row in rows:
            # Создаем список для текущей строки в Excel
            excel_row = []
            # Находим все элементы с классом "k30tm a3E_0 b3E_0"
            table_rows = row.find_all('div', class_='k30tm a3E_0 b3E_0')

            text = table_rows[0].find('p').text.strip()
            if text in unic_first_column:
                excel_row.append(f"{text} second")
            else:
                unic_first_column.append(str(text))
                excel_row.append(str(text))

            # Парсим таблицу и добавляем данные в список excel_row
            for row in table_rows[1:]:
                # Находим первый элемент <p> внутри текущей ячейки
                cell = row.find('p')
                # Проверяем, что элемент не None
                if cell:
                    text = cell.text.strip()
                    excel_row.append(str(text))
                else:
                    excel_row.append("No data available")
            # Добавляем строку в Excel-таблицу
            ws.append(excel_row)

        # Save the Excel file
        current_path = os.getcwd()
        file_name = str(uuid.uuid4())[:15]
        self.link_new_file = os.path.join(current_path, f'banks/alfa/data/{file_name}.xlsx')
        wb.save(self.link_new_file)
        # Close the web driver
        driver.quit()


    @async_exception_handler
    async def compare(self):
        change_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.alfa, typechanges=TypeChanges.landing_page, lim=1)
        # проверяем есть ли записи в бд
        if change_from_db:
            excel_diff_dict = excel_diff(
                path_OLD=Path(change_from_db[0].link_new_file),
                path_NEW=Path(self.link_new_file),
                path_to_save=f'{os.getcwd()}/banks/alfa/data')
            # нашли изменения
            if self.meta_data != change_from_db[0].meta_data or not excel_diff_dict["Bool_Change"]:

                # создаем html файл для description
                file_name_html = str(uuid.uuid4())[:15]
                compare_strings(
                    old_str=change_from_db[0].meta_data,
                    new_str=self.meta_data,
                    filename_html=os.path.join(os.getcwd(), f'banks/alfa/data/{file_name_html}.html')
                )
                # сохраняем в базу изменения
                self.change_to_db = Changes(
                    bank=Banks.alfa,
                    typechanges=TypeChanges.landing_page,
                    meta_data=self.meta_data,
                    link_new_file=self.link_new_file,
                    link_old_file=change_from_db[0].link_new_file,
                    link_compare_file=excel_diff_dict["compare_path"],
                    title=None,
                    description=f"Сначала смотрим excel файлы,"
                                f" если недостаточно переходим по ссылке: {SITE_URL}/get_compare_html/alfa/{file_name_html}.html \n"
                                f"Сообщение от функции, которая сравнивает excel: *{excel_diff_dict['description']}*"
                )
                await AsyncORM.insert_change(class_change=self.change_to_db)

            else:
                os.remove(self.link_new_file)
                os.remove(excel_diff_dict["compare_path"])

        else:
            self.change_to_db = Changes(
                        bank=Banks.alfa,
                        typechanges=TypeChanges.landing_page,
                        meta_data=self.meta_data,
                        link_new_file=self.link_new_file,
                        title="Первая запись в базу",
                        description=None
                    )
            await AsyncORM.insert_change(class_change=self.change_to_db)
            #os.remove(self.link_new_file)
