import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib3.exceptions import MaxRetryError
import time
import pyperclip


service = webdriver.chrome.service.Service(executable_path="chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.set_capability('pageLoadStrategy', "eager")

def login(driver, username, password):

    driver.get('https://auth.fandom.com/signin?flow=7b6a4faa-9098-4b27-b6b7-01ad0d605e26')

    login_field = driver.find_element(by=By.ID, value="identifier")
    password_field = driver.find_element(by=By.ID, value="password")

    login_field.send_keys(username)
    print("Введено имя")
    password_field.send_keys(password)
    print("Введён пароль")

    pickle.dump(driver.get_cookies(), open(f"{username}_cookies", "wb"))
    time.sleep(1)
    login_button = driver.find_element(by=By.XPATH, value="//button[@value='password']")
    login_button.click()
    print('Нажата кнопка "Войти"')

def edit_and_save_text(url, filename, username, password):

    with webdriver.Chrome(service=service, options=options) as driver:
        try:
            start = time.time()
            login(driver, username, password)

            driver.get(url)
            print('Выполнен переход на страницу')
            time.sleep(5)

            editable_element = driver.find_element(by=By.XPATH, value="//div[@class='ve-ce-branchNode ve-ce-documentNode ve-ce-attachedRootNode ve-ce-rootNode mw-content-ltr mw-parser-output mw-show-empty-elt ve-ce-documentNode-codeEditor-webkit-hide']")
            paragraph_element = editable_element.find_element(by=By.XPATH, value=".//p[@class='ve-ce-branchNode ve-ce-contentBranchNode ve-ce-paragraphNode']")

            with open(filename, 'r', encoding='utf-8') as f:
                new_text = f.read()
            pyperclip.copy(new_text)
            print(f"Текст получен")
            time.sleep(1)

            paragraph_element.send_keys(Keys.CONTROL + "a")
            time.sleep(1)
            paragraph_element.send_keys(Keys.DELETE)

            print("Очищено, приступаем писать текст")
            for line in new_text.splitlines():
                paragraph_element.send_keys(line)
                paragraph_element.send_keys(Keys.ENTER)
            print("Написано")

            save_button = driver.find_element(by=By.XPATH, value="//button[contains(.,'Сохранить')]")
            save_button.click()
            time.sleep(2)
            print("Сохранено")
            end = time.time() - start
            print(f"Время выполнения: {end} сек.")

        except MaxRetryError as ex:
            print(f"MaxRetryError: {ex}")
        except Exception as ex:
            print(ex)