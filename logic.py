import traceback
import urllib.parse
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Copy import get_specific_text, write_data_to_file
from Input import edit_and_save_text, login, process_log_file_url
from proxy_auth_data import username, password
from load_file import get_image_files, download_images, download_images_from_wiki
from upload_file import upload_files_in_folder, process_log_file_files


def get_browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.set_capability('pageLoadStrategy', "eager")
    return options


def load_blacklist(blacklist_file):
    if os.path.exists(blacklist_file):
        with open(blacklist_file, 'r', encoding='utf-8') as file:
            blacklist = file.read().splitlines()
        print(f"Черный список {blacklist_file} загружен. Найдено {len(blacklist)} элементов.")
        return blacklist
    else:
        print(f"Файл черного списка {blacklist_file} не найден.")
        return []


def is_in_blacklist(item, blacklist):
    print(f"Проверка на ЧС: {item}")
    decoded_item = urllib.parse.unquote(item)  # Декодируем имя файла
    print(f"  Декодировка: {decoded_item}")
    is_blacklisted = item in blacklist or decoded_item in blacklist
    print(f"  Результат проверки: {'в черном списке' if is_blacklisted else 'не в черном списке'}")
    return is_blacklisted


def process_files(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files):
    output_filename = 'filename.txt'
    get_specific_text(link1, output_filename)

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

    all_files = get_image_files(page_text)
    #files_to_download = [file for file in all_files if not is_in_blacklist(file, blacklist_files)]

    download_images(all_files, folder_path, 'ss220')

    for filename in os.listdir(folder_path):
        if is_in_blacklist(filename, blacklist_files):
            print(f"Файл {filename} находится в черном списке. Пропускаем и удаляем...")
            os.remove(os.path.join(folder_path, filename))

    upload_files_in_folder(folder_path, base_upload_url, submit_button_name, driver)


def process_links(link1, link2, driver, blacklist_links):
    # Проверяем, находится ли link1 в черном списке
    if is_in_blacklist(link1, blacklist_links):
        return 0

    # Проверяем, находится ли link2 в черном списке
    if is_in_blacklist(link2, blacklist_links):
        return 0

    filename = 'filename.txt'

    print(f"Получаем текст с {link1}")
    if get_specific_text(link1) == 'ERR520':
        print(f"Не удалось получить текст с {link1}")
        return 0
    else:
        print("Текст получен")

    print(f"Начинаем вводить текст на {link2}")
    edit_and_save_text(link2, filename, driver)
    print("Ввод окончен")
    return 1


def check_count_links(link1, link2, setting_vars):
    check = 1

    options = get_browser_options()
    service = Service(executable_path="chromedriver.exe")

    count_templates_links = write_data_to_file(link1)

    folder_path = r"D:\Programming\Wiki_Thief\downloaded_images_ss220"
    base_upload_url = "http://aavikko.di9.ru/index.php?title=Служебная:Загрузка"
    submit_button_name = "wpUpload"

    blacklist_links = load_blacklist('blacklist_links.txt')
    blacklist_files = load_blacklist('blacklist_files.txt')

    driver = webdriver.Chrome(service=service, options=options)
    login(username, password, driver, link2)  # Вход выполняется один раз

    try:
        if setting_vars.use_templates:
            if count_templates_links == 'ERR520':
                print(f'Ошибка 520 (в logic.py: {traceback.extract_stack()[-2].lineno})')
            elif count_templates_links > 0:
                print(f'Были обнаружены шаблоны, проверка на шаблоны вернула: {count_templates_links}')
                main1_link = link1
                main2_link = link2
                while count_templates_links != 0:
                    check = 1
                    phrase = get_and_remove_last_link()

                    link1 = create_template_url(phrase, link1)
                    link2 = create_template_url(phrase, link2)

                    count_templates_links -= 1
                    check = process_links(link1, link2, driver, blacklist_links)
                    if check != 0:
                        process_files(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)

                process_links(main1_link, main2_link, driver, blacklist_links)
                process_files(main1_link, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)
            elif count_templates_links == 0:
                print(f'Шаблоны не обнаружены, проверка на шаблоны вернула: {count_templates_links}')
                process_links(link1, link2, driver, blacklist_links)
                process_files(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)
        else:
            print(f'Перенос без шаблонов')
            process_links(link1, link2, driver, blacklist_links)
            process_files(link1, folder_path, base_upload_url, submit_button_name, driver, blacklist_files)
    finally:
        process_log_file_files()
        process_log_file_url()
        print(f'Программа ?успешно? завершила свою работу')
        driver.quit()


def get_and_remove_last_link(file_path='templates_used.txt'):
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


def create_template_url(template_phrase, empty_url):
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed_url = urlparse(empty_url)
    query_params = parse_qs(parsed_url.query)

    query_params['title'] = [template_phrase]

    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))

    decoded_url = urllib.parse.unquote(new_url)
    print(f'Создана новая ссылка {decoded_url}')

    return new_url
