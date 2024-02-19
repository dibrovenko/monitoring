import asyncio
import uuid
import requests
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


# Загрузка веб-страницы
url = 'https://alfabank.ru/news/t/release/'


class News:

    def __init__(self, url):
        self.url_parse = url
        self.titles = []
        self.descriptions = []
        self.links = []
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):
        response = requests.get(self.url_parse)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск всех блоков новостей
        news_blocks = soup.find_all('li', class_='d2C8J b2C8J h2C8J')

        # Извлечение данных о новостях
        for block in news_blocks:
            date = block.find('span',
                              class_='typography__secondary_36jpp typography__secondary-medium_kzul5').text.strip()
            title = block.find('h3').text.strip()
                               #class_='aJQuP lJQuP xJQuP FJQuP mG2mw GG2mw __G2mw aiG2mw d2C8J e2C8J').text.strip()
            link = 'https://alfabank.ru' + block.find('a')['href']
            self.titles.append(title)
            self.descriptions.append(f"Дата новости: {date}")
            self.links.append(link)

    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(bank=Banks.alfa, typechanges=TypeChanges.news)
        change_titles_from_dp = [item.title for item in changes_from_db]
        for index, title in enumerate(self.titles):
            if not title in change_titles_from_dp:
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.alfa,
                        typechanges=TypeChanges.news,
                        # meta_data=self.links[index], - специально
                        link_new_file=await screenshot_page(url=self.links[index],
                                                            file_name=f'{uuid.uuid4()}.png', file_name_bank="alfa"),
                        title=title,
                        description=f'{self.descriptions[index]} \n'
                                    f'Ссылка на акцию:  {self.links[index]} \n'
                                    f'Страница откуда бралась информация: {self.url_parse}'
                                    )
                    )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)



