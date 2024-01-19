import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import NoSuchElementException

import time
import pyperclip


def edit_and_save_text(url, filename, username, password):
    # Инициализация браузера
    service = webdriver.chrome.service.Service(
        executable_path="chromedriver.exe")

    # Опции браузера
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    #options.add_argument("--headless=new")
    options.set_capability('pageLoadStrategy', "eager")

    with webdriver.Chrome(service=service, options=options) as driver:
        try:
            start = time.time()
            # Открытие страницы фандома
            driver.get('https://auth.fandom.com/signin?flow=7b6a4faa-9098-4b27-b6b7-01ad0d605e26')

            # Находим поля для ввода логина и пароля
            login_field = driver.find_element(by=By.ID, value="identifier")
            password_field = driver.find_element(by=By.ID, value="password")

            # Вводим логин и пароль
            login_field.send_keys(username)
            print("Введено имя")
            password_field.send_keys(password)
            print("Введён пароль")

            # coockies
            pickle.dump(driver.get_cookies(), open(f"{username}_cookies", "wb"))

            # Находим кнопку "Войти"
            login_button = driver.find_element(by=By.XPATH, value="//button[@class='wds-button Submit_button__2u2G7']")

            # Кликаем по кнопке "Войти"
            login_button.click()
            print('Нажата кнопка "Войти"')

            # Переходим по ссылке
            driver.get(url)
            print('Выполнен переход на страницу')
            time.sleep(5)
            try:
                # Найти элемент по комбинированному селектору
                enter_button = driver.find_element(by=By.XPATH, value="//span[@class='oo-ui-widget oo-ui-widget-enabled oo-ui-buttonElement oo-ui-buttonElement-framed oo-ui-labelElement oo-ui-flaggedElement-primary oo-ui-flaggedElement-progressive oo-ui-buttonWidget oo-ui-actionWidget']")

                # Нажать на кнопку
                enter_button.click()
                print('Кнопка "Сохранить" нажата')
            except Exception as e:
                print(f'Ошибка при нажатии кнопки "Сохранить": {e}')
                print('Кнопка не была найдена')

            # Получаем редактируемый элемент
            editable_element = driver.find_element(by=By.XPATH,
                                                   value="//div[@class='ve-ce-branchNode ve-ce-documentNode ve-ce-attachedRootNode ve-ce-rootNode mw-content-ltr mw-parser-output mw-show-empty-elt ve-ce-documentNode-codeEditor-webkit-hide']")

            # Получаем вложенный параграф
            paragraph_element = editable_element.find_element(by=By.XPATH,
                                                              value=".//p[@class='ve-ce-branchNode ve-ce-contentBranchNode ve-ce-paragraphNode']")

            # Читаем текст из файла
            with open(filename, 'r', encoding='utf-8') as f:
                new_text = f.read()
            print(f"Текст получен")
            time.sleep(1)

            # Очищаем и вводим новый текст
            paragraph_element.send_keys(Keys.CONTROL + "a")
            time.sleep(1)
            paragraph_element.send_keys(Keys.DELETE)

            print("Очищено, приступаем писать текст")
            for line in new_text.splitlines():
                paragraph_element.send_keys(line)
                paragraph_element.send_keys(Keys.ENTER)
                time.sleep(0.1)
            print("Написано")

            # Находим кнопку сохранения по тексту внутри кнопки
            save_button = driver.find_element(by=By.XPATH, value="//button[contains(.,'Сохранить')]")
            # Кликаем по кнопке сохранения
            save_button.click()
            time.sleep(2)
            print("Сохранено")
            end = time.time() - start
            print(f"Время выполнения: {end} сек.")

            driver.close()
            driver.quit()
        except MaxRetryError as ex:
            print(f"MaxRetryError: {ex}")
        except Exception as ex:
            print(ex)


# Пример использования в другой программе:
#url = 'https://ss14andromeda13.fandom.com/ru/wiki/%D0%A0%D0%95%D0%94_(%D0%A2%D0%B5%D1%81%D1%82%D1%8B)?action=edit'
#filename = 'filename.txt'
#username = 'DeRecnadBot'
#password = 'B0g0m0l1337'

#edit_and_save_text(url, filename, username, password)