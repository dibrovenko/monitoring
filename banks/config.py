import os

current_path = os.getcwd()  # Получаем текущий путь
#chrome_driver_path = os.path.join(current_path, 'banks/chromedriver')
chrome_driver_path = "/usr/bin/chromedriver"

tochka = {
    "promotion1": "https://tochka.com/promo/",
    "news": "https://tochka.com/news/",
    "landing_page": "https://tochka.com/tariffs/",
    "pdf_file": "https://tochka.com/tariffs/files"
}

alfa = {
    "news": "https://alfabank.ru/news/t/release/",
    "landing_page": "https://alfabank.ru/sme/tariffs/compare/?tid=6&tid=2&tid=1&tid=5&tid=4&tid=3",
    "pdf_file": "https://alfabank.ru/sme/rko/tariffs/pdftariffs/#current_tariffs",
    "promotion1": "https://alfabank.ru/sme/quick/docstariffs/?tab=action&accordion-tab=openacc0"
}

sberbank = {
    "news": "https://www.sberbank.ru/ru/s_m_business/news",
    "landing_page": "https://www.sberbank.com/ru/s_m_business/open-accounts?utm_source=yandex&utm_medium=cpc&utm_campaign=open-accounts_corporate_perform_god_20220100016_context_search_brand_rus_yxprrko%7C90332712&utm_content=cid%7C90332712%7Cgid%7C5236795608%7Cad%7C14562051359_14562051359%7Cph_id%7C45924794158%7Csrc%7Cnone_search%7Cgeo%7C%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0_213%7C&utm_term=%D1%81%D0%B1%D0%B5%D1%80%D0%B1%D0%B0%D0%BD%D0%BA+%D1%80%D0%BA%D0%BE&yclid=15323761025803354111",
    "pdf_file": ["https://www.sberbank.ru/common/img/uploaded/mmb/tariffs/package.pdf",
                 "https://www.sberbank.ru/ru/s_m_business/bankingservice/rko/tariffs"],
    "promotion1": "https://www.sberbank.com/ru/s_m_business/actions"
}

vtb = {
    "news": "https://www.vtb.ru/tarify/korporativnym-klientam/",
    "landing_page": "https://www.vtb.ru/malyj-biznes/otkryt-schet/sravnenie-pakety-uslug/",
    "pdf_file_from_landing_page": "https://www.vtb.ru/malyj-biznes/otkryt-schet/sravnenie-pakety-uslug/",
    "pdf_file": "https://www.vtb.ru/tarify/korporativnym-klientam/"
}

raif = {
    "pdf_file": ["https://www.raiffeisen.ru/static/common/business/tariff_book_short.pdf",
                 "https://www.raiffeisen.ru/static/common/business/tariff_book.pdf"]
}

modul = {
    "pdf_file":
        ["https://modulbank.ru/fs/files/Prilozhenie_2_k_oficialnomu_polnomu_sborniku_tarifov_sistemy_Modulbank.pdf",
         "https://modulbank.ru/fs/files/oficialnyj_polnyj_sbornik_tarifov_sistemy_modulbank.pdf"]
}

mts = {
    "pdf_file": "https://www.mtsbank.ru/upload/static/documents/malomu-biznesu/raschetny-schet/Doc-Usloviya-KBO-web.pdf"
}

ozon = {
    "pdf_file": "https://cdn2.ozone.ru/s3/ob-landing/static/docs/ecom/products/rules/Тарифы%20Ozon%20Счёт%20для%20бизнеса%2020231213.pdf"
}

open = {
    "pdf_file": "https://cdn.open.ru/storage/files/tariffs_msb.pdf"
}


bank_configs = {
    "tochka": tochka,
    "alfa": alfa,
    "sberbank": sberbank,
    "vtb": vtb,
    "raif": raif,
    "modul": modul,
    "mts": mts,
    "ozon": ozon,
    "open": open
}


