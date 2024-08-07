import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin  # Импортируем функцию urljoin для объединения URL

# Определение вики
WIKI_BASE_URLS = {
    'station14': 'https://station14.ru/wiki/',
    'ss220': 'https://wiki14.ss220.club/index.php?title='
}

target_tag = 'textarea'
target_class = 'mw-editfont-monospace'

# Функция для получения списка файлов с расширениями .png и .gif
def get_image_files(text):
    start_options = ["File:", "Файл:"]
    end_options = [".png", ".gif"]
    files = []
    for start in start_options:
        for end in end_options:
            pattern = r'\b' + start + r'.*?' + end + r'\b'
            matches = re.findall(pattern, text)
            files.extend(matches)
    return files

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
            # Находим все теги <div> с классом 'fullImageLink'
            image_divs = soup.find_all('div', class_='fullImageLink')
            found_image = False
            for image_div in image_divs:
                # Находим ссылку на изображение внутри тега <a>
                image_link = image_div.find('a', href=True)
                if image_link:
                    image_url = urljoin(url, image_link['href'])
                    if image_url.endswith(('.png', '.gif')):  # Проверяем, является ли ссылка на изображение
                        found_image = True
                        # Создаем папку для сохранения изображений, если она не существует
                        os.makedirs(folder_path, exist_ok=True)
                        # Формируем полный путь для сохранения изображения
                        image_path = os.path.join(folder_path, os.path.basename(image_url))
                        # Сохраняем изображение в папку
                        with open(image_path, 'wb') as f:
                            f.write(requests.get(image_url).content)
                            print(f"Изображение сохранено по пути: {image_path}")
                        break  # Прерываем цикл, если нашли изображение
            if not found_image:
                print(f"Не удалось найти изображение для {file_name}.")
        else:
            print(f"Не удалось загрузить страницу {url}.")

# Функция для скачивания изображений из определенной вики
def download_images_from_wiki(url, folder_path, wiki_key):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        text_area = soup.find(target_tag, class_=target_class)
        if text_area:
            text = text_area.text
            # Получаем список файлов с расширениями .png и .gif
            image_files = get_image_files(text)
            # Скачиваем изображения
            download_images(image_files, folder_path, wiki_key)
        else:
            print("Не удалось найти текстовую область на странице.")
    else:
        print("Не удалось загрузить страницу.")

# Пример использования для station14
#url_station14 = 'https://station14.ru/index.php?title=%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:MainMenuLinks&action=edit'
#download_images_from_wiki(url_station14, 'downloaded_images_station14', 'station14')

# Пример использования для ss220
# url_ss220 = 'https://wiki14.ss220.club/index.php?title=%D0%A0%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D1%81%D1%82%D0%B2%D0%BE_%D0%BF%D0%BE_%D0%B2%D0%B7%D0%BB%D0%BE%D0%BC%D1%83&action=edit'
# download_images_from_wiki(url_ss220, 'downloaded_images_ss220', 'ss220')
