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
        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options, service=s)

        driver.get(self.url_parse)
        await asyncio.sleep(3)

        # Находим элемент с классом "tariffs-section_tariffsSection__bdNb1"
        first_compare = driver.find_element(By.CLASS_NAME, 'tariffs-section_tariffsSection__bdNb1')
        self.meta_data = first_compare.text

        # Create a new Excel workbook
        workbook = Workbook()
        sheet = workbook.active

        # Заголовк + первая строчка таблицы
        sheet.append(["Что входит", "Тариф 1", "Тариф 2", "Тариф 3", "Тариф 4"])
        #header_table = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div[2]/div/div/div/div[3]')
        header_table = driver.find_element(By.XPATH, '// *[ @ id = "__next"] / div[1] / main / div[1] / div / div / div / div[3]')

        div_blocks = header_table.find_elements(By.CSS_SELECTOR, 'div.p-2.tariffs-common_item__iebKT')
        data_first_column = ["_"]
        for div_block in div_blocks:
            data_first_column.append(div_block.text)
        sheet.append(data_first_column)

        # Assuming the table is inside a div with class "tariffs-row-desktop_row__9ZMRZ"
        table_rows = driver.find_elements(By.CSS_SELECTOR, '.tariffs-row-desktop_row__9ZMRZ')
        # Extract data from each row of the table and write it to Excel
        for i, row in enumerate(table_rows):
            # Extracting text from each cell in the row
            row_data: list[str] = [cell.text for cell in row.find_elements(By.CSS_SELECTOR, 'div.pl-2.pr-2')]
            # Нахождение элемента с классом "mobileDescriptionCard"
            elements = row.find_elements(By.CLASS_NAME, "mobileDescriptionCard")
            if elements:
                common_column = []
                # Получение текста из элемента
                for element in elements:
                    common_column.append(f'{element.text} \n')
                row_data.append(' '.join(common_column))
            else:
                try:
                    common_row = row.find_element(By.CLASS_NAME, "mobileDescriptionCardText")
                    row_data.append(common_row.text)
                except:
                    pass

            # Writing data to the Excel sheet
            sheet.append(row_data)

        # Save the Excel file
        current_path = os.getcwd()
        file_name = str(uuid.uuid4())[:15]
        self.link_new_file = os.path.join(current_path, f'banks/tochka/data/{file_name}.xlsx')
        workbook.save(self.link_new_file)

        # Close the web driver
        driver.quit()

    @async_exception_handler
    async def compare(self):
        change_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.tochka, typechanges=TypeChanges.landing_page, lim=1)
        # проверяем есть ли записи в бд
        if change_from_db:
            excel_diff_dict = excel_diff(
                path_OLD=Path(change_from_db[0].link_new_file),
                path_NEW=Path(self.link_new_file),
                path_to_save=f'{os.getcwd()}/banks/tochka/data')
            # нашли изменения
            if self.meta_data != change_from_db[0].meta_data or not excel_diff_dict["Bool_Change"]:

                # создаем html файл для description
                file_name_html = str(uuid.uuid4())[:15]
                compare_strings(
                    old_str=change_from_db[0].meta_data,
                    new_str=self.meta_data,
                    filename_html=os.path.join(os.getcwd(), f'banks/tochka/data/{file_name_html}.html')
                )
                # сохраняем в базу изменения
                self.change_to_db = Changes(
                    bank=Banks.tochka,
                    typechanges=TypeChanges.landing_page,
                    meta_data=self.meta_data,
                    link_new_file=self.link_new_file,
                    link_old_file=change_from_db[0].link_new_file,
                    link_compare_file=excel_diff_dict["compare_path"],
                    title=None,
                    description=f"Сначала смотрим excel файлы,"
                                f" если недостаточно переходим по ссылке: {SITE_URL}/get_compare_html/tochka/{file_name_html}.html \n"
                                f"Сообщение от функции, которая сравнивает excel: *{excel_diff_dict['description']}*"
                )
                await AsyncORM.insert_change(class_change=self.change_to_db)

            else:
                os.remove(self.link_new_file)
                os.remove(excel_diff_dict["compare_path"])

        else:
            self.change_to_db = Changes(
                        bank=Banks.tochka,
                        typechanges=TypeChanges.landing_page,
                        meta_data=self.meta_data,
                        link_new_file=self.link_new_file,
                        title="Первая запись в базу",
                        description=None
                    )
            await AsyncORM.insert_change(class_change=self.change_to_db)
            #os.remove(self.link_new_file)

            """class Changes(Base):
                __tablename__ = "changes"

                number: Mapped[intpk]
                bank: Mapped[Banks]
                typechanges: Mapped[TypeChanges]
                meta_data: Mapped[str | None]
                link_new_file: Mapped[str | None]
                link_old_file: Mapped[str | None]
                link_compare_file: Mapped[str | None]
                title: Mapped[str | None]
                description: Mapped[str | None]
                date: Mapped[created_at]"""
