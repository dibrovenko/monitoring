import asyncio
import uuid

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

from banks.common_func.except_handlers import async_exception_handler
from db.core import AsyncORM
from db.models import Banks, Changes, TypeChanges
from banks.common_func.screenshots import screenshot_page
from banks.config import chrome_driver_path


class News:

    def __init__(self, url):
        self.url_parse = url
        self.titles = []
        self.descriptions = []
        self.links = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        # Инициализация драйвера
        driver = webdriver.Chrome(service=s)
        driver.get(self.url_parse)
        # Находим кнопку по классу и кликаем на нее
        """button = driver.find_element(By.CSS_SELECTOR, '.buttonstyles__Box-foundation-kit__sc-sa2uer-2.LnzIL')
        button.click()"""
        await asyncio.sleep(15)
        driver.find_element(By.ID, "cookie-buttons").click()
        await asyncio.sleep(6)

        # Получение HTML-кода страницы
        html = driver.page_source
        driver.quit()

        # Парсинг HTML-кода с помощью BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        elements = soup.find("div", class_="tabs-layoutstyles__TabContentContainer-foundation-kit__sc-hj413w-2 kkwApA")
        elements2 = elements.find("div", class_="tabstyles__TabsContainer-foundation-kit__sc-1hmeyb5-0 lsFZh")
        elements3 = elements2.find_all("div",
                                       class_="accordionstyles__RelativeContainer-accordion__sc-1d34irg-0 ifvRxF")
        for el in elements3:
            title = el.find('h2', {'itemprop': 'name',
                                   'class': 'typographystyles__Box-accordion__sc-14qzghz-0 fPxqPE accordion-titlestyles__StyledHeading-accordion__sc-ncxzgq-1 kYfvYP'})
            description = el.find("div",
                                  class_="markdownstyles__StyledReactMarkdown-foundation-kit__sc-v45gkz-0 dnDYtR service-packages-tablestyles__StyledMarkdown-service-packages-table__sc-p7ct8d-10 eCUdyZ")
            self.titles.append(title.text)
            self.descriptions.append(description.text)
            self.links.append(self.url_parse)

    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(bank=Banks.vtb, typechanges=TypeChanges.news)
        change_titles_from_dp = [item.title for item in changes_from_db]
        for index, title in enumerate(self.titles):
            if not title in change_titles_from_dp:
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.vtb,
                        typechanges=TypeChanges.news,
                        # meta_data=self.links[index], - специально
                        link_new_file=await screenshot_page(url=self.links[index],
                                                            file_name=f'{uuid.uuid4()}.png', file_name_bank='vtb'),
                        title=title,
                        description=f'Страница откуда бралась информация: {self.url_parse} \n'
                                    f'{self.descriptions[index]}'
                                    )
                    )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)



