import os
import asyncio
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from banks.common_func.except_handlers import exception_handler, async_exception_handler


from banks.config import chrome_driver_path


#@async_exception_handler
async def screenshot_page(url: str, file_name: str | None = None, file_name_bank: str | None = None) -> str:
    """
    Создает скриншот ВСЕЙ веб-страницы с использованием браузера Google Chrome и сохраняет его в указанном файле.

    :param url: URL-адрес веб-страницы для создания скриншота.
    :param file_name: Необязательное имя файла для сохранения скриншота. Если не указано или расширение не .png,
                      будет сгенерировано уникальное имя в формате UUID.
    :param file_name_bank: Костыль

    :return: Ссылка на сохраненный файл.
    """
    #Костыль
    if file_name_bank is None:
        file_name_bank = "tochka"

    # Получаем текущий путь
    current_path = os.getcwd()
    # Генерация имени файла, если не указано или расширение не .png или файл такой уже сущетсвует
    if file_name is None or not file_name.endswith(".png"):
        file_name = f'{uuid.uuid4()}.png'

    # Формирование пути для сохранения скриншота в подкаталоге "banks/tochka/data" и проверка что такой файл не сущетс
    download_path = os.path.join(current_path, f'banks/{file_name_bank}/data/{file_name}')
    if os.path.isfile(download_path):
        download_path = os.path.join(current_path, f'banks/{file_name_bank}/data/{uuid.uuid4()}.png')

    # Указываем путь до исполняемого файла драйвера Google Chrome
    s = Service(executable_path=chrome_driver_path)
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    # Создаем экземпляр браузера с настройками и указываем путь до драйвера
    driver = webdriver.Chrome(service=s, options=chrome_options)

    # Заходим на страницу
    driver.get(url=url)
    await asyncio.sleep(0.5)

    # Дожидаемся полной загрузки страницы
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    # Сделайте скриншот всей страницы
    driver.save_screenshot(download_path)

    # Закрытие браузера
    driver.quit()

    # Возвращаем ссылку на сохраненный файл
    return download_path