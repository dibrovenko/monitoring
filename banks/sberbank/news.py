import asyncio
import os
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

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
        self.changes_to_db = []

    @async_exception_handler
    async def parse(self):

        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        # Инициализация драйвера
        driver = webdriver.Chrome(service=s, options=chrome_options)
        driver.get(self.url_parse)
        await asyncio.sleep(2)
        # Находим блок с новостями
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "na-articles")))
        news_block = driver.find_elements(By.CLASS_NAME, "na-articles")[0]

        # Извлекаем дату и заголовок каждой новости из блока
        articles = news_block.find_elements(By.CLASS_NAME, "na-article")

        for article in articles:
            date = article.find_element(By.CLASS_NAME, "na-article__date").text.strip()
            title = article.find_element(By.CLASS_NAME, "na-article__title").text.strip()
            self.titles.append(title)
            self.descriptions.append(f"дата добавления новости: {date}")

        # Закрываем веб-драйвер после использования
        driver.quit()


    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(bank=Banks.sberbank, typechanges=TypeChanges.news)
        change_titles_from_dp = [item.title for item in changes_from_db]
        for index, title in enumerate(self.titles):
            if not title in change_titles_from_dp:
                download_path, current_url = await self.click_screenshot(index=index)
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.sberbank,
                        typechanges=TypeChanges.news,
                        link_new_file=download_path,
                        title=title,
                        description=f'{self.descriptions[index]} \n'
                                    f'Ссылка на акцию:  {current_url} \n'
                                    f'Страница откуда бралась информация: {self.url_parse}'
                                    )
                    )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)


    async def click_screenshot(self, index: int) -> tuple:
        # Указываем путь до исполняемого файла драйвера Google Chrome
        s = Service(executable_path=chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        # Инициализация драйвера
        driver = webdriver.Chrome(service=s, options=chrome_options)
        driver.get(self.url_parse)
        # Находим блок с новостями
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "na-articles")))
        # Нахождение кнопки по обновленному XPath и нажатие на нее
        try:
            button = driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div/div[3]/div/div/div/div[3]/section/div/div/div/div[2]/button")
            await asyncio.sleep(2.5)
            button.click()
            await asyncio.sleep(0.1)
        except:
            pass

        news_block = driver.find_elements(By.CLASS_NAME, "na-articles")[0]
        # Извлекаем дату и заголовок каждой новости из блока
        articles = news_block.find_elements(By.CLASS_NAME, "na-article")
        title = articles[index].find_element(By.CLASS_NAME, "na-article__title")
        title.click()
        current_url = driver.current_url
        await asyncio.sleep(1.5)
        # Сделайте скриншот всей страницы
        download_path = f"{os.getcwd()}/banks/sberbank/data/{uuid.uuid4()}.png"
        driver.save_screenshot(download_path)

        # Закрываем веб-драйвер после использования
        driver.quit()
        await asyncio.sleep(0.3)
        return download_path, current_url




