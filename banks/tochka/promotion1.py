import asyncio
import uuid

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
        self.date_starts = []
        self.date_ends = []
        self.links = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        # Инициализация веб-драйвера и открываем страницу
        driver = webdriver.Chrome(service=s)
        driver.get(self.url_parse)
        await asyncio.sleep(3)
        # Получаем HTML-код страницы и закрываем веб-драйвер
        html = driver.page_source
        driver.quit()

        # Находим все блоки с itemprop="name"
        soup = BeautifulSoup(html, 'html.parser')
        sale_events = soup.find_all('div', {'itemscope': '', 'itemtype': 'https://schema.org/SaleEvent'})
        # Извлекаем данные
        for event in sale_events:
            title = event.find('meta', {'itemprop': 'name'})['content'].strip()
            description = event.find('meta', {'itemprop': 'description'})['content'].strip()
            date_start = event.find('meta', {'itemprop': 'startDate'})['content'].strip()
            date_end = event.find('meta', {'itemprop': 'endDate'})['content'].strip()
            link = event.find('meta', {'itemprop': 'url'})['content'].strip()

            self.titles.append(title)
            self.descriptions.append(description)
            self.date_starts.append(date_start)
            self.date_ends.append(date_end)
            self.links.append(link)

    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(bank=Banks.tochka,
                                                                    typechanges=TypeChanges.promotion1)
        change_titles_from_dp = [item.title for item in changes_from_db]
        for index, title in enumerate(self.titles):
            if not title in change_titles_from_dp:
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.tochka,
                        typechanges=TypeChanges.promotion1,
                        #meta_data=self.links[index],
                        link_new_file=await screenshot_page(
                            url=self.links[index], file_name=f'{uuid.uuid4()}.png'),
                        title=title,
                        description=(f'{self.descriptions[index]} Ссылка на новость:  {self.links[index]} \n'
                                     f'Start Date: {self.date_starts[index]} '
                                     f'End Date: {self.date_ends[index]} \n'
                                     f'Страница откуда бралась информация: {self.url_parse}')
                    )
                )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)



