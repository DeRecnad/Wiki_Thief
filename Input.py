import pickle

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib3.exceptions import MaxRetryError

import time

def click_save_button_iframe(driver, save_button_xpath):
    try:
        save_button = driver.find_element(by=By.XPATH, value=save_button_xpath)

        # Прокрутка к элементу
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
        time.sleep(1)  # Даем время на прокрутку

        # Проверим, доступен ли элемент для клика
        if save_button.is_displayed() and save_button.is_enabled():
            try:
                save_button.click()  # Пробуем кликнуть по кнопке
                print("Кнопка успешно нажата методом click().")
            except ElementClickInterceptedException:
                print("Элемент перекрыт другим элементом, используем ActionChains для клика.")
                ActionChains(driver).move_to_element(save_button).click().perform()
                print("Кнопка успешно нажата методом ActionChains.")
            except Exception as e:
                print(f"Произошла ошибка при клике методом click(): {e}")
                print("Пробуем кликнуть через JavaScript.")
                driver.execute_script("arguments[0].click();", save_button)
                print("Кнопка успешно нажата через JavaScript.")
        else:
            print("Элемент недоступен для клика.")
    except NoSuchElementException:
        print(f"Элемент с XPath '{save_button_xpath}' не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def determine_wiki(url):
    if 'aavikko.di9.ru' in url:
        return 'AAVIKKO'
    elif 'ss14andromeda13.fandom.com' in url:
        return 'FANDOM'
    else:
        return 'UNKNOWN'


def login(username, password, driver, url):
    try:
        wiki_type = determine_wiki(url)

        if wiki_type == 'FANDOM':
            login_url = 'https://auth.fandom.com/signin?flow=7b6a4faa-9098-4b27-b6b7-01ad0d605e26'
        elif wiki_type == 'AAVIKKO':
            login_url = 'http://aavikko.di9.ru/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%92%D1%85%D0%BE%D0%B4&returnto=%D0%A0%D0%BE%D0%BB%D0%B8'  # Замените на правильный URL для входа на Aavikko

        driver.get(login_url)

        if wiki_type == 'FANDOM':
            login_field = driver.find_element(by=By.ID, value="identifier")
            password_field = driver.find_element(by=By.ID, value="password")
            login_button_xpath = "//button[@class='wds-button Submit_button__2u2G7']"
        elif wiki_type == 'AAVIKKO':
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


def edit_and_save_text(url, filename, driver):
    wiki_type = determine_wiki(url)

    driver.get(url)
    print('Выполнен переход на страницу')
    time.sleep(5)

    try:
        if wiki_type == 'FANDOM':
            enter_button_xpath = "//span[@class='oo-ui-widget oo-ui-widget-enabled oo-ui-buttonElement oo-ui-buttonElement-framed oo-ui-labelElement oo-ui-flaggedElement-primary oo-ui-flaggedElement-progressive oo-ui-buttonWidget oo-ui-actionWidget']"
            editable_xpath = "//div[@class='ve-ce-branchNode ve-ce-documentNode ve-ce-attachedRootNode ve-ce-rootNode mw-content-ltr mw-parser-output mw-show-empty-elt ve-ce-documentNode-codeEditor-webkit-hide']"
            paragraph_xpath = ".//p[@class='ve-ce-branchNode ve-ce-contentBranchNode ve-ce-paragraphNode']"
            save_button_xpath = "//button[contains(.,'Сохранить')]"
        elif wiki_type == 'AAVIKKO':
            enter_button_xpath = "//a[@title='Редактировать данную страницу [alt-v]']"
            editable_xpath = "//div[@class='wikiEditor-ui']"
            paragraph_xpath = ".//textarea[@aria-label='Редактор исходного вики-текста']"
            save_element_xpath = "//span[@id='wpSaveWidget']"
            save_button_xpath = "//input[@id='wpSave']"

        if wiki_type == 'FANDOM':
            enter_button = driver.find_element(by=By.XPATH, value=enter_button_xpath)
            enter_button.click()
            print('Кнопка "Редактировать" нажата')
        editable_element = driver.find_element(by=By.XPATH, value=editable_xpath)

        if wiki_type == 'FANDOM':
            paragraph_element = editable_element.find_element(by=By.XPATH, value=paragraph_xpath)
        elif wiki_type == 'AAVIKKO':
            paragraph_element =editable_element.find_element(by=By.XPATH, value=paragraph_xpath)

        with open(filename, 'r', encoding='utf-8') as f:
            new_text = f.read()
        print(f"Текст получен в new_text")
        time.sleep(1)

        paragraph_element.send_keys(Keys.CONTROL + "a")
        time.sleep(1)
        paragraph_element.send_keys(Keys.DELETE)

        print("Очищено, приступаем писать текст")
        for line in new_text.splitlines():
            paragraph_element.send_keys(line)
            paragraph_element.send_keys(Keys.ENTER)
            time.sleep(0.1)
        print("Написано")



        if wiki_type == 'FANDOM':
            save_button = driver.find_element(by=By.ID, value=save_button_xpath)
            save_button.click()
        elif wiki_type == 'AAVIKKO':
            click_save_button_iframe(driver, save_button_xpath)

        time.sleep(2)

        print("Сохранено")
    except MaxRetryError as ex:
        print(f"MaxRetryError: {ex}")
    except Exception as ex:
        print(ex)


# Пример использования в другой программе:
# url = 'https://ss14andromeda13.fandom.com/ru/wiki/%D0%A0%D0%95%D0%94_(%D0%A2%D0%B5%D1%81%D1%82%D1%8B)?action=edit'
# filename = 'filename.txt'
# username = 'DeRecnadBot'
# password = 'B0g0m0l1337'
# wiki_type = determine_wiki(url)
# driver = webdriver.Chrome()  # Не забудьте импортировать и инициализировать WebDriver
# login(username, password, driver, wiki_type)
# edit_and_save_text(url, filename, driver, wiki_type)
