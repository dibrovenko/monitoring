import pandas as pd
from pathlib import Path

import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC

from banks.config import chrome_driver_path


def excel_diff(path_OLD: Path, path_NEW: Path, path_to_save: str):
    Bool_Change = True

    # Сравнение двух файлов
    df1 = pd.read_excel(path_NEW)
    df2 = pd.read_excel(path_OLD)
    if not df1.equals(df2):
        Bool_Change = False

    index_col = df1.columns[0]
    df_OLD = pd.read_excel(path_OLD, index_col=index_col).fillna(0)
    df_NEW = pd.read_excel(path_NEW, index_col=index_col).fillna(0)

    # Perform Diff
    dfDiff = df_NEW.copy()
    droppedRows = []
    newRows = []

    cols_OLD = df_OLD.columns
    cols_NEW = df_NEW.columns
    sharedCols = list(set(cols_OLD).intersection(cols_NEW))

    for row in dfDiff.index:
        if (row in df_OLD.index) and (row in df_NEW.index):
            for col in sharedCols:
                value_OLD = df_OLD.loc[row, col]
                value_NEW = df_NEW.loc[row, col]
                if value_OLD == value_NEW:
                    dfDiff.loc[row, col] = df_NEW.loc[row, col]
                else:
                    dfDiff.loc[row, col] = ('{}→{}').format(value_OLD, value_NEW)
                    Bool_Change = False
        else:
            newRows.append(row)
            Bool_Change = False

    for row in df_OLD.index:
        if row not in df_NEW.index:
            droppedRows.append(row)
            dfDiff = dfDiff._append(df_OLD.loc[row, :])
            Bool_Change = False

    dfDiff = dfDiff.sort_index().fillna('')
    DESCRIPTION = (f'\nNew Rows: {newRows} \n'
                   f'Dropped Rows: {droppedRows}')
    # Save output and format
    fname = f'{path_to_save}/{path_OLD.stem} vs {path_NEW.stem}.xlsx'
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')

    dfDiff.to_excel(writer, sheet_name='DIFF', index=True)
    df_NEW.to_excel(writer, sheet_name=path_NEW.stem, index=True)
    df_OLD.to_excel(writer, sheet_name=path_OLD.stem, index=True)

    # get xlsxwriter objects
    workbook = writer.book
    worksheet = writer.sheets['DIFF']
    worksheet.hide_gridlines(2)
    worksheet.set_default_row(15)

    # define formats
    date_fmt = workbook.add_format({'align': 'center', 'num_format': 'yyyy-mm-dd'})
    center_fmt = workbook.add_format({'align': 'center'})
    number_fmt = workbook.add_format({'align': 'center', 'num_format': '#,##0.00'})
    cur_fmt = workbook.add_format({'align': 'center', 'num_format': '$#,##0.00'})
    perc_fmt = workbook.add_format({'align': 'center', 'num_format': '0%'})
    grey_fmt = workbook.add_format({'font_color': '#E0E0E0'})
    highlight_fmt = workbook.add_format({'font_color': '#FF0000', 'bg_color': '#B1B3B3'})
    new_fmt = workbook.add_format({'font_color': '#32CD32', 'bold': True})

    # set format over range
    # highlight changed cells
    worksheet.conditional_format('A1:ZZ1000', {'type': 'text',
                                               'criteria': 'containing',
                                               'value': '→',
                                               'format': highlight_fmt})

    # highlight new/changed rows
    for row in range(dfDiff.shape[0]):
        if row + 1 in newRows:
            worksheet.set_row(row + 1, 15, new_fmt)
        if row + 1 in droppedRows:
            worksheet.set_row(row + 1, 15, grey_fmt)

    # save
    writer._save()
    return {"Bool_Change": Bool_Change, "description": DESCRIPTION, "compare_path": fname}


async def excel_diff_aspose(file_path1: str, file_path2: str) -> str:
    s = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=s)
    await asyncio.sleep(3)
    # URL страницы, на которой находится элемент для загрузки файла
    url = 'https://products.aspose.app/cells/ru/comparison'
    driver.get(url)

    # Найдем элемент для загрузки файла по его ID
    upload_input = driver.find_element(By.ID, 'UploadFileInput-779922903')
    await asyncio.sleep(15)
    # Отправляем путь к файлу на элемент для загрузки файла
    upload_input.send_keys(file_path1)
    await asyncio.sleep(4)

    upload_input = driver.find_element(By.ID, 'UploadFileInput-779922904')
    await asyncio.sleep(2)
    # Отправляем путь к файлу на элемент для загрузки файла
    upload_input.send_keys(file_path2)
    await asyncio.sleep(15)

    # Ждем, пока кнопка "СРАВНИВАТЬ" станет видимой
    compare_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "uploadButton"))
    )
    compare_button.click()
    await asyncio.sleep(30)
    url_link = driver.current_url
    return url_link
