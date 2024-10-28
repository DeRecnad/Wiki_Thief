import traceback
import urllib.parse
import os
import pickle
import time
import json
import requests
import re

import tkinter as tk
from tkinter import ttk

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Подключаем менеджер драйвера Хрома
from webdriver_manager.chrome import ChromeDriverManager

from urllib3.exceptions import MaxRetryError
from urllib.parse import urljoin
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from proxy_auth_data import username, password


with open('wiki_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Загрузка JSON файла в память
def load_wiki_data(filename="wiki_data.json"):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Данные из JSON-файла должны быть словарём, а не строкой или другим типом.")



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}
proxies = {}


# Определение вики
WIKI_BASE_URLS = {}
for wiki in data['wiki_output']:
    # Используем 'wiki_type' как ключ, а 'wiki_url' как значение
    WIKI_BASE_URLS[wiki['wiki_type']] = wiki['wiki_base_url']

target_tag = 'textarea'
target_class = 'mw-editfont-monospace'


# Загружаем опции браузера
def get_browser_options():
    """
        Настраивает и возвращает параметры для браузера Chrome.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.set_capability('pageLoadStrategy', "eager")
    return options


# Загружаем черный список
def load_blacklist(file_path):
    """
    Загружает черный список элементов из указанного файла.
    """
    # file_path - путь к черному списку
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            blacklist = file.read().splitlines()
        print(f"Черный список {file_path} загружен. Найдено {len(blacklist)} элементов.")
        return blacklist
    else:
        print(f"Файл черного списка {file_path} не найден.")
        return []


# Проверяем наличие элемента в черном списке
def is_item_in_blacklist(item, blacklist):
    """
    Проверяет, находится ли элемент в черном списке.
    """
    print(f"Проверка на ЧС: {item}")
    decoded_item = urllib.parse.unquote(item)  # Декодируем имя файла
    print(f"  Декодировка: {decoded_item}")
    is_blacklisted = item in blacklist or decoded_item in blacklist
    print(f"  Результат проверки: {'в черном списке' if is_blacklisted else 'не в черном списке'}")
    return is_blacklisted


# Обрабатываем файлы с заданной ссылкой
def process_files_for_upload(link, folder_path, upload_url, submit_button_name, driver, blacklist_files):
    """
    Находит изображения, проверяет их на черный список, скачивает и отправляет на сервер.
    """
    output_filename = 'filename.txt'
    get_specific_text(link, output_filename)

    try:
        with open(output_filename, 'r', encoding='utf-8') as f:
            page_text = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл {output_filename} не найден.")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла {output_filename}: {e}")
        return

    if not page_text:
        print("Ошибка: полученный текст пуст.")
        return

    # Получаем файлы, не находящиеся в черном списке
    valid_files = get_image_files(page_text, blacklist_files)

    # Определяем параметры для скачивания
    wiki_params = determine_wiki_type_output(link, data, fields=['wiki_type'])
    wiki_type = wiki_params[0]

    # Скачиваем только файлы, прошедшие проверку
    download_images(valid_files, folder_path, wiki_type)

    # Загрузка изображений на сервер
    upload_files_in_folder(folder_path, upload_url, submit_button_name, driver)


# Обрабатываем пару ссылок
def process_link_pair(link1, link2, driver, blacklist_links):
    """
    Проверяет ссылки и запускает процесс их обработки, если они не в черном списке.
    """
    # Проверяем, находится ли link1 в черном списке
    if is_item_in_blacklist(link1, blacklist_links):
        return 0

    # Проверяем, находится ли link2 в черном списке
    if is_item_in_blacklist(link2, blacklist_links):
        return 0

    filename = 'filename.txt'

    print(f"Получаем текст с {link1}")

    if get_specific_text(link1) == 'ERR520':
        print(f"Не удалось получить текст с {link1}")
        return 0
    else:
        print("Текст получен")

    print(f"Начинаем вводить текст на {link2}")
    edit_and_save_wiki_text(link2, filename, driver)
    print("Ввод окончен")
    return 1



def check_and_process_links(link1, link2, settings):
    """
    Проверяет количество шаблонов, и запускает процесс их обработки.
    """
    check = 1
    options = get_browser_options()
    service = Service(executable_path="chromedriver.exe")

    count_templates_links = write_template_data_to_file(link1)

    # Определение типа вики и параметров
    wiki_params = determine_wiki_type_input(link2, data, fields=[
        'wiki_type', 'base_upload_url', 'submit_button_name'
    ])

    wiki_type = wiki_params[0]
    base_upload_url = wiki_params[1]
    submit_button_name = wiki_params[2]

    if wiki_type is None:
        raise ValueError(f"Unknown wiki type for URL: {link1}")

    folder_path = os.path.join(os.getcwd(), "downloaded_images")
    #base_upload_url = "http://aavikko.di9.ru/index.php?title=Служебная:Загрузка"
    #submit_button_name = "wpUpload"

    blacklist_links = load_blacklist('blacklist_links.txt')
    blacklist_files = load_blacklist('blacklist_files.txt')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    login_to_wiki(username, password, driver, link2)  # Вход выполняется один раз

    try:
        if settings.use_templates:
            handle_templates(link1, link2, driver, count_templates_links, folder_path, base_upload_url, submit_button_name, blacklist_links, blacklist_files)
        else:
            print('Перенос без шаблонов')
            process_link_pair(link1, link2, driver, blacklist_links)
            process_files_for_upload(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)
    finally:
        process_log_file_files()
        process_link_log_file()
        print('Программа успешно завершила свою работу')
        driver.quit()

def handle_templates(link1, link2, driver, count_templates_links, folder_path, base_upload_url, submit_button_name, blacklist_links, blacklist_files):
    """
    Обрабатывает процесс обработки ссылок с шаблонами.
    """
    if count_templates_links == 'ERR520':
        print(f'Ошибка 520 (в handle_templates: {traceback.extract_stack()[-2].lineno})')
    elif count_templates_links > 0:
        print(f'Были обнаружены шаблоны, проверка на шаблоны вернула: {count_templates_links}')
        main1_link, main2_link = link1, link2

        while count_templates_links != 0:
            phrase = get_and_remove_last_link()
            link1 = create_template_url(phrase, main1_link)
            link2 = create_template_url(phrase, main2_link)

            count_templates_links -= 1
            check = process_link_pair(link1, link2, driver, blacklist_links)
            if check != 0:
                process_files_for_upload(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)

        # Обработка основной пары ссылок после цикла
        process_link_pair(main1_link, main2_link, driver, blacklist_links)
        process_files_for_upload(main1_link, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)
    else:
        print(f'Шаблоны не обнаружены, проверка на шаблоны вернула: {count_templates_links}')
        process_link_pair(link1, link2, driver, blacklist_links)
        process_files_for_upload(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)


# Получаем последнюю ссылку из файла и удаляем её
def get_and_remove_last_link(file_path='templates_used.txt'):
    """
    Получает последнюю строку из файла и удаляет её.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if lines:
            last_link = lines[-1].strip()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines[:-1])

            return last_link
        else:
            print(f'Файл {file_path} пуст. Нет ссылок для извлечения.')
            return None
    except Exception as e:
        print(f'Произошла ошибка при обработке файла: {e}')
        return None


# Функция для создания URL на основе шаблона и базового URL
def create_template_url(template_phrase, base_url):
    parsed_url = urlparse(base_url)

    # Проверяем наличие '/edit/' в пути
    if '/edit/' in parsed_url.path:
        # Оставляем только '/edit/' и добавляем template_phrase
        edit_index = parsed_url.path.find('/edit/')
        new_path = parsed_url.path[:edit_index + len('/edit/')] + template_phrase
        new_url = urlunparse(parsed_url._replace(path=new_path))

    else:
        # Если URL имеет структуру с ?title=, добавляем template_phrase в параметры запроса
        query_params = parse_qs(parsed_url.query)
        query_params['title'] = [template_phrase]
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query))

    decoded_url = urllib.parse.unquote(new_url)
    print(f'Создана новая ссылка {decoded_url}')

    return decoded_url


# Логируем ссылку в файл
def log_link_to_file(link, log_file='used_links.txt'):
    """
    Записывает ссылку в лог файл.
    """
    # Расшифровываем ссылку для удобства чтения
    decoded_link = urllib.parse.unquote(link)

    # Открываем файл в режиме добавления и записываем ссылку
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(decoded_link + '\n')


# Обрабатываем файл логов ссылок
def process_link_log_file(log_file='used_links.txt'):
    """
    Очищает лог-файл от дубликатов и сортирует ссылки.
    """
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            links = f.readlines()

        # Удаляем пробелы и дубликаты
        unique_links = sorted(set(link.strip() for link in links))

        # Сохраняем уникальные и отсортированные ссылки обратно в файл
        with open(log_file, 'w', encoding='utf-8') as f:
            for link in unique_links:
                f.write(link + '\n')

    except FileNotFoundError:
        print(f"Файл {log_file} не найден. Возможно, он еще не был создан.")


# Нажимаем кнопку сохранения в iframe
def click_save_button_in_iframe(driver, save_button_xpath):
    """
    Нажимает кнопку сохранения в iframe, используя различные методы.
    """
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


# Функция для определения типа вики и загрузки параметров из JSON
def determine_wiki_type_input(url, data="wiki_data.json", fields=None):
    """
    Определяет параметры типа вики на основе URL и данных из JSON.
    """
    # Пробуем распарсить строку как JSON, если это строка
    if isinstance(data, str):
        try:
            data = json.loads(data)  # Пробуем распарсить строку как JSON
        except json.JSONDecodeError:
            print("Ошибка при декодировании JSON")
            return None

    # Проверяем, что данные являются словарем и содержат ключ 'wiki_input'
    if isinstance(data, dict) and 'wiki_input' in data:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        for wiki in data['wiki_input']:
            if hostname and wiki['wiki_url'] in hostname:
                # Если указаны поля, возвращаем только их значения
                if fields:
                    return tuple(wiki.get(field) for field in fields)
                else:
                    # Если поля не указаны, возвращаем все ключевые параметры
                    return (
                        wiki.get('wiki_type'),
                        wiki.get('wiki_url'),
                        wiki.get('login_url'),
                        wiki.get('base_upload_url'),
                        wiki.get('submit_button_name'),
                        wiki.get('login_button_xpath'),
                        wiki.get('login_field'),
                        wiki.get('password_field'),
                        wiki.get('enter_button_xpath'),
                        wiki.get('editable_xpath'),
                        wiki.get('paragraph_xpath'),
                        wiki.get('save_element_xpath'),
                        wiki.get('save_button_xpath')
                    )
    else:
        print("Неверный формат данных")
        return tuple(None for _ in (fields or [
            'wiki_type', 'wiki_url', 'login_url',
            'base_upload_url', 'submit_button_name',
            'login_button_xpath', 'login_field', 'password_field',
            'enter_button_xpath', 'editable_xpath', 'paragraph_xpath',
            'save_element_xpath', 'save_button_xpath'
        ]))


def determine_wiki_type_output(url, data="wiki_data.json", fields=None):
    """
    Определяет тип вики на основе URL и данных из JSON.
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    # Если data - это строка и не JSON, пробуем загрузить файл
    if isinstance(data, str):
        try:
            with open(data, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"Файл {data} не найден.")
            return None
        except json.JSONDecodeError:
            try:
                data = json.loads(data)  # Пробуем распарсить строку как JSON
            except json.JSONDecodeError:
                print("Ошибка при декодировании JSON")
                return None

    if isinstance(data, dict) and 'wiki_output' in data:
        for wiki in data['wiki_output']:
            if hostname and wiki['wiki_url'] in hostname:
                # Если указаны поля, возвращаем только их значения
                if fields:
                    return tuple(wiki.get(field) for field in fields)
                else:
                    # Если поля не указаны, возвращаем все ключевые параметры
                    return (
                        wiki.get('wiki_url'),
                        wiki.get('wiki_type'),
                        wiki.get('div_class'),
                        wiki.get('template_keyword'),
                        wiki.get('target_tag'),
                        wiki.get('target_class'),
                        wiki.get('wiki_link')
                    )
    else:
        print("Неверный формат данных")

    # Возвращаем None для всех запрашиваемых полей, если wiki не найдена
    return tuple(None for _ in (fields or [
        'wiki_url', 'wiki_type', 'div_class', 'template_keyword', 'target_tag', 'target_class',
        'wiki_link'
    ]))


# Входим в аккаунт на wiki
def login_to_wiki(username, password, driver, wiki_url):
    """
    Выполняет вход на указанной вики-странице.
    """
    try:
        # Определение типа вики и параметров
        wiki_params = determine_wiki_type_input(wiki_url, data, fields=[
            'wiki_type', 'login_url', 'login_field', 'password_field',
            'login_button_xpath'
        ])

        wiki_type = wiki_params[0]
        login_url = wiki_params[1]
        login_field_selector = wiki_params[2]
        password_field_selector = wiki_params[3]
        login_button_xpath = wiki_params[4]

        if wiki_type is None:
            raise ValueError(f"Unknown wiki type for URL: {wiki_url}")

        # Переход на страницу входа
        driver.get(login_url)

        # Динамическое получение полей и кнопки
        login_field = driver.find_element(by=By.ID, value=login_field_selector)
        password_field = driver.find_element(by=By.ID, value=password_field_selector)
        login_button = driver.find_element(by=By.XPATH, value=login_button_xpath)  # Замените на правильный селектор для Aavikko

        login_field.send_keys(username)
        print("Введено имя")
        password_field.send_keys(password)
        print("Введён пароль")

        login_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, login_button_xpath))
        )
        login_button.click()
        print('Нажата кнопка "Войти"')
        time.sleep(0.5)

        return driver
    except Exception as e:
        print(f"Ошибка при логине: {e}")


# Редактируем и сохраняем текст на странице wiki
#def click_save_button_in_iframe(driver, save_button_xpath):
    # Это функция-обертка для нажатия на кнопку сохранения в iframe, если требуется.
    #save_button = driver.find_element(by=By.XPATH, value=save_button_xpath)
    #save_button.click()

def edit_and_save_wiki_text(url, filename, driver):
    """
    Редактирует и сохраняет текст на странице вики, используя Selenium.
    """
    # Определение типа вики и получение параметров
    wiki_params = determine_wiki_type_input(url, data, fields=[
        'wiki_type', 'editable_xpath', 'paragraph_xpath', 'save_button_xpath'
    ])

    wiki_type = wiki_params[0]
    editable_xpath = wiki_params[1]
    paragraph_xpath = wiki_params[2]
    save_button_xpath = wiki_params[3]

    if wiki_type is None:
        raise ValueError(f"Unknown wiki type for URL: {url}")

    driver.get(url)
    print('Выполнен переход на страницу')
    time.sleep(3)

    try:
        editable_element = driver.find_element(by=By.XPATH, value=editable_xpath)
        paragraph_element = editable_element.find_element(by=By.XPATH, value=paragraph_xpath)

        with open(filename, 'r', encoding='utf-8') as f:
            new_text = f.read()
        print(f"Текст получен в new_text")
        time.sleep(0.5)

        paragraph_element.send_keys(Keys.CONTROL + "a")
        time.sleep(0.5)
        paragraph_element.send_keys(Keys.DELETE)

        print("Очищено, приступаем писать текст")
        for line in new_text.splitlines():
            # Экранирование строки с помощью json.dumps
            escaped_line = json.dumps(line + "\n")
            script = f"arguments[0].value += {escaped_line};"
            driver.execute_script(script, paragraph_element)
            time.sleep(0.1)
        print("Написано")

        click_save_button_in_iframe(driver, save_button_xpath)

        time.sleep(1)

        print("Сохранено")
        log_link_to_file(url)

    except MaxRetryError as ex:
        print(f"MaxRetryError: {ex}")
    except Exception as ex:
        print(ex)


def write_template_data_to_file(url, file_path='templates_used.txt', json_file_path='wiki_data.json'):
    """
    Записывает данные о шаблонах на странице в указанный файл.
    """
    # Загружаем JSON данные из файла
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при загрузке JSON данных: {e}")
        return 0

    if json_data is None:
        raise ValueError("JSON data must be provided for the function to work.")

    # Определение типа вики и получение параметров
    wiki_params = determine_wiki_type_output(url, data, fields=[
        'wiki_type', 'div_class', 'template_keyword'
    ])

    if wiki_params is None:
        print(f"Не удалось определить параметры wiki для URL: {url}")
        return 0

    wiki_type = wiki_params[0]
    div_class = wiki_params[1]
    template_keyword = wiki_params[2]

    if wiki_type is None:
        print(f"Неизвестный тип вики для URL: {url}")
        return 0

    # Отправляем запрос к странице
    response = requests.get(url)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все теги <div class="templatesUsed">
        templates_used_divs = soup.find_all('div', {'class': div_class})

        # Проверяем, есть ли какие-либо теги
        if templates_used_divs:
            # Обрабатываем каждую вторую ссылку и записываем только те, которые содержат template_keyword
            links_count = 0
            with open(file_path, 'w', encoding='utf-8') as file:
                for div in templates_used_divs:
                    # Находим все ссылки внутри тега
                    links = div.find_all('a', href=True)

                    # Извлекаем и записываем каждую вторую ссылку на шаблон, содержащую template_keyword
                    for i in range(1, len(links), 2):
                        link_title = links[i]['title']
                        if template_keyword in link_title:
                            file.write(link_title + '\n')
                            links_count += 1

            print(f'Ссылки на шаблоны, содержащие "{template_keyword}", успешно записаны в файл {file_path}')
            print(f'Общее количество таких ссылок: {links_count}')

            # Возвращаем количество ссылок
            return links_count
        else:
            print(f'Теги <div class="{div_class}"> не найдены на странице')
            return 0
    else:
        print(f'Ошибка при запросе к странице. Код: {response.status_code}')
        return 'ERR520'


def get_specific_text(url, output_filename='filename.txt', json_data="wiki_data.json"):
    """
    Получает текст из указанного URL и сохраняет его в файл.
    """
    # Определение типа вики и получение параметров
    wiki_params = determine_wiki_type_output(url, json_data, fields=[
        'wiki_type', 'target_tag', 'target_class'
    ])

    wiki_type = wiki_params[0]
    target_tag = wiki_params[1]
    target_class = wiki_params[2]

    #wiki_type, target_tag, target_class = determine_wiki_type_output(url, json_data)

    if not wiki_type:
        print(f"Неизвестный тип вики для URL: {url}")
        return 'ERR520'

    # Отправляем GET-запрос
    response = requests.get(url)

    # Проверяем успешность запроса
    try:
        response.raise_for_status()
    except Exception:
        print(f"Ошибка 520 (в Copy.py: {traceback.extract_stack()[-2].lineno})")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(" ")
        return 'ERR520'

    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим конкретный тег с указанным классом
        target_element = soup.find(target_tag, class_=target_class)

        # Получаем текст из найденного элемента
        if target_element:
            text_content = target_element.get_text()

            # Сохраняем текст в файл
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)

            print(f"Текст сохранен в файл: {output_filename}")
        else:
            print(f"Элемент с тегом '{target_tag}' и классом '{target_class}' не найден.")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(" ")
    else:
        print(f"Ошибка {response.status_code}: Невозможно получить содержимое страницы.")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(" ")


def normalize_filename(filename):
    """Нормализует название файла, заменяя пробелы на подчеркивания и приводя к нижнему регистру."""
    return filename.replace(" ", "_").lower()


# Функция для получения списка файлов с расширениями .png и .gif, с проверкой на черный список
def get_image_files(text, blacklist):
    start_options = ["File:", "Файл:", "file:"]
    end_options = [".png", ".gif"]
    valid_files = []

    # Нормализуем черный список
    normalized_blacklist = {normalize_filename(entry.strip()) for entry in blacklist}

    for start in start_options:
        for end in end_options:
            pattern = rf'\b{start}(.+?){end}\b'
            matches = re.findall(pattern, text)

            for item in matches:
                filename = f"{item.strip()}{end}"
                decoded_filename = normalize_filename(urllib.parse.unquote(filename))

                # Проверяем, не входит ли нормализированное имя в черный список
                if decoded_filename not in normalized_blacklist:
                    valid_files.append(f"{start}{filename}")

    print("Файлы, не попавшие в черный список:", valid_files)
    return valid_files



# Функция для скачивания изображений
def download_images(file_names, folder_path, wiki_key):
    base_url = WIKI_BASE_URLS.get(wiki_key)
    if not base_url:
        print(f"Неизвестный ключ вики: {wiki_key}")
        return

    for file_name in file_names:
        url = f"{base_url}{file_name}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            image_divs = soup.find_all('div', class_='fullImageLink')
            found_image = False
            for image_div in image_divs:
                image_link = image_div.find('a', href=True)
                if image_link:
                    image_url = urljoin(url, image_link['href'])
                    if image_url.endswith(('.png', '.gif')):
                        found_image = True
                        os.makedirs(folder_path, exist_ok=True)

                        # Декодирование URL для получения корректного имени файла
                        decoded_filename = urllib.parse.unquote(os.path.basename(image_url))

                        # Проверка допустимости имени файла
                        sanitized_filename = "".join(
                            [c if c.isalnum() or c in (' ', '.', '_') else '_' for c in decoded_filename])

                        # Формирование полного пути для сохранения изображения
                        image_path = os.path.join(folder_path, sanitized_filename)

                        # Сохраняем изображение в папку
                        with open(image_path, 'wb') as f:
                            f.write(requests.get(image_url).content)
                            print(f"Изображение сохранено по пути: {image_path}")
                        break  # Прерываем цикл, если нашли изображение
            if not found_image:
                print(f"Не удалось найти изображение для {file_name}.")
        else:
            print(f"Не удалось загрузить страницу {url}.")


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
