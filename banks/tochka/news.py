import asyncio
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options, service=s)

        driver.get(self.url_parse)
        await asyncio.sleep(3)
        # Находим блоки новостей
        news_blocks = driver.find_elements(By.CLASS_NAME, "news-item_container__D_Xbj")

        # Перебираем блоки новостей и выводим информацию
        for news_block in news_blocks:
            date = news_block.find_element(By.CLASS_NAME, "news-item_date__JXUFm").text
            # Проверка актуальности новости
            if datetime.strptime(date, "%d.%m.%Y") > datetime.now() - timedelta(days=45):
                title = news_block.find_element(By.CLASS_NAME, "fs-xl").text
                link = news_block.find_element(By.CLASS_NAME, "news-item_link__q88Vc").get_attribute("href")
                self.titles.append(title)
                self.descriptions.append(f"Дата новости: {date}")
                self.links.append(link)

        driver.quit()

    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(bank=Banks.tochka, typechanges=TypeChanges.news)
        change_titles_from_dp = [item.title for item in changes_from_db]
        for index, title in enumerate(self.titles):
            if not title in change_titles_from_dp:
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.tochka,
                        typechanges=TypeChanges.news,
                        # meta_data=self.links[index], - специально
                        link_new_file=await screenshot_page(url=self.links[index], file_name=f'{uuid.uuid4()}.png'),
                        title=title,
                        description=f'{self.descriptions[index]} \n'
                                    f'Ссылка на акцию:  {self.links[index]} \n'
                                    f'Страница откуда бралась информация: {self.url_parse}'
                                    )
                    )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)



