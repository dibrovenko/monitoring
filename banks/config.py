import os

current_path = os.getcwd()  # Получаем текущий путь
chrome_driver_path = os.path.join(current_path, 'banks/chromedriver')

tochka = {
    "promotion1": "https://tochka.com/promo/",
    "news": "https://tochka.com/news/",
    "landing_page": "https://tochka.com/tariffs/",
    "pdf_file": "https://tochka.com/tariffs/files"
}

bank_configs = {"tochka": tochka}
