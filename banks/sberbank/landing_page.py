import asyncio
import configparser
import os
import pandas as pd
import uuid
from pathlib import Path


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service

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

        # Инициализация веб-драйвера и открываем страницу
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("window-size=1400,2100")
        s = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=s, options=chrome_options)
        driver.get(self.url_parse)

        wait = WebDriverWait(driver, 30)
        wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "RubTariffsCardList__item")))
        await asyncio.sleep(10)

        # Нахождение элемента с помощью CSS-селектора
        try:
            driver.find_element(By.CSS_SELECTOR, ".MlchtUI-Col.MlchtUI-Col_sm_size_1 button.MlchtUI-Button").click()
        except:
            pass
        await asyncio.sleep(2)
        driver.find_element(By.CLASS_NAME, 'TariffCardLink').click()
        await asyncio.sleep(2)

        # Создание списка для хранения данных
        data = []
        self.meta_data = " "

        # Вводим первую колонку:
        column = ["Название тарифа", "Цена тарифа"]
        items = driver.find_elements(By.CLASS_NAME, "RubTariffsCardList__item")
        divs = items[0].find_elements(By.CLASS_NAME, "TariffServices__item")
        for div in divs:
            column.append(div.find_element(By.CLASS_NAME, "TariffServices__title").text)
        divs = items[0].find_elements(By.CLASS_NAME, "TariffsComissions__title")
        for div in divs:
            column.append(div.text)
        data.append(column)

        # парсинг основных данных
        titles_add = ["Для ИП", "Для ООО"]
        types_add = ["СТАНДАРТ", "ДВОЙНОЙ"]
        for title_add in titles_add:
            double_button_list = []

            # переходим на страницу Для ООО
            if title_add == "Для ООО":
                tab_list = driver.find_element(By.CLASS_NAME, 'TabList')
                button_ooo = tab_list.find_element(By.XPATH, "//button[contains(text(), 'Для ООО')]")
                button_ooo.click()
                wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'TariffCardLink')))
                # нажимаем показать полностью
                driver.find_element(By.CLASS_NAME, 'TariffCardLink').click()
                await asyncio.sleep(10)

            for type_add in types_add:
                self.meta_data += f'Страница {title_add} и выбраны тарифы {type_add} \n ' \
                                  f'{driver.find_element(By.CLASS_NAME, "RublePackages").text} \n \n ' \
                                  f'###################################################################################'

                items = driver.find_elements(By.CLASS_NAME, "RubTariffsCardList__item")
                # Перебор каждого элемента и извлечение данных
                for item in items:
                    title_name = item.find_element(By.CLASS_NAME, "TariffsCardHead__title").text
                    title_text = item.find_element(By.CLASS_NAME, "TariffsCardHead__text").text
                    price_title = item.find_element(By.CLASS_NAME, "TarrifsCardPrice__title").text
                    price_text = item.find_element(By.CLASS_NAME, "TarrifsCardPrice__text").text
                    title = f"{title_add} '{title_name}'. \n {title_text}"
                    price = f"{price_title} \n {price_text}"
                    column = [title, price]

                    divs = item.find_elements(By.CLASS_NAME, "TariffServices__item")
                    for div in divs:
                        column.append(div.text)

                    divs = item.find_elements(By.CLASS_NAME, "TariffsComissions__list")
                    divs2 = item.find_elements(By.CLASS_NAME, "TariffsComissions__title")
                    for index, div in enumerate(divs):
                        column.append(f"{divs2[index].text} \n {div.text}")

                    # нажатие тарифа двойной
                    try:
                        item.find_element(By.XPATH, './div/div[1]/div/div/button[2]').click()
                        await asyncio.sleep(2)
                    except:
                        pass

                    # добавляем в дату
                    if column not in data:
                        if type_add == "ДВОЙНОЙ":
                            column[0] = f"{type_add} {column[0]}"
                        data.append(column)

        # Закрытие веб-драйвера после завершения работы с ним
        driver.quit()

        transposed_data = list(zip(*data))
        df = pd.DataFrame(transposed_data)

        # Save the Excel file
        current_path = os.getcwd()
        file_name = str(uuid.uuid4())[:15]
        self.link_new_file = os.path.join(current_path, f'banks/sberbank/data/{file_name}.xlsx')
        # Запись DataFrame в Excel-файл
        df.to_excel(self.link_new_file, index=False)

    @async_exception_handler
    async def compare(self):
        change_from_db = await AsyncORM.select_changes_for_compare(
            bank=Banks.sberbank, typechanges=TypeChanges.landing_page, lim=1)
        # проверяем есть ли записи в бд
        if change_from_db:
            excel_diff_dict = excel_diff(
                path_OLD=Path(change_from_db[0].link_new_file),
                path_NEW=Path(self.link_new_file),
                path_to_save=f'{os.getcwd()}/banks/sberbank/data')
            # нашли изменения
            if self.meta_data != change_from_db[0].meta_data or not excel_diff_dict["Bool_Change"]:

                # создаем html файл для description
                file_name_html = str(uuid.uuid4())[:15]
                compare_strings(
                    old_str=change_from_db[0].meta_data,
                    new_str=self.meta_data,
                    filename_html=os.path.join(os.getcwd(), f'banks/sberbank/data/{file_name_html}.html')
                )
                # сохраняем в базу изменения
                self.change_to_db = Changes(
                    bank=Banks.sberbank,
                    typechanges=TypeChanges.landing_page,
                    meta_data=self.meta_data,
                    link_new_file=self.link_new_file,
                    link_old_file=change_from_db[0].link_new_file,
                    link_compare_file=excel_diff_dict["compare_path"],
                    title=None,
                    description=f"Сначала смотрим excel файлы,"
                                f" если недостаточно переходим по ссылке: {SITE_URL}/get_compare_html/sberbank/{file_name_html}.html \n"
                                f"Сообщение от функции, которая сравнивает excel: {excel_diff_dict['description']}"
                )
                await AsyncORM.insert_change(class_change=self.change_to_db)

            else:
                os.remove(self.link_new_file)
                os.remove(excel_diff_dict["compare_path"])

        else:
            self.change_to_db = Changes(
                        bank=Banks.sberbank,
                        typechanges=TypeChanges.landing_page,
                        meta_data=self.meta_data,
                        link_new_file=self.link_new_file,
                        title="Первая запись в базу",
                        description=None
                    )
            await AsyncORM.insert_change(class_change=self.change_to_db)
            #os.remove(self.link_new_file)
