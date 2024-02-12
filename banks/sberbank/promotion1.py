import asyncio
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

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

        # Ожидание загрузки всех элементов на странице
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "MlchtUI-OfferCard__BlockText")))

        # Находим все блоки с акциями
        action_blocks = driver.find_elements(By.CLASS_NAME, "MlchtUI-OfferCard")

        # Нажимаем на каждую акцию
        for block in action_blocks:
            title = block.find_element(By.CLASS_NAME, 'MlchtUI-OfferCard__Title').text.strip()
            description = block.find_element(By.CLASS_NAME, 'MlchtUI-OfferCard__Description').text.strip()
            deadline = block.find_element(By.CSS_SELECTOR, 'p.sticker').text
            block.click()
            # Ждем загрузки новой страницы
            wait.until(EC.number_of_windows_to_be(2))
            # Переключаемся на новую вкладку
            driver.switch_to.window(driver.window_handles[1])
            # Получаем текущий URL
            current_url = driver.current_url
            self.titles.append(title)
            self.descriptions.append(f"{description}. Дедлайн: {deadline}")
            self.links.append(current_url)
            await asyncio.sleep(1)
            # Закрываем вкладку с акцией
            driver.close()
            # Переключаемся на основную вкладку
            driver.switch_to.window(driver.window_handles[0])
        driver.quit()

    @async_exception_handler
    async def compare(self):
        changes_from_db = await AsyncORM.select_changes_for_compare(bank=Banks.sberbank,
                                                                    typechanges=TypeChanges.promotion1)
        change_titles_from_dp = [item.title for item in changes_from_db]
        for index, title in enumerate(self.titles):
            if not title in change_titles_from_dp:
                self.changes_to_db.append(
                    Changes(
                        bank=Banks.sberbank,
                        typechanges=TypeChanges.promotion1,
                        #meta_data=self.links[index],
                        link_new_file=await screenshot_page(
                            url=self.links[index], file_name=f'{uuid.uuid4()}.png', file_name_bank="sberbank"),
                        title=title,
                        description=(f'{self.descriptions[index]} \nСсылка на акцию:  {self.links[index]} \n'
                                     f'Страница откуда бралась информация: {self.url_parse}')
                    )
                )
        # отправляем все изменения одним запросом в бд
        await AsyncORM.insert_list_changes(list_class_changes=self.changes_to_db)



