from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from proxy_auth_data import password, username

import os

import time

def login(username, password, driver):
    try:
        login_url = 'http://aavikko.di9.ru/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%92%D1%85%D0%BE%D0%B4&returnto=%D0%A0%D0%BE%D0%BB%D0%B8'  # Замените на правильный URL для входа на Aavikko

        driver.get(login_url)

        login_field = driver.find_element(by=By.ID, value="wpName1")  # Замените на правильный селектор для Aavikko
        password_field = driver.find_element(by=By.ID, value="wpPassword1")  # Замените на правильный селектор для Aavikko
        login_button_xpath = "//button[@class='mw-htmlform-submit mw-ui-button mw-ui-primary mw-ui-progressive']"  # Замените на правильный селектор для Aavikko

        login_field.send_keys(username)
        print("Введено имя")
        password_field.send_keys(password)
        print("Введён пароль")

        login_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, login_button_xpath))
        )
        login_button.click()
        print('Нажата кнопка "Войти"')
        time.sleep(2)

        return driver
    except Exception as e:
        print(f"Ошибка при логине: {e}")


def upload_file_to_wiki(driver, upload_url, file_path):
    try:
        driver.get(upload_url)
        wait = WebDriverWait(driver, 10)

        # Найти элемент input для загрузки файла
        file_input = wait.until(EC.presence_of_element_located((By.ID, "wpUploadFile")))
        file_input.send_keys(file_path)

        # Найти кнопку отправки и использовать JavaScript для клика
        submit_button = wait.until(EC.presence_of_element_located((By.NAME, "wpUpload")))
        driver.execute_script("arguments[0].click();", submit_button)

        print(f"Файл '{file_path}' успешно загружен.")
    except Exception as e:
        print(f"Произошла ошибка при загрузке файла '{file_path}': {e}")


def process_files_in_folder(folder_path, base_upload_url, submit_button_name, driver):
    # Опции браузера
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.set_capability('pageLoadStrategy', "eager")
    service = Service(executable_path="chromedriver.exe")

    # Создаем экземпляр веб-драйвера
    driver = webdriver.Chrome(service=service, options=options)

    login(username, password, driver)

    try:
        # Проходимся по всем файлам в указанной папке
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                # Формируем URL для загрузки файла
                encoded_file_name = file_name.replace(' ', '%20')  # URL-кодируем имя файла
                upload_url = f"{base_upload_url}&wpDestFile={encoded_file_name}"

                # Загружаем файл на вики
                upload_file_to_wiki(driver, upload_url, file_path)

                # Удаляем файл после успешной загрузки
                os.remove(file_path)
                print(f"Файл '{file_path}' удален.")

    finally:
        # Закрываем браузер
        driver.quit()

# Пример использования
# if __name__ == "__main__":
    # folder_path = r"D:\Programming\Wiki_Thief\downloaded_images_ss220"  # Путь к папке с изображениями
    # base_upload_url = "http://aavikko.di9.ru/index.php?title=Служебная:Загрузка"  # Базовый URL для загрузки
    # submit_button_name = "wpUpload"

    # process_files_in_folder(folder_path, base_upload_url, submit_button_name)
