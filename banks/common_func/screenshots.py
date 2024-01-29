import os
import asyncio
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from banks.common_func.except_handlers import exception_handler, async_exception_handler


from banks.config import chrome_driver_path


#@async_exception_handler
async def screenshot_page(url: str, file_name: str | None = None) -> str:
    """
    Создает скриншот ВСЕЙ веб-страницы с использованием браузера Google Chrome и сохраняет его в указанном файле.

    :param url: URL-адрес веб-страницы для создания скриншота.
    :param file_name: Необязательное имя файла для сохранения скриншота. Если не указано или расширение не .png,
                      будет сгенерировано уникальное имя в формате UUID.

    :return: Ссылка на сохраненный файл.
    """
    # Получаем текущий путь
    current_path = os.getcwd()
    # Генерация имени файла, если не указано или расширение не .png или файл такой уже сущетсвует
    if file_name is None or not file_name.endswith(".png"):
        file_name = f'{uuid.uuid4()}.png'

    # Формирование пути для сохранения скриншота в подкаталоге "banks/tochka/data" и проверка что такой файл не сущетс
    download_path = os.path.join(current_path, f'banks/tochka/data/{file_name}')
    if os.path.isfile(download_path):
        download_path = os.path.join(current_path, f'banks/tochka/data/{uuid.uuid4()}.png')

    # Указываем путь до исполняемого файла драйвера Google Chrome
    s = Service(executable_path=chrome_driver_path)

    # Создаем экземпляр браузера с настройками и указываем путь до драйвера
    driver = webdriver.Chrome(service=s)

    # Заходим на страницу
    driver.get(url=url)
    await asyncio.sleep(0.3)
    # Сделайте скриншот всей страницы
    driver.save_screenshot(download_path)

    # Закрытие браузера
    driver.quit()

    # Возвращаем ссылку на сохраненный файл
    return download_path