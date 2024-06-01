import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}
proxies = {}

def write_data_to_file(url, file_path='templates_used.txt'):
    response = send_request(url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        templates_used_divs = soup.find_all('div', {'class': 'templatesUsed'})
        if templates_used_divs:
            links_count = 0
            with open(file_path, 'w', encoding='utf-8') as file:
                for div in templates_used_divs:
                    links = div.find_all('a', href=True)
                    for i in range(1, len(links), 2):
                        link_title = links[i]['title']
                        if 'Шаблон' in link_title:
                            file.write(link_title + '\n')
                            links_count += 1

            print(f'Ссылки на шаблоны, содержащие "Шаблон", успешно записаны в файл {file_path}')
            print(f'Общее количество таких ссылок: {links_count}')
            return links_count
        else:
            print('Теги <div class="templatesUsed"> не найдены на странице')
            return 0
    else:
        print('Ошибка при запросе к странице')
        return 'E520'

def get_specific_text(url, output_filename='filename.txt'):
    response = send_request(url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        target_tag = 'textarea'
        target_class = 'mw-editfont-monospace'
        target_element = soup.find(target_tag, class_=target_class)
        if target_element:
            text_content = target_element.get_text()
            save_to_file(text_content, output_filename)
        else:
            print(f"Элемент с тегом '{target_tag}' и классом '{target_class}' не найден.")
    else:
        print(f"Ошибка при запросе к странице {url}")

def send_request(url):
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Текст сохранен в файл: {filename}")
