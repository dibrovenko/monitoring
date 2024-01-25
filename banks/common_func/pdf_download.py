import asyncio
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

from banks.config import chrome_driver_path


async def selenium_pdf_down(url: str, download_path: str) -> str:
    await asyncio.sleep(1)
    # Создаем объект опций Chrome
    chrome_options = Options()
    # Указываем путь до исполняемого файла драйвера Google Chrome
    s = Service(executable_path=chrome_driver_path)
    chrome_options.add_experimental_option(
        'prefs', {
            'download.default_directory': download_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        })

    # Создаем экземпляр браузера с настройками и указываем путь до драйвера
    driver = webdriver.Chrome(service=s, options=chrome_options)
    # Заходим на страницу
    driver.get(url)
    # Ждем некоторое время для загрузки страницы
    await asyncio.sleep(3)

    # Выполняем JS код
    js_code = """
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.responseType = 'blob'; // Устанавливаем тип ответа на blob

    xhr.addEventListener("readystatechange", function() {
      if (this.readyState === 4 && this.status === 200) {
        // Создаем ссылку на объект Blob
        var blob = new Blob([this.response], { type: 'application/pdf' });

        // Создаем ссылку на скачивание файла
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = "FILENAME.pdf";
        link.click();
      }
    });

    xhr.open("GET", "url_link_js");
    xhr.setRequestHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7");
    // Другие заголовки...

    xhr.send();
    """

    js_code = js_code.replace("url_link_js", url)
    FILENAME = f"{uuid.uuid4()}.pdf"
    js_code = js_code.replace("FILENAME.pdf", FILENAME)
    driver.execute_script(js_code)
    await asyncio.sleep(5)

    # Закрываем браузер
    driver.quit()
    return f"{download_path}/{FILENAME}"
