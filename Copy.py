import requests
from bs4 import BeautifulSoup
import traceback

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}
proxies = {}

def determine_wiki(url):
    if 'station14.ru' in url:
        return 'KORVAX'
    elif 'wiki14.ss220.club' in url:
        return 'SS220'
    else:
        return 'UNKNOWN'

def write_data_to_file(url, file_path='templates_used.txt'):
    wiki_type = determine_wiki(url)

    if wiki_type == 'KORVAX':
        div_class = 'templatesUsed'
        link_keyword = 'Шаблон'
    elif wiki_type == 'SS220':
        div_class = 'templatesUsed'  # Замените на правильный класс для SS220, если он отличается
        link_keyword = 'Шаблон'  # Замените на правильное ключевое слово для SS220, если оно отличается
    else:
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
            # Обрабатываем каждую вторую ссылку и записываем только те, которые содержат link_keyword
            links_count = 0
            with open(file_path, 'w', encoding='utf-8') as file:
                for div in templates_used_divs:
                    # Находим все ссылки внутри тега
                    links = div.find_all('a', href=True)

                    # Извлекаем и записываем каждую вторую ссылку на шаблон, содержащую link_keyword
                    for i in range(1, len(links), 2):
                        link_title = links[i]['title']
                        if link_keyword in link_title:
                            file.write(link_title + '\n')
                            links_count += 1

            print(f'Ссылки на шаблоны, содержащие "{link_keyword}", успешно записаны в файл {file_path}')
            print(f'Общее количество таких ссылок: {links_count}')

            # Возвращаем количество ссылок
            return links_count
        else:
            print(f'Теги <div class="{div_class}"> не найдены на странице')
            return 0
    else:
        print(f'Ошибка при запросе к странице. Код: {response.status_code}')
        return 'ERR520'

def get_specific_text(url, output_filename='filename.txt'):
    wiki_type = determine_wiki(url)

    if wiki_type == 'KORVAX':
        target_tag = 'textarea'
        target_class = 'mw-editfont-monospace'
    elif wiki_type == 'SS220':
        target_tag = 'textarea'  # тек текста
        target_class = 'mw-editfont-monospace'  # класс текста
    else:
        print(f"Неизвестный тип вики для URL: {url}")
        return 'ERR520'

    # Отправляем GET-запрос
    response = requests.get(url)

    # Проверяем успешность запроса
    try:
        response.raise_for_status()
    except Exception:
        print(f"Ошибка 520 (в Copy.py: {traceback.extract_stack()[-2].lineno})")
        return 'ERR520'

    # Проверяем успешность запроса
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
    else:
        # Если запрос не успешен, выводим сообщение об ошибке
        print(f"Ошибка {response.status_code}: Невозможно получить содержимое страницы.")

# Пример использования для вики КОРВАКС
# korvax_url = 'https://station14.ru/wiki/Some_Page'
# write_data_to_file(korvax_url)

# Пример использования для вики СС220
# ss220_url = 'https://wiki14.ss220.club/wiki/Some_Page'
# write_data_to_file(ss220_url, file_path='templates_used_ss220.txt')
