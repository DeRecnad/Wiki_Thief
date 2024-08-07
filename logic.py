from Copy import get_specific_text, write_data_to_file
from Input import edit_and_save_text, login
from proxy_auth_data import username, password
from load_file import get_image_files, download_images, download_images_from_wiki
from upload_file import process_files_in_folder
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument("--headless=new")
    options.set_capability('pageLoadStrategy', "eager")
    return options


def process_links(link1, link2, driver):
    filename = 'filename.txt'

    print(f"Получаем текст с {link1}")
    if get_specific_text(link1) == 'ERR520':
        print(f"Не удалось получить текст с {link1}")
        return
    else:
        print("Текст получен")

    print(f"Начинаем вводить текст на {link2}")
    edit_and_save_text(link2, filename, driver)
    print("Ввод окончен")


def copy_and_update_links(link1, link2, driver):
    process_links(link1, link2, driver)

def check_count_links(link1, link2, setting_vars):
    # Опции браузера
    options = get_browser_options()
    service = Service(executable_path="chromedriver.exe")

    count_templates_links = write_data_to_file(link1)

    # Опции для файлов
    folder_path = r"D:\Programming\Wiki_Thief\downloaded_images_ss220"  # Путь к папке с изображениями
    base_upload_url = "http://aavikko.di9.ru/index.php?title=Служебная:Загрузка"  # Базовый URL для загрузки
    submit_button_name = "wpUpload"

    if setting_vars.use_templates:
        if count_templates_links == 'ERR520':
            print(f'Ошибка 520 (в logic.py: {traceback.extract_stack()[-2].lineno})')
        elif count_templates_links > 0:
            print(f'Были обнаружены шаблоны, проверка на шаблоны вернула: {count_templates_links}')
            main1_link = link1
            main2_link = link2
            with webdriver.Chrome(service=service, options=options) as driver:
                login(username, password, driver, link2)
                while count_templates_links != 0:
                    phrase = get_and_remove_last_link()

                    link1 = create_template_url(phrase, link1)
                    link2 = create_template_url(phrase, link2)

                    count_templates_links -= 1
                    process_links(link1, link2, driver)

                    download_images_from_wiki(link1, 'downloaded_images_ss220', 'ss220')
                    process_files_in_folder(folder_path, base_upload_url, submit_button_name, driver)

                process_links(main1_link, main2_link, driver)
        elif count_templates_links == 0:
            print(f'Шаблоны не обнаружены проверка на шаблоны вернула: {count_templates_links}')
            with webdriver.Chrome(service=service, options=options) as driver:
                login(username, password, driver, link2)
                copy_and_update_links(link1, link2, driver)
        else:
            print(f'Ошибка, проверка на шаблоны вернула: {count_templates_links}')
    elif not setting_vars.use_templates:
        print(f'Перенос без шаблонов')
        with webdriver.Chrome(service=service, options=options) as driver:
            login(username, password, driver)
            copy_and_update_links(link1, link2, driver)
    else:
        print(f'Неизвестная ошибка')


def get_and_remove_last_link(file_path='templates_used.txt'):
    try:
        # Читаем все строки из файла
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Проверяем, есть ли ссылки в файле
        if lines:
            # Извлекаем последнюю ссылку
            last_link = lines[-1].strip()

            # Перезаписываем файл без последней строки
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines[:-1])

            return last_link
        else:
            print(f'Файл {file_path} пуст. Нет ссылок для извлечения.')
            return None
    except Exception as e:
        print(f'Произошла ошибка при обработке файла: {e}')
        return None

def create_template_url(template_phrase, empty_url):
    """
    Заменяет '***' в URL на заданную фразу.

    :param template_phrase: Фраза для замены
    :param empty_url: URL с '***' в качестве значения параметра title
    :return: Новый URL с замененной фразой
    """
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    # Разбираем URL
    parsed_url = urlparse(empty_url)
    query_params = parse_qs(parsed_url.query)

    # Заменяем '***' на template_phrase
    query_params['title'] = [template_phrase]

    # Формируем новый URL с обновленными параметрами
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    print(f'создана новая ссылка {new_url}')

    return new_url

