from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from proxy_auth_data import password, username
import os
import time

import urllib.parse


def log_transferred_file(file_name, log_file='transferred_files.txt'):
    """
        Записывает имя файла в лог файл.
        """
    try:
        # Открываем файл в режиме добавления и записываем имя файла
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(file_name + '\n')
    except Exception as e:
        print(f"Ошибка при записи файла {file_name}: {e}")

def process_log_file_files(log_file_path='transferred_files.txt'):
    try:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Удаление дубликатов и сортировка записей
        unique_lines = sorted(set(lines))

        # Перезапись файла с отсортированными уникальными значениями
        with open(log_file_path, 'w', encoding='utf-8') as file:
            file.writelines(unique_lines)

        print(f"Лог-файл '{log_file_path}' обработан: удалены дубликаты и отсортированы записи.")

    except Exception as e:
        print(f"Произошла ошибка при обработке лог-файла: {e}")



def upload_file_to_wiki(driver, upload_url, file_path):
    try:
        driver.get(upload_url)
        wait = WebDriverWait(driver, 1)

        # Найти элемент input для загрузки файла
        file_input = wait.until(EC.presence_of_element_located((By.ID, "wpUploadFile")))
        file_input.send_keys(file_path)

        # Найти кнопку отправки и использовать JavaScript для клика
        submit_button = wait.until(EC.presence_of_element_located((By.NAME, "wpUpload")))
        driver.execute_script("arguments[0].click();", submit_button)

        print(f"Файл '{file_path}' успешно загружен.")

        file_name = os.path.basename(file_path)
        decoded_item = urllib.parse.unquote(file_name)
        log_transferred_file(decoded_item)

    except Exception as e:
        print(f"Произошла ошибка при загрузке файла '{file_path}': {e}")


def upload_files_in_folder(folder_path, base_upload_url, submit_button_name, driver):
    try:
        # Проходимся по всем файлам в указанной папке
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                try:
                    # Формируем URL для загрузки файла
                    encoded_file_name = file_name.replace(' ', '%20')  # URL-кодируем имя файла
                    upload_url = f"{base_upload_url}&wpDestFile={encoded_file_name}"

                    # Загружаем файл на вики
                    upload_file_to_wiki(driver, upload_url, file_path)

                    # Удаляем файл после успешной загрузки
                    os.remove(file_path)
                    print(f"Файл '{file_path}' удален.")
                except Exception as e:
                    print(f"Ошибка при загрузке или удалении файла '{file_path}': {e}")

                time.sleep(1)  # Добавляем задержку между загрузками
    except Exception as e:
        print(f"Ошибка при обработке файлов в папке '{folder_path}': {e}")
